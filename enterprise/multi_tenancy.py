#!/usr/bin/env python3
"""
Multi-Tenancy and Enterprise Features for ReliQuary Platform
Advanced tenant isolation, resource management, and enterprise capabilities
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

import redis
from cryptography.fernet import Fernet


class TenantTier(Enum):
    """Tenant subscription tiers"""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    ENTERPRISE_PLUS = "enterprise_plus"


class ResourceQuotaType(Enum):
    """Types of resource quotas"""
    API_REQUESTS_PER_HOUR = "api_requests_per_hour"
    STORAGE_GB = "storage_gb"
    CONCURRENT_USERS = "concurrent_users"
    CONSENSUS_OPERATIONS = "consensus_operations_per_hour"
    CRYPTO_OPERATIONS = "crypto_operations_per_hour"
    VAULT_COUNT = "vault_count"
    AGENT_COUNT = "agent_count"


@dataclass
class TenantConfig:
    """Tenant configuration settings"""
    tenant_id: str
    name: str
    tier: TenantTier
    created_at: datetime
    is_active: bool
    settings: Dict[str, Any]
    resource_quotas: Dict[ResourceQuotaType, int]
    feature_flags: Dict[str, bool]
    custom_domains: List[str]
    sso_config: Optional[Dict[str, Any]] = None
    compliance_settings: Optional[Dict[str, Any]] = None


@dataclass
class ResourceUsage:
    """Resource usage tracking"""
    tenant_id: str
    resource_type: ResourceQuotaType
    current_usage: int
    quota_limit: int
    reset_period: str
    last_reset: datetime


Base = declarative_base()


class Tenant(Base):
    """Tenant database model"""
    __tablename__ = 'tenants'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    tier = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default={})
    resource_quotas = Column(JSON, default={})
    feature_flags = Column(JSON, default={})
    custom_domains = Column(JSON, default=[])
    sso_config = Column(JSON)
    compliance_settings = Column(JSON)
    
    # Relationships
    users = relationship("TenantUser", back_populates="tenant")
    vaults = relationship("TenantVault", back_populates="tenant")
    usage_records = relationship("TenantUsage", back_populates="tenant")


class TenantUser(Base):
    """Tenant user mapping"""
    __tablename__ = 'tenant_users'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
    user_id = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, user, viewer
    permissions = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    tenant = relationship("Tenant", back_populates="users")


class TenantVault(Base):
    """Tenant vault mapping"""
    __tablename__ = 'tenant_vaults'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
    vault_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    encryption_key = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, default={})
    
    tenant = relationship("Tenant", back_populates="vaults")


class TenantUsage(Base):
    """Tenant resource usage tracking"""
    __tablename__ = 'tenant_usage'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
    resource_type = Column(String, nullable=False)
    usage_count = Column(Integer, default=0)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="usage_records")


class MultiTenancyManager:
    """Multi-tenancy management system"""
    
    def __init__(self, database_url: str, redis_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        self.redis_client = redis.from_url(redis_url)
        self.logger = logging.getLogger("multi_tenancy")
        
        # Tier configurations
        self.tier_configs = self._initialize_tier_configs()
        
        # Encryption for tenant data
        self.fernet = Fernet(Fernet.generate_key())
    
    def _initialize_tier_configs(self) -> Dict[TenantTier, Dict[str, Any]]:
        """Initialize tier-based configurations"""
        
        return {
            TenantTier.STARTER: {
                "resource_quotas": {
                    ResourceQuotaType.API_REQUESTS_PER_HOUR: 1000,
                    ResourceQuotaType.STORAGE_GB: 10,
                    ResourceQuotaType.CONCURRENT_USERS: 5,
                    ResourceQuotaType.CONSENSUS_OPERATIONS: 100,
                    ResourceQuotaType.CRYPTO_OPERATIONS: 500,
                    ResourceQuotaType.VAULT_COUNT: 3,
                    ResourceQuotaType.AGENT_COUNT: 2
                },
                "features": {
                    "custom_domains": False,
                    "sso_integration": False,
                    "advanced_analytics": False,
                    "priority_support": False,
                    "compliance_reports": False,
                    "audit_logs": True,
                    "api_access": True
                },
                "monthly_price": 99
            },
            TenantTier.PROFESSIONAL: {
                "resource_quotas": {
                    ResourceQuotaType.API_REQUESTS_PER_HOUR: 10000,
                    ResourceQuotaType.STORAGE_GB: 100,
                    ResourceQuotaType.CONCURRENT_USERS: 25,
                    ResourceQuotaType.CONSENSUS_OPERATIONS: 1000,
                    ResourceQuotaType.CRYPTO_OPERATIONS: 5000,
                    ResourceQuotaType.VAULT_COUNT: 15,
                    ResourceQuotaType.AGENT_COUNT: 5
                },
                "features": {
                    "custom_domains": True,
                    "sso_integration": True,
                    "advanced_analytics": True,
                    "priority_support": False,
                    "compliance_reports": True,
                    "audit_logs": True,
                    "api_access": True,
                    "webhook_notifications": True
                },
                "monthly_price": 499
            },
            TenantTier.ENTERPRISE: {
                "resource_quotas": {
                    ResourceQuotaType.API_REQUESTS_PER_HOUR: 100000,
                    ResourceQuotaType.STORAGE_GB: 1000,
                    ResourceQuotaType.CONCURRENT_USERS: 100,
                    ResourceQuotaType.CONSENSUS_OPERATIONS: 10000,
                    ResourceQuotaType.CRYPTO_OPERATIONS: 50000,
                    ResourceQuotaType.VAULT_COUNT: 100,
                    ResourceQuotaType.AGENT_COUNT: 20
                },
                "features": {
                    "custom_domains": True,
                    "sso_integration": True,
                    "advanced_analytics": True,
                    "priority_support": True,
                    "compliance_reports": True,
                    "audit_logs": True,
                    "api_access": True,
                    "webhook_notifications": True,
                    "custom_integrations": True,
                    "dedicated_support": True,
                    "sla_guarantee": True
                },
                "monthly_price": 1999
            },
            TenantTier.ENTERPRISE_PLUS: {
                "resource_quotas": {
                    ResourceQuotaType.API_REQUESTS_PER_HOUR: 1000000,
                    ResourceQuotaType.STORAGE_GB: 10000,
                    ResourceQuotaType.CONCURRENT_USERS: 1000,
                    ResourceQuotaType.CONSENSUS_OPERATIONS: 100000,
                    ResourceQuotaType.CRYPTO_OPERATIONS: 500000,
                    ResourceQuotaType.VAULT_COUNT: 1000,
                    ResourceQuotaType.AGENT_COUNT: 100
                },
                "features": {
                    "custom_domains": True,
                    "sso_integration": True,
                    "advanced_analytics": True,
                    "priority_support": True,
                    "compliance_reports": True,
                    "audit_logs": True,
                    "api_access": True,
                    "webhook_notifications": True,
                    "custom_integrations": True,
                    "dedicated_support": True,
                    "sla_guarantee": True,
                    "on_premise_deployment": True,
                    "custom_security_policies": True,
                    "white_label_branding": True
                },
                "monthly_price": 9999
            }
        }
    
    async def create_tenant(
        self,
        name: str,
        tier: TenantTier,
        admin_user_id: str,
        custom_settings: Dict[str, Any] = None
    ) -> TenantConfig:
        """Create a new tenant"""
        
        tenant_id = str(uuid.uuid4())
        tier_config = self.tier_configs[tier]
        
        tenant_config = TenantConfig(
            tenant_id=tenant_id,
            name=name,
            tier=tier,
            created_at=datetime.utcnow(),
            is_active=True,
            settings=custom_settings or {},
            resource_quotas=tier_config["resource_quotas"].copy(),
            feature_flags=tier_config["features"].copy(),
            custom_domains=[]
        )
        
        # Save to database
        session = self.Session()
        try:
            tenant = Tenant(
                id=tenant_id,
                name=name,
                tier=tier.value,
                settings=tenant_config.settings,
                resource_quotas={k.value: v for k, v in tenant_config.resource_quotas.items()},
                feature_flags=tenant_config.feature_flags,
                custom_domains=tenant_config.custom_domains
            )
            session.add(tenant)
            
            # Add admin user
            admin_user = TenantUser(
                tenant_id=tenant_id,
                user_id=admin_user_id,
                role="admin",
                permissions=["*"]  # Full permissions
            )
            session.add(admin_user)
            
            session.commit()
            
            self.logger.info(f"Created tenant {tenant_id} with tier {tier.value}")
            
            # Cache tenant config
            await self._cache_tenant_config(tenant_config)
            
            return tenant_config
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to create tenant: {e}")
            raise
        finally:
            session.close()
    
    async def get_tenant_config(self, tenant_id: str) -> Optional[TenantConfig]:
        """Get tenant configuration"""
        
        # Try cache first
        cached_config = await self._get_cached_tenant_config(tenant_id)
        if cached_config:
            return cached_config
        
        # Query database
        session = self.Session()
        try:
            tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                return None
            
            config = TenantConfig(
                tenant_id=tenant.id,
                name=tenant.name,
                tier=TenantTier(tenant.tier),
                created_at=tenant.created_at,
                is_active=tenant.is_active,
                settings=tenant.settings,
                resource_quotas={ResourceQuotaType(k): v for k, v in tenant.resource_quotas.items()},
                feature_flags=tenant.feature_flags,
                custom_domains=tenant.custom_domains,
                sso_config=tenant.sso_config,
                compliance_settings=tenant.compliance_settings
            )
            
            # Cache for future use
            await self._cache_tenant_config(config)
            
            return config
            
        finally:
            session.close()
    
    async def check_resource_quota(
        self,
        tenant_id: str,
        resource_type: ResourceQuotaType,
        requested_amount: int = 1
    ) -> bool:
        """Check if tenant has sufficient resource quota"""
        
        tenant_config = await self.get_tenant_config(tenant_id)
        if not tenant_config:
            return False
        
        quota_limit = tenant_config.resource_quotas.get(resource_type, 0)
        current_usage = await self._get_current_usage(tenant_id, resource_type)
        
        return (current_usage + requested_amount) <= quota_limit
    
    async def consume_resource_quota(
        self,
        tenant_id: str,
        resource_type: ResourceQuotaType,
        amount: int = 1
    ) -> bool:
        """Consume resource quota if available"""
        
        # Check quota
        if not await self.check_resource_quota(tenant_id, resource_type, amount):
            return False
        
        # Increment usage
        await self._increment_usage(tenant_id, resource_type, amount)
        return True
    
    async def _get_current_usage(self, tenant_id: str, resource_type: ResourceQuotaType) -> int:
        """Get current resource usage for tenant"""
        
        # Check Redis cache for real-time usage
        cache_key = f"usage:{tenant_id}:{resource_type.value}"
        cached_usage = self.redis_client.get(cache_key)
        
        if cached_usage:
            return int(cached_usage)
        
        # Query database for current period
        session = self.Session()
        try:
            current_period_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            usage_record = session.query(TenantUsage).filter(
                TenantUsage.tenant_id == tenant_id,
                TenantUsage.resource_type == resource_type.value,
                TenantUsage.period_start == current_period_start
            ).first()
            
            usage = usage_record.usage_count if usage_record else 0
            
            # Cache for 5 minutes
            self.redis_client.setex(cache_key, 300, usage)
            
            return usage
            
        finally:
            session.close()
    
    async def _increment_usage(self, tenant_id: str, resource_type: ResourceQuotaType, amount: int):
        """Increment resource usage"""
        
        # Update Redis cache
        cache_key = f"usage:{tenant_id}:{resource_type.value}"
        self.redis_client.incrby(cache_key, amount)
        self.redis_client.expire(cache_key, 86400)  # 24 hours
        
        # Update database
        session = self.Session()
        try:
            current_period_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            current_period_end = current_period_start + timedelta(days=1)
            
            usage_record = session.query(TenantUsage).filter(
                TenantUsage.tenant_id == tenant_id,
                TenantUsage.resource_type == resource_type.value,
                TenantUsage.period_start == current_period_start
            ).first()
            
            if usage_record:
                usage_record.usage_count += amount
            else:
                usage_record = TenantUsage(
                    tenant_id=tenant_id,
                    resource_type=resource_type.value,
                    usage_count=amount,
                    period_start=current_period_start,
                    period_end=current_period_end
                )
                session.add(usage_record)
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to update usage: {e}")
        finally:
            session.close()
    
    async def _cache_tenant_config(self, config: TenantConfig):
        """Cache tenant configuration in Redis"""
        
        cache_key = f"tenant_config:{config.tenant_id}"
        self.redis_client.setex(
            cache_key,
            3600,  # 1 hour
            json.dumps(asdict(config), default=str)
        )
    
    async def _get_cached_tenant_config(self, tenant_id: str) -> Optional[TenantConfig]:
        """Get cached tenant configuration"""
        
        cache_key = f"tenant_config:{tenant_id}"
        cached_data = self.redis_client.get(cache_key)
        
        if cached_data:
            try:
                data = json.loads(cached_data)
                data["tier"] = TenantTier(data["tier"])
                data["created_at"] = datetime.fromisoformat(data["created_at"])
                data["resource_quotas"] = {ResourceQuotaType(k): v for k, v in data["resource_quotas"].items()}
                return TenantConfig(**data)
            except Exception as e:
                self.logger.error(f"Failed to deserialize cached tenant config: {e}")
        
        return None
    
    async def create_tenant_vault(
        self,
        tenant_id: str,
        vault_name: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Create a new vault for tenant"""
        
        # Check vault quota
        if not await self.check_resource_quota(tenant_id, ResourceQuotaType.VAULT_COUNT, 1):
            raise ValueError("Vault quota exceeded")
        
        vault_id = str(uuid.uuid4())
        encryption_key = Fernet.generate_key().decode()
        
        session = self.Session()
        try:
            vault = TenantVault(
                tenant_id=tenant_id,
                vault_id=vault_id,
                name=vault_name,
                encryption_key=encryption_key,
                metadata=metadata or {}
            )
            session.add(vault)
            session.commit()
            
            # Consume quota
            await self.consume_resource_quota(tenant_id, ResourceQuotaType.VAULT_COUNT, 1)
            
            self.logger.info(f"Created vault {vault_id} for tenant {tenant_id}")
            return vault_id
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to create vault: {e}")
            raise
        finally:
            session.close()
    
    async def get_tenant_usage_report(self, tenant_id: str, days: int = 30) -> Dict[str, Any]:
        """Generate usage report for tenant"""
        
        session = self.Session()
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            usage_records = session.query(TenantUsage).filter(
                TenantUsage.tenant_id == tenant_id,
                TenantUsage.period_start >= start_date
            ).all()
            
            # Aggregate usage by resource type
            usage_summary = {}
            for record in usage_records:
                resource_type = record.resource_type
                if resource_type not in usage_summary:
                    usage_summary[resource_type] = {
                        "total_usage": 0,
                        "peak_daily_usage": 0,
                        "average_daily_usage": 0
                    }
                
                usage_summary[resource_type]["total_usage"] += record.usage_count
                usage_summary[resource_type]["peak_daily_usage"] = max(
                    usage_summary[resource_type]["peak_daily_usage"],
                    record.usage_count
                )
            
            # Calculate averages
            for resource_type in usage_summary:
                total_days = len([r for r in usage_records if r.resource_type == resource_type])
                if total_days > 0:
                    usage_summary[resource_type]["average_daily_usage"] = (
                        usage_summary[resource_type]["total_usage"] / total_days
                    )
            
            tenant_config = await self.get_tenant_config(tenant_id)
            
            return {
                "tenant_id": tenant_id,
                "tenant_name": tenant_config.name if tenant_config else "Unknown",
                "tier": tenant_config.tier.value if tenant_config else "Unknown",
                "report_period_days": days,
                "generated_at": datetime.utcnow().isoformat(),
                "usage_summary": usage_summary,
                "quotas": {k.value: v for k, v in tenant_config.resource_quotas.items()} if tenant_config else {}
            }
            
        finally:
            session.close()
    
    async def upgrade_tenant_tier(self, tenant_id: str, new_tier: TenantTier) -> bool:
        """Upgrade tenant to new tier"""
        
        session = self.Session()
        try:
            tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                return False
            
            old_tier = TenantTier(tenant.tier)
            new_config = self.tier_configs[new_tier]
            
            # Update tier and quotas
            tenant.tier = new_tier.value
            tenant.resource_quotas = {k.value: v for k, v in new_config["resource_quotas"].items()}
            tenant.feature_flags = new_config["features"].copy()
            
            session.commit()
            
            # Clear cache
            cache_key = f"tenant_config:{tenant_id}"
            self.redis_client.delete(cache_key)
            
            self.logger.info(f"Upgraded tenant {tenant_id} from {old_tier.value} to {new_tier.value}")
            return True
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to upgrade tenant tier: {e}")
            return False
        finally:
            session.close()
    
    async def check_feature_access(self, tenant_id: str, feature_name: str) -> bool:
        """Check if tenant has access to specific feature"""
        
        tenant_config = await self.get_tenant_config(tenant_id)
        if not tenant_config:
            return False
        
        return tenant_config.feature_flags.get(feature_name, False)
    
    async def get_all_tenant_metrics(self) -> Dict[str, Any]:
        """Get metrics across all tenants"""
        
        session = self.Session()
        try:
            # Count tenants by tier
            tenant_counts = {}
            for tier in TenantTier:
                count = session.query(Tenant).filter(
                    Tenant.tier == tier.value,
                    Tenant.is_active == True
                ).count()
                tenant_counts[tier.value] = count
            
            # Total usage for current period
            current_period_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            total_usage = {}
            for resource_type in ResourceQuotaType:
                usage_sum = session.query(TenantUsage).filter(
                    TenantUsage.resource_type == resource_type.value,
                    TenantUsage.period_start == current_period_start
                ).with_entities(TenantUsage.usage_count).all()
                
                total_usage[resource_type.value] = sum(usage[0] for usage in usage_sum)
            
            return {
                "total_active_tenants": sum(tenant_counts.values()),
                "tenants_by_tier": tenant_counts,
                "total_usage_today": total_usage,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        finally:
            session.close()


class TenantMiddleware:
    """FastAPI middleware for tenant isolation"""
    
    def __init__(self, tenancy_manager: MultiTenancyManager):
        self.tenancy_manager = tenancy_manager
        self.logger = logging.getLogger("tenant_middleware")
    
    async def __call__(self, request, call_next):
        """Process request with tenant context"""
        
        # Extract tenant ID from various sources
        tenant_id = await self._extract_tenant_id(request)
        
        if not tenant_id:
            # Public endpoints or error
            return await call_next(request)
        
        # Validate tenant and set context
        tenant_config = await self.tenancy_manager.get_tenant_config(tenant_id)
        if not tenant_config or not tenant_config.is_active:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Invalid or inactive tenant")
        
        # Set tenant context in request state
        request.state.tenant_id = tenant_id
        request.state.tenant_config = tenant_config
        
        # Check API quota
        if not await self.tenancy_manager.check_resource_quota(
            tenant_id, 
            ResourceQuotaType.API_REQUESTS_PER_HOUR, 
            1
        ):
            from fastapi import HTTPException
            raise HTTPException(status_code=429, detail="API quota exceeded")
        
        try:
            response = await call_next(request)
            
            # Consume API quota on successful request
            await self.tenancy_manager.consume_resource_quota(
                tenant_id, 
                ResourceQuotaType.API_REQUESTS_PER_HOUR, 
                1
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Request failed for tenant {tenant_id}: {e}")
            raise
    
    async def _extract_tenant_id(self, request) -> Optional[str]:
        """Extract tenant ID from request"""
        
        # Try header first
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            return tenant_id
        
        # Try subdomain
        host = request.headers.get("Host", "")
        if "." in host:
            subdomain = host.split(".")[0]
            # Check if subdomain maps to tenant
            # This would require a subdomain-to-tenant mapping
            pass
        
        # Try JWT token claim
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # Extract tenant ID from JWT token
            # This would require JWT parsing
            pass
        
        return None


async def main():
    """Initialize multi-tenancy system"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize system
    tenancy_manager = MultiTenancyManager(
        database_url="postgresql://user:pass@localhost/reliquary",
        redis_url="redis://localhost:6379"
    )
    
    # Create example tenant
    config = await tenancy_manager.create_tenant(
        name="Acme Corporation",
        tier=TenantTier.ENTERPRISE,
        admin_user_id="admin-user-123"
    )
    
    print(f"🏢 Multi-tenancy system initialized!")
    print(f"📊 Created example tenant: {config.tenant_id}")
    print(f"🎯 Tier: {config.tier.value}")
    print(f"📈 Quotas: {len(config.resource_quotas)} resource types")
    print(f"🚀 Features: {len([f for f in config.feature_flags.values() if f])} enabled")


if __name__ == "__main__":
    asyncio.run(main())