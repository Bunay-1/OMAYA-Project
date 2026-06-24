# Vault Integration Guide

## Table of Contents

- [Overview](#overview)
- [Why Vault](#why-vault)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Secret Management](#secret-management)
- [Application Integration](#application-integration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers the integration of HashiCorp Vault with the OMAYA Platform for secure secrets management. Vault provides a centralized, secure way to manage secrets, encryption keys, and certificates.

### Key Benefits

- **Centralized Secret Management**: All secrets in one secure location
- **Dynamic Secrets**: Automatically rotate database credentials
- **Encryption as a Service**: Encrypt/decrypt data without managing keys
- **Audit Logging**: Complete audit trail of secret access
- **Access Control**: Fine-grained permissions and policies

---

## Why Vault

### Security Requirements

The OMAYA Platform handles sensitive data including:
- Database credentials
- API keys
- JWT secrets
- TLS certificates
- Encryption keys

### Compliance Requirements

- **ISO 27001**: Information security management
- **GDPR**: Data protection and privacy
- **SOC 2**: Security and availability controls
- **Industry Regulations**: Manufacturing and industrial standards

### Risk Mitigation

Without Vault:
- Secrets hardcoded in configuration files
- Secrets in version control
- No secret rotation
- No audit trail
- Difficult to revoke access

With Vault:
- Secrets never in code or config
- Automatic secret rotation
- Complete audit logging
- Fine-grained access control
- Easy revocation

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OMAYA Platform                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Frontend  │    │   Backend    │    │  Database    │  │
│  │              │    │              │    │              │  │
│  │  React + TS  │    │   FastAPI    │    │ TimescaleDB  │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │          │
│         │                   │                   │          │
│         └───────────────────┴───────────────────┘          │
│                             │                               │
│                             ▼                               │
│                    ┌──────────────┐                        │
│                    │    Vault     │                        │
│                    │              │                        │
│                    │  Secrets     │                        │
│                    │  Encryption  │                        │
│                    │  Policies    │                        │
│                    └──────────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Components

1. **Vault Server**: Central secret management service
2. **Vault Agent**: Local agent for secret retrieval
3. **Application Integration**: Backend and frontend integration
4. **Audit Device**: Logging and monitoring

---

## Installation

### Development Setup (WARNING: Not for Production)

**SECURITY WARNING**: The development configuration uses Vault in dev mode with a default token. This is **NOT** suitable for production. Never copy dev configuration to production.

Vault is included in the main `docker-compose.yml` for development:

```yaml
vault:
  image: hashicorp/vault:latest
  container_name: omaya-vault
  ports:
    - "8200:8200"
  environment:
    - VAULT_DEV_ROOT_TOKEN_ID=${VAULT_DEV_ROOT_TOKEN_ID:-dev-token}
    - VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200
  cap_add:
    - IPC_LOCK
  restart: unless-stopped
  networks:
    - omaya-network
  volumes:
    - vault-data:/data
```

**Important Security Notes**:
- The dev token is only for local development
- Use environment variable `VAULT_DEV_ROOT_TOKEN_ID` to override
- Never commit the actual token value to version control
- Never use dev mode in production

### Production Setup

For production, use `docker-compose.prod.yml` with proper Vault security:

```yaml
vault:
  image: hashicorp/vault:latest
  container_name: omaya-vault
  ports:
    - "8200:8200"
  environment:
    - VAULT_ADDR=${VAULT_ADDR:-http://0.0.0.0:8200}
    - VAULT_API_ADDR=${VAULT_API_ADDR:-http://0.0.0.0:8200}
  cap_add:
    - IPC_LOCK
  restart: unless-stopped
  networks:
    - omaya-network
  volumes:
    - vault-data:/data
    - ./vault/config:/vault/config:ro
    - ./vault/policies:/vault/policies:ro
    - ./vault/ssl:/vault/ssl:ro
  command: server
```

**Production Security Requirements**:
- Use TLS/SSL for all Vault communication
- Use proper Vault initialization (not dev mode)
- Store unseal keys securely (not in code)
- Use proper authentication methods (not just tokens)
- Enable audit logging
- Use proper secret engines (not just KV)
- Implement proper access policies

### Initial Configuration

```bash
# Start Vault
docker-compose up -d vault

# Initialize Vault (production only)
docker-compose exec vault vault operator init

# Unseal Vault (production only)
docker-compose exec vault vault operator unseal
docker-compose exec vault vault operator unseal
docker-compose exec vault vault operator unseal

# Login with root token
docker-compose exec vault vault login <root-token>
```

---

## Configuration

### Vault Configuration File

Create `vault/config/vault.hcl`:

```hcl
listener "tcp" {
  address = "0.0.0.0:8200"
  tls_cert_file = "/vault/config/cert.pem"
  tls_key_file = "/vault/config/key.pem"
  tls_client_ca_file = "/vault/config/ca.pem"
}

storage "file" {
  path = "/data"
}

ui = true

api_addr = "http://0.0.0.0:8200"
cluster_addr = "https://0.0.0.0:8201"

disable_mlock = true
```

### Environment Variables

```bash
# Backend configuration
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=dev-token
```

---

## Secret Management

### Enable Secrets Engine

```bash
# Enable KV secrets engine
vault secrets enable -path=omaya kv

# Enable database secrets engine
vault secrets enable -path=database database

# Enable transit secrets engine for encryption
vault secrets enable transit
```

### Configure Database Secrets Engine

```bash
# Configure PostgreSQL connection
vault write database/config/omaya-timescaledb \
  plugin_name=postgresql-database-plugin \
  connection_url="postgresql://{{username}}:{{password}}@timescaledb:5432/omaya_monitoring" \
  allowed_roles="omaya-role" \
  username="omaya_vault_user" \
  password="vault_password"

# Create role with TTL
vault write database/roles/omaya-role \
  db_name=omaya-timescaledb \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"
```

### Store Application Secrets

```bash
# Store JWT secret
vault kv put omaya/jwt \
  secret=$(openssl rand -base64 32)

# Store API keys
vault kv put omaya/api \
  minio_access_key=minioadmin \
  minio_secret_key=minioadmin

# Store Redis password
vault kv put omaya/redis \
  password=$(openssl rand -base64 24)

# Store Grafana credentials
vault kv put omaya/grafana \
  admin_user=admin \
  admin_password=$(openssl rand -base64 16)
```

### Configure Transit Encryption

```bash
# Create encryption key
vault write -f transit/keys/omaya-data

# Encrypt data
vault write transit/encrypt/omaya-data \
  plaintext=$(base64 <<< "sensitive-data")

# Decrypt data
vault write transit/decrypt/omaya-data \
  ciphertext=<encrypted-value>
```

---

## Application Integration

### Backend Integration

#### Install Vault Client

```bash
# Add to requirements.txt
hvac==2.1.0
```

#### Vault Client Configuration

Create `backend/vault_client.py`:

```python
import hvac
import os
from typing import Optional, Dict, Any

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=os.getenv('VAULT_ADDR', 'http://vault:8200'),
            token=os.getenv('VAULT_TOKEN', 'dev-token')
        )
        self.client.is_authenticated()
    
    def get_secret(self, path: str) -> Optional[Dict[str, Any]]:
        """Retrieve secret from Vault"""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            return response['data']['data']
        except Exception as e:
            print(f"Error retrieving secret from Vault: {e}")
            return None
    
    def get_database_credentials(self, role: str = 'omaya-role') -> Optional[Dict[str, str]]:
        """Get dynamic database credentials"""
        try:
            response = self.client.secrets.database.generate_credentials(
                name=role
            )
            return {
                'username': response['data']['username'],
                'password': response['data']['password']
            }
        except Exception as e:
            print(f"Error getting database credentials: {e}")
            return None
    
    def encrypt_data(self, plaintext: str, key: str = 'omaya-data') -> Optional[str]:
        """Encrypt data using Transit"""
        try:
            import base64
            response = self.client.secrets.transit.encrypt_data(
                name=key,
                plaintext=base64.b64encode(plaintext.encode()).decode()
            )
            return response['data']['ciphertext']
        except Exception as e:
            print(f"Error encrypting data: {e}")
            return None
    
    def decrypt_data(self, ciphertext: str, key: str = 'omaya-data') -> Optional[str]:
        """Decrypt data using Transit"""
        try:
            import base64
            response = self.client.secrets.transit.decrypt_data(
                name=key,
                ciphertext=ciphertext
            )
            return base64.b64decode(response['data']['plaintext']).decode()
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return None

# Global vault client instance
vault_client = VaultClient()
```

#### Update Backend Configuration

Modify `backend/main.py`:

```python
from backend.vault_client import vault_client

# Get secrets from Vault
jwt_secret = vault_client.get_secret('omaya/jwt')['secret']
db_credentials = vault_client.get_database_credentials()

# Update configuration
app = FastAPI()
app.state.jwt_secret = jwt_secret
app.state.db_credentials = db_credentials
```

#### Update Database Connection

Modify `backend/database.py`:

```python
from backend.vault_client import vault_client

def get_database_url():
    """Get database URL with dynamic credentials"""
    credentials = vault_client.get_database_credentials()
    if credentials:
        return f"postgresql://{credentials['username']}:{credentials['password']}@timescaledb:5432/omaya_monitoring"
    else:
        # Fallback to environment variables
        return f"postgresql://{os.getenv('TIMESCALE_USER')}:{os.getenv('TIMESCALE_PASSWORD')}@timescaledb:5432/{os.getenv('TIMESCALE_DB')}"

# Use dynamic credentials
DATABASE_URL = get_database_url()
```

### Frontend Integration

#### Environment Variables

The frontend doesn't directly access Vault. Instead, secrets are injected via environment variables or API endpoints.

```typescript
// Frontend gets secrets from backend API
const getJwtSecret = async () => {
  const response = await fetch('/api/config/jwt');
  return response.json();
};
```

### Docker Compose Integration

Update `docker-compose.yml`:

```yaml
api:
  build:
    context: ./backend
    dockerfile: Dockerfile
  container_name: omaya-api
  environment:
    - VAULT_ADDR=http://vault:8200
    - VAULT_TOKEN=dev-token
  depends_on:
    vault:
      condition: service_started
  networks:
    - omaya-network
```

---

## Policies

### Create Admin Policy

Create `vault/policies/admin.hcl`:

```hcl
# Allow full access
path "omaya/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "database/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "transit/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "sys/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
```

### Create Application Policy

Create `vault/policies/application.hcl`:

```hcl
# Allow read access to application secrets
path "omaya/jwt" {
  capabilities = ["read"]
}

path "omaya/api" {
  capabilities = ["read"]
}

path "omaya/redis" {
  capabilities = ["read"]
}

# Allow database credential generation
path "database/creds/omaya-role" {
  capabilities = ["read"]
}

# Allow encryption/decryption
path "transit/encrypt/omaya-data" {
  capabilities = ["create", "update"]
}

path "transit/decrypt/omaya-data" {
  capabilities = ["create", "update"]
}
```

### Apply Policies

```bash
# Apply admin policy
vault policy write admin vault/policies/admin.hcl

# Apply application policy
vault policy write application vault/policies/application.hcl

# Create token with application policy
vault token create -policy=application
```

---

## Audit Logging

### Enable Audit Device

```bash
# Enable file audit device
vault audit enable file file_path=/vault/logs/audit.log

# Enable syslog audit device
vault audit enable syslog
```

### Review Audit Logs

```bash
# View audit logs
docker-compose exec vault cat /vault/logs/audit.log

# Search audit logs
vault audit list
```

---

## Best Practices

### Secret Rotation

```bash
# Rotate JWT secret
vault kv patch omaya/jwt secret=$(openssl rand -base64 32)

# Rotate database credentials
vault write -f database/rotate-role/omaya-role
```

### Access Control

- **Principle of Least Privilege**: Grant minimum required access
- **Token TTL**: Use short-lived tokens
- **Role-Based Access**: Use policies for access control
- **Regular Audits**: Review access logs regularly

### Backup and Recovery

```bash
# Backup Vault data
docker cp omaya-vault:/data ./vault-backup

# Restore Vault data
docker cp ./vault-backup omaya-vault:/data
```

### Monitoring

```bash
# Check Vault health
vault status

# Monitor Vault metrics
# Enable Prometheus metrics in Vault config
telemetry {
  prometheus_retention_time = "24h"
  disable_hostname = false
  disable_performance_metrics = false
}
```

---

## Troubleshooting

### Connection Issues

```bash
# Check Vault status
vault status

# Check Vault logs
docker-compose logs vault

# Test connectivity
curl http://localhost:8200/v1/sys/health
```

### Authentication Issues

```bash
# Check token
vault token lookup

# Renew token
vault token renew

# Create new token
vault token create -policy=application
```

### Secret Access Issues

```bash
# Check secret path
vault kv list omaya/

# Test secret retrieval
vault kv get omaya/jwt

# Check policy
vault policy read application
```

---

## Migration from Environment Variables

### Migration Steps

1. **Install and configure Vault**
2. **Migrate secrets to Vault**
3. **Update application code**
4. **Test in development**
5. **Deploy to production**
6. **Remove old secrets from environment**

### Migration Script

```python
# backend/migrate_to_vault.py
import os
from backend.vault_client import vault_client

def migrate_secrets():
    """Migrate secrets from environment variables to Vault"""
    
    # JWT secret
    if 'JWT_SECRET' in os.environ:
        vault_client.client.secrets.kv.v2.create_or_update_secret(
            path='omaya/jwt',
            secret={'secret': os.environ['JWT_SECRET']}
        )
    
    # Database credentials
    if all(k in os.environ for k in ['TIMESCALE_USER', 'TIMESCALE_PASSWORD']):
        vault_client.client.secrets.kv.v2.create_or_update_secret(
            path='omaya/database',
            secret={
                'username': os.environ['TIMESCALE_USER'],
                'password': os.environ['TIMESCALE_PASSWORD']
            }
        )
    
    # Redis password
    if 'REDIS_PASSWORD' in os.environ:
        vault_client.client.secrets.kv.v2.create_or_update_secret(
            path='omaya/redis',
            secret={'password': os.environ['REDIS_PASSWORD']}
        )
    
    print("Secrets migrated to Vault")

if __name__ == '__main__':
    migrate_secrets()
```

---

## Support

For additional help:
- Documentation: [https://docs.omaya-platform.com](https://docs.omaya-platform.com)
- Issues: [https://github.com/Def-Coms/OMAYA-industrial/issues](https://github.com/Def-Coms/OMAYA-industrial/issues)
- Email: security@omaya-platform.com

---

**Version**: 3.1.0
**Last Updated**: June 2026
