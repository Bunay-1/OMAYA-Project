"""
Service Mesh Configuration
Istio/Linkerd integration for microservices
"""
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ServiceMeshConfig:
    """
    Configuration for service mesh integration
    Supports Istio and Linkerd
    """
    
    def __init__(self):
        self.mesh_type = os.getenv("SERVICE_MESH", "istio")  # istio or linkerd
        self.namespace = os.getenv("K8S_NAMESPACE", "omaya-monitoring")
        self.mtls_enabled = os.getenv("MTLS_ENABLED", "true").lower() == "true"
    
    def get_istio_virtual_service(self, service_name: str, host: str) -> Dict:
        """
        Generate Istio VirtualService configuration
        
        Args:
            service_name: Name of the service
            host: Host for the service
            
        Returns:
            VirtualService YAML as dict
        """
        return {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "VirtualService",
            "metadata": {
                "name": service_name,
                "namespace": self.namespace
            },
            "spec": {
                "hosts": [host],
                "gateways": [f"{service_name}-gateway"],
                "http": [
                    {
                        "match": [
                            {"uri": {"prefix": "/api"}}
                        ],
                        "route": [
                            {
                                "destination": {
                                    "host": service_name,
                                    "port": {"number": 8000}
                                },
                                "weight": 100
                            }
                        ],
                        "timeout": "30s",
                        "retries": {
                            "attempts": 3,
                            "perTryTimeout": "10s",
                            "retryOn": "gateway-error,connect-failure,refused-stream"
                        }
                    }
                ]
            }
        }
    
    def get_istio_destination_rule(self, service_name: str) -> Dict:
        """
        Generate Istio DestinationRule configuration
        
        Args:
            service_name: Name of the service
            
        Returns:
            DestinationRule YAML as dict
        """
        return {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "DestinationRule",
            "metadata": {
                "name": service_name,
                "namespace": self.namespace
            },
            "spec": {
                "host": service_name,
                "trafficPolicy": {
                    "connectionPool": {
                        "tcp": {
                            "maxConnections": 100
                        },
                        "http": {
                            "h2UpgradePolicy": "UPGRADE",
                            "http1MaxPendingRequests": 100,
                            "http2MaxRequests": 1000
                        }
                    },
                    "loadBalancer": {
                        "simple": "ROUND_ROBIN"
                    },
                    "outlierDetection": {
                        "consecutive5xxErrors": 5,
                        "interval": "30s",
                        "baseEjectionTime": "30s",
                        "maxEjectionPercent": 50
                    },
                    "tls": {
                        "mode": "ISTIO_MUTUAL" if self.mtls_enabled else "DISABLE"
                    }
                }
            }
        }
    
    def get_istio_gateway(self, service_name: str, hosts: list) -> Dict:
        """
        Generate Istio Gateway configuration
        
        Args:
            service_name: Name of the service
            hosts: List of hosts
            
        Returns:
            Gateway YAML as dict
        """
        return {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "Gateway",
            "metadata": {
                "name": f"{service_name}-gateway",
                "namespace": self.namespace
            },
            "spec": {
                "selector": {
                    "istio": "ingressgateway"
                },
                "servers": [
                    {
                        "port": {
                            "number": 443,
                            "name": "https",
                            "protocol": "HTTPS"
                        },
                        "tls": {
                            "mode": "SIMPLE",
                            "credentialName": f"{service_name}-tls"
                        },
                        "hosts": hosts
                    },
                    {
                        "port": {
                            "number": 80,
                            "name": "http",
                            "protocol": "HTTP"
                        },
                        "hosts": hosts,
                        "tls": {
                            "httpsRedirect": True
                        }
                    }
                ]
            }
        }
    
    def get_peer_authentication(self) -> Dict:
        """
        Generate PeerAuthentication for mTLS
        
        Returns:
            PeerAuthentication YAML as dict
        """
        return {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "PeerAuthentication",
            "metadata": {
                "name": "default",
                "namespace": self.namespace
            },
            "spec": {
                "mtls": {
                    "mode": "STRICT" if self.mtls_enabled else "PERMISSIVE"
                }
            }
        }
    
    def get_authorization_policy(self, service_name: str, allowed_principals: list) -> Dict:
        """
        Generate AuthorizationPolicy for service
        
        Args:
            service_name: Name of the service
            allowed_principals: List of allowed service accounts
            
        Returns:
            AuthorizationPolicy YAML as dict
        """
        return {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "AuthorizationPolicy",
            "metadata": {
                "name": f"{service_name}-policy",
                "namespace": self.namespace
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": service_name
                    }
                },
                "action": "ALLOW",
                "rules": [
                    {
                        "from": [
                            {
                                "source": {
                                    "principals": allowed_principals
                                }
                            }
                        ],
                        "to": [
                            {
                                "operation": {
                                    "methods": ["GET", "POST", "PUT", "DELETE"]
                                }
                            }
                        ]
                    }
                ]
            }
        }
    
    def get_linkerd_service_profile(self, service_name: str) -> Dict:
        """
        Generate Linkerd ServiceProfile configuration
        
        Args:
            service_name: Name of the service
            
        Returns:
            ServiceProfile YAML as dict
        """
        return {
            "apiVersion": "linkerd.io/v1alpha2",
            "kind": "ServiceProfile",
            "metadata": {
                "name": f"{service_name}.{self.namespace}.svc.cluster.local",
                "namespace": self.namespace
            },
            "spec": {
                "routes": [
                    {
                        "name": "GET /api/machines",
                        "condition": {
                            "method": "GET",
                            "pathRegex": "/api/machines.*"
                        },
                        "responseClasses": [
                            {
                                "condition": {
                                    "status": {
                                        "min": 500,
                                        "max": 599
                                    }
                                },
                                "isFailure": True
                            }
                        ]
                    },
                    {
                        "name": "POST /api/predict",
                        "condition": {
                            "method": "POST",
                            "pathRegex": "/api/predict.*"
                        },
                        "timeout": "30s"
                    }
                ],
                "retryBudget": {
                    "retryRatio": 0.2,
                    "minRetriesPerSecond": 10,
                    "ttl": "10s"
                }
            }
        }
    
    def generate_all_configs(self, service_name: str = "omaya-api", host: str = "api.omaya-monitoring.com") -> Dict:
        """
        Generate all service mesh configurations
        
        Args:
            service_name: Name of the service
            host: Host for the service
            
        Returns:
            Dict with all configurations
        """
        configs = {}
        
        if self.mesh_type == "istio":
            configs["gateway"] = self.get_istio_gateway(service_name, [host])
            configs["virtual_service"] = self.get_istio_virtual_service(service_name, host)
            configs["destination_rule"] = self.get_istio_destination_rule(service_name)
            configs["peer_authentication"] = self.get_peer_authentication()
            configs["authorization_policy"] = self.get_authorization_policy(
                service_name,
                [f"cluster.local/ns/{self.namespace}/sa/omaya-api"]
            )
        elif self.mesh_type == "linkerd":
            configs["service_profile"] = self.get_linkerd_service_profile(service_name)
        
        return configs

# Singleton instance
service_mesh = ServiceMeshConfig()
