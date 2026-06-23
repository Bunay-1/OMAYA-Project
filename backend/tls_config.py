"""
TLS Configuration Module
Internal communications encryption
"""
import os
import ssl
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class TLSConfig:
    """
    TLS configuration for secure internal communications
    """
    
    def __init__(self):
        self.certs_dir = Path(os.getenv("CERTS_DIR", "/etc/ssl/omaya"))
        self.ca_cert = self.certs_dir / "ca.crt"
        self.server_cert = self.certs_dir / "server.crt"
        self.server_key = self.certs_dir / "server.key"
        self.client_cert = self.certs_dir / "client.crt"
        self.client_key = self.certs_dir / "client.key"
        
        self.tls_version = ssl.TLSVersion.TLSv1_3
        self.verify_mode = ssl.CERT_REQUIRED
    
    def get_server_ssl_context(self) -> Optional[ssl.SSLContext]:
        """
        Create SSL context for server
        
        Returns:
            SSLContext for server or None if certs not available
        """
        if not self._certs_exist():
            logger.warning("TLS certificates not found. Running without TLS.")
            return None
        
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.minimum_version = self.tls_version
            
            # Load server certificate
            context.load_cert_chain(
                certfile=str(self.server_cert),
                keyfile=str(self.server_key)
            )
            
            # Load CA for client verification
            context.load_verify_locations(cafile=str(self.ca_cert))
            context.verify_mode = self.verify_mode
            
            # Security settings
            context.set_ciphers('ECDHE+AESGCM:DHE+AESGCM:ECDHE+CHACHA20:DHE+CHACHA20')
            context.options |= ssl.OP_NO_SSLv2
            context.options |= ssl.OP_NO_SSLv3
            context.options |= ssl.OP_NO_TLSv1
            context.options |= ssl.OP_NO_TLSv1_1
            
            logger.info("✅ Server TLS context created")
            return context
            
        except Exception as e:
            logger.error(f"Error creating server SSL context: {e}")
            return None
    
    def get_client_ssl_context(self) -> Optional[ssl.SSLContext]:
        """
        Create SSL context for client connections
        
        Returns:
            SSLContext for client or None if certs not available
        """
        if not self._certs_exist():
            logger.warning("TLS certificates not found")
            return None
        
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.minimum_version = self.tls_version
            
            # Load client certificate
            context.load_cert_chain(
                certfile=str(self.client_cert),
                keyfile=str(self.client_key)
            )
            
            # Load CA for server verification
            context.load_verify_locations(cafile=str(self.ca_cert))
            context.verify_mode = self.verify_mode
            context.check_hostname = True
            
            logger.info("✅ Client TLS context created")
            return context
            
        except Exception as e:
            logger.error(f"Error creating client SSL context: {e}")
            return None
    
    def _certs_exist(self) -> bool:
        """Check if required certificates exist"""
        required = [self.ca_cert, self.server_cert, self.server_key]
        return all(cert.exists() for cert in required)
    
    def get_redis_tls_config(self) -> Dict:
        """
        Get TLS configuration for Redis connection
        
        Returns:
            Redis TLS config dict
        """
        if not self._certs_exist():
            return {}
        
        return {
            "ssl": True,
            "ssl_ca_certs": str(self.ca_cert),
            "ssl_certfile": str(self.client_cert),
            "ssl_keyfile": str(self.client_key),
            "ssl_cert_reqs": "required"
        }
    
    def get_kafka_tls_config(self) -> Dict:
        """
        Get TLS configuration for Kafka connection
        
        Returns:
            Kafka TLS config dict
        """
        if not self._certs_exist():
            return {}
        
        return {
            "security_protocol": "SSL",
            "ssl_cafile": str(self.ca_cert),
            "ssl_certfile": str(self.client_cert),
            "ssl_keyfile": str(self.client_key),
            "ssl_check_hostname": True
        }
    
    def get_postgres_tls_config(self) -> Dict:
        """
        Get TLS configuration for PostgreSQL connection
        
        Returns:
            PostgreSQL TLS config dict
        """
        if not self._certs_exist():
            return {"sslmode": "prefer"}
        
        return {
            "sslmode": "verify-full",
            "sslrootcert": str(self.ca_cert),
            "sslcert": str(self.client_cert),
            "sslkey": str(self.client_key)
        }
    
    def generate_self_signed_certs(self, common_name: str = "omaya-monitoring") -> bool:
        """
        Generate self-signed certificates for development
        
        Args:
            common_name: Common name for certificates
            
        Returns:
            True if successful
        """
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.backends import default_backend
            from datetime import datetime, timedelta
            
            # Create directory
            self.certs_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate CA key
            ca_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
            
            # Generate CA certificate
            ca_name = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "OMAYA Monitoring"),
                x509.NameAttribute(NameOID.COMMON_NAME, f"{common_name} CA"),
            ])
            
            ca_cert = (
                x509.CertificateBuilder()
                .subject_name(ca_name)
                .issuer_name(ca_name)
                .public_key(ca_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.utcnow())
                .not_valid_after(datetime.utcnow() + timedelta(days=3650))
                .add_extension(
                    x509.BasicConstraints(ca=True, path_length=None),
                    critical=True
                )
                .sign(ca_key, hashes.SHA256(), default_backend())
            )
            
            # Write CA cert
            with open(self.ca_cert, "wb") as f:
                f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
            
            # Generate server key
            server_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Generate server certificate
            server_name = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "OMAYA Monitoring"),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ])
            
            server_cert = (
                x509.CertificateBuilder()
                .subject_name(server_name)
                .issuer_name(ca_name)
                .public_key(server_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.utcnow())
                .not_valid_after(datetime.utcnow() + timedelta(days=365))
                .add_extension(
                    x509.SubjectAlternativeName([
                        x509.DNSName("localhost"),
                        x509.DNSName(common_name),
                        x509.DNSName("*.omaya-monitoring.com"),
                    ]),
                    critical=False
                )
                .sign(ca_key, hashes.SHA256(), default_backend())
            )
            
            # Write server cert and key
            with open(self.server_cert, "wb") as f:
                f.write(server_cert.public_bytes(serialization.Encoding.PEM))
            
            with open(self.server_key, "wb") as f:
                f.write(server_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Generate client key and cert (same process)
            client_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            client_name = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "OMAYA Monitoring"),
                x509.NameAttribute(NameOID.COMMON_NAME, f"{common_name}-client"),
            ])
            
            client_cert = (
                x509.CertificateBuilder()
                .subject_name(client_name)
                .issuer_name(ca_name)
                .public_key(client_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.utcnow())
                .not_valid_after(datetime.utcnow() + timedelta(days=365))
                .sign(ca_key, hashes.SHA256(), default_backend())
            )
            
            with open(self.client_cert, "wb") as f:
                f.write(client_cert.public_bytes(serialization.Encoding.PEM))
            
            with open(self.client_key, "wb") as f:
                f.write(client_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            logger.info("✅ Self-signed certificates generated")
            return True
            
        except ImportError:
            logger.error("cryptography library not installed")
            return False
        except Exception as e:
            logger.error(f"Error generating certificates: {e}")
            return False

# Singleton instance
tls_config = TLSConfig()
