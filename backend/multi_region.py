"""
Multi-Region Deployment Configuration
Geo-redundancy and failover management
"""
import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RegionStatus(str, Enum):
    """Region health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"

@dataclass
class Region:
    """Region configuration"""
    name: str
    code: str
    endpoint: str
    priority: int
    status: RegionStatus = RegionStatus.HEALTHY
    latency_ms: float = 0.0
    capacity_percent: float = 100.0

class MultiRegionManager:
    """
    Manages multi-region deployment and failover
    """
    
    def __init__(self):
        self.primary_region = os.getenv("PRIMARY_REGION", "eu-west-1")
        self.current_region = os.getenv("CURRENT_REGION", "eu-west-1")
        
        # Define available regions
        self.regions: Dict[str, Region] = {
            "eu-west-1": Region(
                name="Europe (Ireland)",
                code="eu-west-1",
                endpoint="https://eu-west-1.api.omaya-monitoring.com",
                priority=1
            ),
            "us-east-1": Region(
                name="US East (N. Virginia)",
                code="us-east-1",
                endpoint="https://us-east-1.api.omaya-monitoring.com",
                priority=2
            ),
            "ap-northeast-1": Region(
                name="Asia Pacific (Tokyo)",
                code="ap-northeast-1",
                endpoint="https://ap-northeast-1.api.omaya-monitoring.com",
                priority=3
            ),
            "us-west-2": Region(
                name="US West (Oregon)",
                code="us-west-2",
                endpoint="https://us-west-2.api.omaya-monitoring.com",
                priority=4
            )
        }
    
    def get_region(self, region_code: str) -> Optional[Region]:
        """Get region by code"""
        return self.regions.get(region_code)
    
    def get_healthy_regions(self) -> List[Region]:
        """Get list of healthy regions sorted by priority"""
        healthy = [
            r for r in self.regions.values()
            if r.status == RegionStatus.HEALTHY
        ]
        return sorted(healthy, key=lambda x: x.priority)
    
    def get_failover_region(self) -> Optional[Region]:
        """Get the best failover region"""
        healthy = self.get_healthy_regions()
        
        # Return first healthy region that's not current
        for region in healthy:
            if region.code != self.current_region:
                return region
        
        return None
    
    def update_region_status(
        self, 
        region_code: str, 
        status: RegionStatus,
        latency_ms: Optional[float] = None,
        capacity_percent: Optional[float] = None
    ):
        """
        Update region health status
        
        Args:
            region_code: Region code
            status: New status
            latency_ms: Optional latency measurement
            capacity_percent: Optional capacity percentage
        """
        if region_code in self.regions:
            self.regions[region_code].status = status
            
            if latency_ms is not None:
                self.regions[region_code].latency_ms = latency_ms
            
            if capacity_percent is not None:
                self.regions[region_code].capacity_percent = capacity_percent
            
            logger.info(f"Region {region_code} status updated: {status}")
    
    def should_failover(self) -> bool:
        """Check if failover should be triggered"""
        current = self.regions.get(self.current_region)
        
        if not current:
            return True
        
        return current.status in [RegionStatus.UNHEALTHY, RegionStatus.MAINTENANCE]
    
    def get_dns_config(self) -> Dict:
        """
        Generate DNS configuration for multi-region setup
        (Route53, Cloudflare, etc.)
        
        Returns:
            DNS configuration dict
        """
        records = []
        
        for region in self.get_healthy_regions():
            records.append({
                "name": "api.omaya-monitoring.com",
                "type": "A",
                "routing_policy": "geolocation",
                "region": region.code,
                "endpoint": region.endpoint,
                "health_check": {
                    "path": "/health",
                    "interval": 30,
                    "threshold": 3
                },
                "failover_priority": region.priority
            })
        
        return {
            "hosted_zone": "omaya-monitoring.com",
            "records": records,
            "failover_config": {
                "enabled": True,
                "health_check_interval": 30,
                "failover_threshold": 3
            }
        }
    
    def get_replication_config(self) -> Dict:
        """
        Generate database replication configuration
        
        Returns:
            Replication configuration dict
        """
        return {
            "primary": {
                "region": self.primary_region,
                "endpoint": f"db.{self.primary_region}.omaya-monitoring.com",
                "mode": "read-write"
            },
            "replicas": [
                {
                    "region": region.code,
                    "endpoint": f"db.{region.code}.omaya-monitoring.com",
                    "mode": "read-only",
                    "replication_lag_threshold_ms": 1000
                }
                for region in self.regions.values()
                if region.code != self.primary_region
            ],
            "sync_mode": "async",
            "conflict_resolution": "last-write-wins"
        }
    
    def get_kubernetes_config(self) -> Dict:
        """
        Generate Kubernetes federation configuration
        
        Returns:
            K8s federation config dict
        """
        return {
            "apiVersion": "types.kubefed.io/v1beta1",
            "kind": "FederatedDeployment",
            "metadata": {
                "name": "omaya-api",
                "namespace": "omaya-monitoring"
            },
            "spec": {
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "omaya-api"
                        }
                    },
                    "spec": {
                        "replicas": 3,
                        "selector": {
                            "matchLabels": {
                                "app": "omaya-api"
                            }
                        }
                    }
                },
                "placement": {
                    "clusters": [
                        {"name": f"cluster-{region.code}"}
                        for region in self.regions.values()
                    ]
                },
                "overrides": [
                    {
                        "clusterName": f"cluster-{region.code}",
                        "clusterOverrides": [
                            {
                                "path": "/spec/replicas",
                                "value": 3 if region.priority <= 2 else 2
                            }
                        ]
                    }
                    for region in self.regions.values()
                ]
            }
        }
    
    def get_traffic_routing(self) -> Dict:
        """
        Get traffic routing weights for each region
        
        Returns:
            Traffic routing configuration
        """
        healthy_regions = self.get_healthy_regions()
        
        if not healthy_regions:
            return {"error": "No healthy regions available"}
        
        # Calculate weights based on priority and capacity
        total_weight = sum(
            (1 / r.priority) * (r.capacity_percent / 100)
            for r in healthy_regions
        )
        
        routing = {}
        for region in healthy_regions:
            weight = ((1 / region.priority) * (region.capacity_percent / 100)) / total_weight
            routing[region.code] = {
                "weight": round(weight * 100, 1),
                "endpoint": region.endpoint,
                "latency_ms": region.latency_ms
            }
        
        return routing
    
    def get_status_report(self) -> Dict:
        """
        Get comprehensive status report for all regions
        
        Returns:
            Status report dict
        """
        return {
            "current_region": self.current_region,
            "primary_region": self.primary_region,
            "should_failover": self.should_failover(),
            "failover_target": self.get_failover_region().code if self.get_failover_region() else None,
            "regions": {
                code: {
                    "name": region.name,
                    "status": region.status.value,
                    "priority": region.priority,
                    "latency_ms": region.latency_ms,
                    "capacity_percent": region.capacity_percent,
                    "endpoint": region.endpoint
                }
                for code, region in self.regions.items()
            },
            "traffic_routing": self.get_traffic_routing(),
            "healthy_count": len(self.get_healthy_regions()),
            "total_count": len(self.regions)
        }

# Singleton instance
multi_region = MultiRegionManager()
