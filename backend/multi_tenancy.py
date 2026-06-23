"""
Multi-tenancy Module for OMAYA Platform
Support for multiple organizations with isolated data and resources
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
import secrets
import hashlib
from enum import Enum

logger = logging.getLogger(__name__)


class TenantStatus(Enum):
    """Tenant status enumeration."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"
    TRIAL = "trial"


class TenantTier(Enum):
    """Tenant tier enumeration."""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


@dataclass
class TenantConfig:
    """Tenant configuration."""
    tenant_id: str
    name: str
    status: TenantStatus
    tier: TenantTier
    max_machines: int
    max_users: int
    storage_quota_gb: int
    api_rate_limit: int
    features: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class TenantManager:
    """Multi-tenant management system."""
    
    def __init__(self):
        """Initialize tenant manager."""
        self.tenants: Dict[str, TenantConfig] = {}
        self.tenant_databases: Dict[str, str] = {}  # tenant_id -> database_name
        self.tenant_api_keys: Dict[str, List[str]] = {}  # tenant_id -> api_keys
    
    def create_tenant(self, name: str, tier: TenantTier = TenantTier.BASIC,
                     trial_days: int = 30) -> TenantConfig:
        """
        Create a new tenant.
        
        Args:
            name: Tenant name
            tier: Tenant tier
            trial_days: Trial period in days
            
        Returns:
            TenantConfig
        """
        tenant_id = self._generate_tenant_id(name)
        
        # Get tier configuration
        tier_config = self._get_tier_config(tier)
        
        # Set expiration for trial
        expires_at = None
        if tier == TenantTier.TRIAL:
            expires_at = datetime.now() + timedelta(days=trial_days)
        
        tenant = TenantConfig(
            tenant_id=tenant_id,
            name=name,
            status=TenantStatus.ACTIVE,
            tier=tier,
            max_machines=tier_config['max_machines'],
            max_users=tier_config['max_users'],
            storage_quota_gb=tier_config['storage_quota_gb'],
            api_rate_limit=tier_config['api_rate_limit'],
            features=tier_config['features'],
            created_at=datetime.now(),
            expires_at=expires_at,
            metadata={}
        )
        
        self.tenants[tenant_id] = tenant
        self.tenant_databases[tenant_id] = f"omaya_{tenant_id}"
        self.tenant_api_keys[tenant_id] = [self._generate_api_key()]
        
        logger.info(f"Created tenant {tenant_id} ({name}) with tier {tier.value}")
        
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[TenantConfig]:
        """
        Get tenant by ID.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            TenantConfig or None
        """
        return self.tenants.get(tenant_id)
    
    def update_tenant(self, tenant_id: str, **kwargs) -> bool:
        """
        Update tenant configuration.
        
        Args:
            tenant_id: Tenant ID
            **kwargs: Fields to update
            
        Returns:
            True on success, False on error
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        for key, value in kwargs.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)
        
        logger.info(f"Updated tenant {tenant_id}")
        return True
    
    def suspend_tenant(self, tenant_id: str, reason: str = "") -> bool:
        """
        Suspend tenant.
        
        Args:
            tenant_id: Tenant ID
            reason: Suspension reason
            
        Returns:
            True on success, False on error
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.status = TenantStatus.SUSPENDED
        if reason:
            tenant.metadata = tenant.metadata or {}
            tenant.metadata['suspension_reason'] = reason
        
        logger.info(f"Suspended tenant {tenant_id}: {reason}")
        return True
    
    def activate_tenant(self, tenant_id: str) -> bool:
        """
        Activate tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            True on success, False on error
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.status = TenantStatus.ACTIVE
        if tenant.metadata and 'suspension_reason' in tenant.metadata:
            del tenant.metadata['suspension_reason']
        
        logger.info(f"Activated tenant {tenant_id}")
        return True
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """
        Delete tenant (soft delete).
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            True on success, False on error
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.status = TenantStatus.DELETED
        logger.info(f"Deleted tenant {tenant_id}")
        return True
    
    def upgrade_tier(self, tenant_id: str, new_tier: TenantTier) -> bool:
        """
        Upgrade tenant tier.
        
        Args:
            tenant_id: Tenant ID
            new_tier: New tier
            
        Returns:
            True on success, False on error
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        tier_config = self._get_tier_config(new_tier)
        tenant.tier = new_tier
        tenant.max_machines = tier_config['max_machines']
        tenant.max_users = tier_config['max_users']
        tenant.storage_quota_gb = tier_config['storage_quota_gb']
        tenant.api_rate_limit = tier_config['api_rate_limit']
        tenant.features = tier_config['features']
        
        logger.info(f"Upgraded tenant {tenant_id} to {new_tier.value}")
        return True
    
    def generate_api_key(self, tenant_id: str) -> str:
        """
        Generate new API key for tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            API key
        """
        if tenant_id not in self.tenant_api_keys:
            self.tenant_api_keys[tenant_id] = []
        
        api_key = self._generate_api_key()
        self.tenant_api_keys[tenant_id].append(api_key)
        
        logger.info(f"Generated API key for tenant {tenant_id}")
        return api_key
    
    def revoke_api_key(self, tenant_id: str, api_key: str) -> bool:
        """
        Revoke API key.
        
        Args:
            tenant_id: Tenant ID
            api_key: API key to revoke
            
        Returns:
            True on success, False on error
        """
        if tenant_id not in self.tenant_api_keys:
            return False
        
        if api_key in self.tenant_api_keys[tenant_id]:
            self.tenant_api_keys[tenant_id].remove(api_key)
            logger.info(f"Revoked API key for tenant {tenant_id}")
            return True
        
        return False
    
    def validate_api_key(self, api_key: str) -> Optional[str]:
        """
        Validate API key and return tenant ID.
        
        Args:
            api_key: API key to validate
            
        Returns:
            Tenant ID or None
        """
        for tenant_id, keys in self.tenant_api_keys.items():
            if api_key in keys:
                tenant = self.tenants.get(tenant_id)
                if tenant and tenant.status == TenantStatus.ACTIVE:
                    return tenant_id
        return None
    
    def check_tenant_limits(self, tenant_id: str, resource_type: str,
                           current_count: int) -> bool:
        """
        Check if tenant has exceeded resource limits.
        
        Args:
            tenant_id: Tenant ID
            resource_type: Type of resource (machines, users, storage)
            current_count: Current count
            
        Returns:
            True if within limits, False otherwise
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant or tenant.status != TenantStatus.ACTIVE:
            return False
        
        if resource_type == 'machines':
            return current_count < tenant.max_machines
        elif resource_type == 'users':
            return current_count < tenant.max_users
        elif resource_type == 'storage':
            return current_count < tenant.storage_quota_gb
        
        return True
    
    def get_tenant_usage(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get tenant resource usage statistics.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Usage statistics
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return {}
        
        # In a real implementation, this would query actual usage
        # For now, return mock data
        return {
            'tenant_id': tenant_id,
            'machines_used': 0,
            'machines_limit': tenant.max_machines,
            'users_used': 0,
            'users_limit': tenant.max_users,
            'storage_used_gb': 0,
            'storage_limit_gb': tenant.storage_quota_gb,
            'api_calls_today': 0,
            'api_rate_limit': tenant.api_rate_limit
        }
    
    def list_tenants(self, status: Optional[TenantStatus] = None) -> List[TenantConfig]:
        """
        List tenants, optionally filtered by status.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of tenants
        """
        tenants = list(self.tenants.values())
        
        if status:
            tenants = [t for t in tenants if t.status == status]
        
        return tenants
    
    def _generate_tenant_id(self, name: str) -> str:
        """Generate unique tenant ID."""
        # Normalize name
        normalized = name.lower().replace(' ', '-').replace('_', '-')
        # Add random suffix
        suffix = secrets.token_hex(4)
        return f"{normalized}-{suffix}"
    
    def _generate_api_key(self) -> str:
        """Generate secure API key."""
        prefix = "omaya_"
        key = secrets.token_urlsafe(32)
        return f"{prefix}{key}"
    
    def _get_tier_config(self, tier: TenantTier) -> Dict[str, Any]:
        """Get configuration for a tier."""
        configs = {
            TenantTier.BASIC: {
                'max_machines': 10,
                'max_users': 5,
                'storage_quota_gb': 10,
                'api_rate_limit': 1000,
                'features': ['basic_dashboard', 'real_time_monitoring']
            },
            TenantTier.PROFESSIONAL: {
                'max_machines': 50,
                'max_users': 20,
                'storage_quota_gb': 100,
                'api_rate_limit': 10000,
                'features': [
                    'basic_dashboard',
                    'real_time_monitoring',
                    'predictive_maintenance',
                    'custom_reports',
                    'api_access'
                ]
            },
            TenantTier.ENTERPRISE: {
                'max_machines': 500,
                'max_users': 100,
                'storage_quota_gb': 1000,
                'api_rate_limit': 100000,
                'features': [
                    'basic_dashboard',
                    'real_time_monitoring',
                    'predictive_maintenance',
                    'custom_reports',
                    'api_access',
                    'multi_region',
                    'advanced_analytics',
                    'white_label',
                    'dedicated_support'
                ]
            },
            TenantTier.TRIAL: {
                'max_machines': 5,
                'max_users': 2,
                'storage_quota_gb': 5,
                'api_rate_limit': 500,
                'features': ['basic_dashboard', 'real_time_monitoring']
            },
            TenantTier.CUSTOM: {
                'max_machines': 1000,
                'max_users': 500,
                'storage_quota_gb': 10000,
                'api_rate_limit': 1000000,
                'features': ['all']
            }
        }
        
        return configs.get(tier, configs[TenantTier.BASIC])


class TenantIsolationMiddleware:
    """Middleware for tenant isolation."""
    
    def __init__(self, tenant_manager: TenantManager):
        """
        Initialize middleware.
        
        Args:
            tenant_manager: Tenant manager instance
        """
        self.tenant_manager = tenant_manager
    
    def extract_tenant(self, request: Dict[str, Any]) -> Optional[str]:
        """
        Extract tenant ID from request.
        
        Args:
            request: Request dictionary
            
        Returns:
            Tenant ID or None
        """
        # Try API key
        api_key = request.get('headers', {}).get('X-API-Key')
        if api_key:
            tenant_id = self.tenant_manager.validate_api_key(api_key)
            if tenant_id:
                return tenant_id
        
        # Try JWT token
        auth_header = request.get('headers', {}).get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            # In real implementation, decode JWT and extract tenant_id
            # For now, return None
            pass
        
        # Try subdomain
        host = request.get('headers', {}).get('Host', '')
        if '.' in host:
            subdomain = host.split('.')[0]
            tenant = self.tenant_manager.get_tenant(subdomain)
            if tenant:
                return tenant.tenant_id
        
        return None
    
    def add_tenant_context(self, request: Dict[str, Any], 
                          tenant_id: str) -> Dict[str, Any]:
        """
        Add tenant context to request.
        
        Args:
            request: Original request
            tenant_id: Tenant ID
            
        Returns:
            Request with tenant context
        """
        request['tenant_id'] = tenant_id
        request['tenant'] = self.tenant_manager.get_tenant(tenant_id)
        return request
    
    def check_tenant_status(self, tenant_id: str) -> bool:
        """
        Check if tenant is active.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            True if active, False otherwise
        """
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            return False
        
        if tenant.status != TenantStatus.ACTIVE:
            return False
        
        # Check expiration
        if tenant.expires_at and datetime.now() > tenant.expires_at:
            return False
        
        return True


class TenantBilling:
    """Tenant billing management."""
    
    def __init__(self, tenant_manager: TenantManager):
        """
        Initialise billing.
        
        Args:
            tenant_manager: Tenant manager instance
        """
        self.tenant_manager = tenant_manager
        self.billing_records: Dict[str, List[Dict[str, Any]]] = {}
    
    def create_invoice(self, tenant_id: str, amount: float, 
                      description: str) -> str:
        """
        Create invoice for tenant.
        
        Args:
            tenant_id: Tenant ID
            amount: Invoice amount
            description: Invoice description
            
        Returns:
            Invoice ID
        """
        invoice_id = f"INV-{secrets.token_hex(8).upper()}"
        
        invoice = {
            'invoice_id': invoice_id,
            'tenant_id': tenant_id,
            'amount': amount,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            'due_date': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        if tenant_id not in self.billing_records:
            self.billing_records[tenant_id] = []
        
        self.billing_records[tenant_id].append(invoice)
        
        logger.info(f"Created invoice {invoice_id} for tenant {tenant_id}")
        return invoice_id
    
    def get_invoices(self, tenant_id: str) -> List[Dict[str, Any]]:
        """
        Get invoices for tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            List of invoices
        """
        return self.billing_records.get(tenant_id, [])
    
    def calculate_monthly_cost(self, tenant_id: str) -> float:
        """
        Calculate monthly cost for tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Monthly cost
        """
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            return 0.0
        
        # Base pricing
        tier_pricing = {
            TenantTier.BASIC: 99,
            TenantTier.PROFESSIONAL: 499,
            TenantTier.ENTERPRISE: 1999,
            TenantTier.TRIAL: 0,
            TenantTier.CUSTOM: 0  # Custom pricing
        }
        
        base_cost = tier_pricing.get(tenant.tier, 0)
        
        # Add usage-based costs
        usage = self.tenant_manager.get_tenant_usage(tenant_id)
        
        # Machine overage
        machines_overage = max(0, usage['machines_used'] - tenant.max_machines)
        machine_cost = machines_overage * 20
        
        # Storage overage
        storage_overage = max(0, usage['storage_used_gb'] - tenant.storage_quota_gb)
        storage_cost = storage_overage * 2
        
        total_cost = base_cost + machine_cost + storage_cost
        
        return total_cost
