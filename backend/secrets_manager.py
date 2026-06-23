"""
Secrets Management Module
HashiCorp Vault / Kubernetes Secrets integration
"""
import os
import json
import logging
from typing import Dict, Optional, Any
from functools import lru_cache

logger = logging.getLogger(__name__)

class SecretsManager:
    """
    Unified secrets management supporting multiple backends:
    - HashiCorp Vault
    - Kubernetes Secrets
    - AWS Secrets Manager
    - Environment variables (fallback)
    """
    
    def __init__(self):
        self.backend = os.getenv("SECRETS_BACKEND", "env")  # vault, k8s, aws, env
        self.vault_addr = os.getenv("VAULT_ADDR", "http://localhost:8200")
        self.vault_token = os.getenv("VAULT_TOKEN")
        self.vault_namespace = os.getenv("VAULT_NAMESPACE", "omaya-monitoring")
        
        self.client = None
        self._init_backend()
    
    def _init_backend(self):
        """Initialize secrets backend"""
        if self.backend == "vault":
            self._init_vault()
        elif self.backend == "k8s":
            self._init_kubernetes()
        elif self.backend == "aws":
            self._init_aws()
        else:
            logger.info("Using environment variables for secrets")
    
    def _init_vault(self):
        """Initialize HashiCorp Vault client"""
        try:
            import hvac
            
            self.client = hvac.Client(
                url=self.vault_addr,
                token=self.vault_token,
                namespace=self.vault_namespace
            )
            
            if self.client.is_authenticated():
                logger.info(f"✅ Connected to Vault: {self.vault_addr}")
            else:
                logger.warning("⚠️  Vault authentication failed")
                self.backend = "env"
                
        except ImportError:
            logger.warning("hvac library not installed. Using env fallback.")
            self.backend = "env"
        except Exception as e:
            logger.error(f"Vault initialization error: {e}")
            self.backend = "env"
    
    def _init_kubernetes(self):
        """Initialize Kubernetes secrets access"""
        try:
            from kubernetes import client, config
            
            # Try in-cluster config first, then local config
            try:
                config.load_incluster_config()
            except config.ConfigException:
                config.load_kube_config()
            
            self.client = client.CoreV1Api()
            logger.info("✅ Connected to Kubernetes Secrets")
            
        except ImportError:
            logger.warning("kubernetes library not installed. Using env fallback.")
            self.backend = "env"
        except Exception as e:
            logger.error(f"Kubernetes initialization error: {e}")
            self.backend = "env"
    
    def _init_aws(self):
        """Initialize AWS Secrets Manager client"""
        try:
            import boto3
            
            self.client = boto3.client(
                'secretsmanager',
                region_name=os.getenv("AWS_REGION", "us-east-1")
            )
            logger.info("✅ Connected to AWS Secrets Manager")
            
        except ImportError:
            logger.warning("boto3 library not installed. Using env fallback.")
            self.backend = "env"
        except Exception as e:
            logger.error(f"AWS initialization error: {e}")
            self.backend = "env"
    
    @lru_cache(maxsize=100)
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a secret value
        
        Args:
            key: Secret key/path
            default: Default value if not found
            
        Returns:
            Secret value or default
        """
        try:
            if self.backend == "vault":
                return self._get_vault_secret(key) or default
            elif self.backend == "k8s":
                return self._get_k8s_secret(key) or default
            elif self.backend == "aws":
                return self._get_aws_secret(key) or default
            else:
                return os.getenv(key, default)
                
        except Exception as e:
            logger.error(f"Error getting secret {key}: {e}")
            return default
    
    def _get_vault_secret(self, key: str) -> Optional[str]:
        """Get secret from Vault"""
        if not self.client:
            return None
        
        try:
            # Parse key path (e.g., "secret/data/omaya/database")
            if "/" in key:
                path, secret_key = key.rsplit("/", 1)
            else:
                path = f"secret/data/omaya"
                secret_key = key
            
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path.replace("secret/data/", "")
            )
            
            return response["data"]["data"].get(secret_key)
            
        except Exception as e:
            logger.debug(f"Vault secret not found: {key}")
            return None
    
    def _get_k8s_secret(self, key: str) -> Optional[str]:
        """Get secret from Kubernetes"""
        if not self.client:
            return None
        
        try:
            namespace = os.getenv("K8S_NAMESPACE", "omaya-monitoring")
            
            # Parse key (e.g., "secret-name/key")
            if "/" in key:
                secret_name, secret_key = key.split("/", 1)
            else:
                secret_name = "omaya-secrets"
                secret_key = key
            
            secret = self.client.read_namespaced_secret(
                name=secret_name,
                namespace=namespace
            )
            
            import base64
            data = secret.data.get(secret_key)
            return base64.b64decode(data).decode() if data else None
            
        except Exception as e:
            logger.debug(f"K8s secret not found: {key}")
            return None
    
    def _get_aws_secret(self, key: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager"""
        if not self.client:
            return None
        
        try:
            response = self.client.get_secret_value(SecretId=key)
            
            if 'SecretString' in response:
                secret = json.loads(response['SecretString'])
                # Return entire secret or specific key
                if isinstance(secret, dict) and len(secret) == 1:
                    return list(secret.values())[0]
                return response['SecretString']
            
            return None
            
        except Exception as e:
            logger.debug(f"AWS secret not found: {key}")
            return None
    
    def set_secret(self, key: str, value: str) -> bool:
        """
        Set a secret value (for Vault and AWS only)
        
        Args:
            key: Secret key/path
            value: Secret value
            
        Returns:
            True if successful
        """
        try:
            if self.backend == "vault":
                return self._set_vault_secret(key, value)
            elif self.backend == "aws":
                return self._set_aws_secret(key, value)
            else:
                logger.warning(f"Cannot set secrets with backend: {self.backend}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting secret {key}: {e}")
            return False
    
    def _set_vault_secret(self, key: str, value: str) -> bool:
        """Set secret in Vault"""
        if not self.client:
            return False
        
        try:
            if "/" in key:
                path, secret_key = key.rsplit("/", 1)
            else:
                path = "omaya"
                secret_key = key
            
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret={secret_key: value}
            )
            
            # Clear cache
            self.get_secret.cache_clear()
            return True
            
        except Exception as e:
            logger.error(f"Error setting Vault secret: {e}")
            return False
    
    def _set_aws_secret(self, key: str, value: str) -> bool:
        """Set secret in AWS Secrets Manager"""
        if not self.client:
            return False
        
        try:
            self.client.put_secret_value(
                SecretId=key,
                SecretString=value
            )
            
            # Clear cache
            self.get_secret.cache_clear()
            return True
            
        except self.client.exceptions.ResourceNotFoundException:
            # Create new secret
            self.client.create_secret(
                Name=key,
                SecretString=value
            )
            return True
        except Exception as e:
            logger.error(f"Error setting AWS secret: {e}")
            return False
    
    def get_database_credentials(self) -> Dict[str, str]:
        """Get database credentials"""
        return {
            "host": self.get_secret("TIMESCALE_HOST", "localhost"),
            "port": self.get_secret("TIMESCALE_PORT", "5432"),
            "database": self.get_secret("TIMESCALE_DB", "omaya_monitoring"),
            "username": self.get_secret("TIMESCALE_USER", "omaya_user"),
            "password": self.get_secret("TIMESCALE_PASSWORD", "")
        }
    
    def get_redis_credentials(self) -> Dict[str, str]:
        """Get Redis credentials"""
        return {
            "host": self.get_secret("REDIS_HOST", "localhost"),
            "port": self.get_secret("REDIS_PORT", "6379"),
            "password": self.get_secret("REDIS_PASSWORD", "")
        }
    
    def get_kafka_credentials(self) -> Dict[str, str]:
        """Get Kafka credentials"""
        return {
            "bootstrap_servers": self.get_secret("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            "username": self.get_secret("KAFKA_USERNAME", ""),
            "password": self.get_secret("KAFKA_PASSWORD", "")
        }
    
    def get_jwt_secret(self) -> str:
        """Get JWT signing secret"""
        return self.get_secret("SECRET_KEY", "change-me-in-production")
    
    def rotate_secret(self, key: str, new_value: str) -> bool:
        """
        Rotate a secret (with versioning in Vault/AWS)
        
        Args:
            key: Secret key
            new_value: New secret value
            
        Returns:
            True if successful
        """
        # Set new secret (Vault/AWS handle versioning)
        success = self.set_secret(key, new_value)
        
        if success:
            logger.info(f"✅ Secret rotated: {key}")
            # Clear cache
            self.get_secret.cache_clear()
        
        return success
    
    def get_status(self) -> Dict:
        """Get secrets manager status"""
        status = {
            "backend": self.backend,
            "connected": False,
            "features": []
        }
        
        if self.backend == "vault":
            status["connected"] = self.client and self.client.is_authenticated()
            status["features"] = ["versioning", "rotation", "dynamic_secrets"]
            status["address"] = self.vault_addr
        elif self.backend == "k8s":
            status["connected"] = self.client is not None
            status["features"] = ["namespaced", "rbac"]
        elif self.backend == "aws":
            status["connected"] = self.client is not None
            status["features"] = ["versioning", "rotation", "encryption"]
        else:
            status["connected"] = True
            status["features"] = ["simple"]
        
        return status

# Singleton instance
secrets_manager = SecretsManager()

# Convenience function
def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a secret value"""
    return secrets_manager.get_secret(key, default)
