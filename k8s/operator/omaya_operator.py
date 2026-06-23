"""
OMAYA Kubernetes Operator
Custom Kubernetes operator for managing OMAYA Fleet Monitoring Platform deployments
"""
import kopf
import kubernetes
from kubernetes import client, config
import logging
from typing import Dict, Any, Optional, List
import yaml
import base64
import json
from pydantic import BaseModel, ValidationError, validator

logger = logging.getLogger(__name__)


class DeploymentSpec(BaseModel):
    """Validation model for deployment spec."""
    backendImage: Optional[str] = "omaya-backend:2.5.0"
    backendReplicas: Optional[int] = 2
    frontendImage: Optional[str] = "omaya-frontend:2.5.0"
    frontendReplicas: Optional[int] = 1
    backendEnv: Optional[Dict[str, str]] = {}
    frontendEnv: Optional[Dict[str, str]] = {}
    backendResources: Optional[Dict[str, Any]] = None
    frontendResources: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, str]] = None
    secrets: Optional[Dict[str, str]] = None
    
    @validator('backendReplicas', 'frontendReplicas')
    def validate_replicas(cls, v):
        if v is not None and v < 0:
            raise ValueError('Replicas must be non-negative')
        return v
    
    @validator('backendImage', 'frontendImage')
    def validate_image(cls, v):
        if v and not v:
            raise ValueError('Image cannot be empty')
        return v


class OMAYAOperator:
    """Kubernetes operator for OMAYA platform management."""
    
    def __init__(self, namespace: str = "omaya"):
        """
        Initialize OMAYA operator.
        
        Args:
            namespace: Kubernetes namespace to watch
        """
        self.namespace = namespace
        self.api = client.CoreV1Api()
        self.apps_api = client.AppsV1Api()
        self.custom_api = client.CustomObjectsApi()
        self.autoscaling_api = client.AutoscalingV2Api()
        self.networking_api = client.NetworkingV1Api()
        self.rbac_api = client.RbacAuthorizationV1Api()
        
        # Load kube config
        try:
            config.load_kube_config()
            logger.info("Loaded kube config")
        except config.ConfigException:
            config.load_incluster_config()
            logger.info("Loaded in-cluster config")
    
    def create_namespace(self):
        """Create OMAYA namespace if it doesn't exist."""
        try:
            self.api.create_namespace(
                body=client.V1Namespace(
                    metadata=client.V1ObjectMeta(name=self.namespace)
                )
            )
            logger.info(f"Created namespace {self.namespace}")
        except kubernetes.client.exceptions.ApiException as e:
            if e.status == 409:
                logger.info(f"Namespace {self.namespace} already exists")
            else:
                raise
    
    def validate_spec(self, spec: Dict[str, Any]) -> DeploymentSpec:
        """
        Validate deployment spec using pydantic model.
        
        Args:
            spec: Deployment spec dictionary
            
        Returns:
            Validated DeploymentSpec object
            
        Raises:
            ValidationError: If spec is invalid
        """
        try:
            return DeploymentSpec(**spec)
        except ValidationError as e:
            logger.error(f"Invalid deployment spec: {e}")
            raise
    
    def create_deployment(self, name: str, image: str, replicas: int = 1,
                        env_vars: Dict[str, str] = None, resources: Dict[str, str] = None,
                        liveness_probe: Dict[str, Any] = None, readiness_probe: Dict[str, Any] = None,
                        security_context: Dict[str, Any] = None, image_pull_secrets: List[str] = None,
                        pod_annotations: Dict[str, str] = None):
        """
        Create Kubernetes deployment.
        
        Args:
            name: Deployment name
            image: Container image
            replicas: Number of replicas
            env_vars: Environment variables
            resources: Resource limits/requests
            liveness_probe: Liveness probe configuration
            readiness_probe: Readiness probe configuration
            security_context: Pod security context
            image_pull_secrets: Image pull secrets for private registries
            pod_annotations: Pod annotations
        """
        env = [client.V1EnvVar(name=k, value=v) for k, v in (env_vars or {}).items()]
        
        resource_requirements = None
        if resources:
            resource_requirements = client.V1ResourceRequirements(
                requests=resources.get('requests'),
                limits=resources.get('limits')
            )
        
        # Build probes
        liveness = None
        if liveness_probe:
            liveness = client.V1Probe(
                http_get=client.V1HTTPGetAction(
                    path=liveness_probe.get('path', '/health'),
                    port=liveness_probe.get('port', 8000)
                ) if liveness_probe.get('type') == 'http' else None,
                tcp_socket=client.V1TCPSocketAction(
                    port=liveness_probe.get('port', 8000)
                ) if liveness_probe.get('type') == 'tcp' else None,
                initial_delay_seconds=liveness_probe.get('initialDelaySeconds', 30),
                period_seconds=liveness_probe.get('periodSeconds', 10),
                timeout_seconds=liveness_probe.get('timeoutSeconds', 5),
                failure_threshold=liveness_probe.get('failureThreshold', 3)
            )
        
        readiness = None
        if readiness_probe:
            readiness = client.V1Probe(
                http_get=client.V1HTTPGetAction(
                    path=readiness_probe.get('path', '/ready'),
                    port=readiness_probe.get('port', 8000)
                ) if readiness_probe.get('type') == 'http' else None,
                tcp_socket=client.V1TCPSocketAction(
                    port=readiness_probe.get('port', 8000)
                ) if readiness_probe.get('type') == 'tcp' else None,
                initial_delay_seconds=readiness_probe.get('initialDelaySeconds', 10),
                period_seconds=readiness_probe.get('periodSeconds', 5),
                timeout_seconds=readiness_probe.get('timeoutSeconds', 3),
                failure_threshold=readiness_probe.get('failureThreshold', 3)
            )
        
        # Build security context
        pod_security_context = None
        if security_context:
            pod_security_context = client.V1PodSecurityContext(
                run_as_non_root=security_context.get('runAsNonRoot', True),
                run_as_user=security_context.get('runAsUser'),
                fs_group=security_context.get('fsGroup'),
                seccomp_profile=client.V1SeccompProfile(
                    type=security_context.get('seccompProfileType', 'RuntimeDefault')
                ) if security_context.get('seccompProfileType') else None
            )
        
        container = client.V1Container(
            name=name,
            image=image,
            env=env,
            resources=resource_requirements,
            liveness_probe=liveness,
            readiness_probe=readiness
        )
        
        # Build image pull secrets
        image_pull_secret_refs = None
        if image_pull_secrets:
            image_pull_secret_refs = [
                client.V1LocalObjectReference(name=secret) 
                for secret in image_pull_secrets
            ]
        
        # Merge pod annotations with Prometheus metrics annotations
        final_annotations = pod_annotations or {}
        final_annotations.update({
            'prometheus.io/scrape': 'true',
            'prometheus.io/port': '8000',
            'prometheus.io/path': '/metrics'
        })
        
        spec = client.V1DeploymentSpec(
            replicas=replicas,
            selector=client.V1LabelSelector(match_labels={"app": name}),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={"app": name},
                    annotations=final_annotations
                ),
                spec=client.V1PodSpec(
                    containers=[container],
                    security_context=pod_security_context,
                    image_pull_secrets=image_pull_secret_refs
                )
            )
        )
        
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(name=name, namespace=self.namespace),
            spec=spec
        )
        
        try:
            self.apps_api.create_namespaced_deployment(
                namespace=self.namespace,
                body=deployment
            )
            logger.info(f"Created deployment {name}")
        except kubernetes.client.exceptions.ApiException as e:
            if e.status == 409:
                logger.info(f"Deployment {name} already exists")
            else:
                raise
    
    def create_service(self, name: str, port: int, target_port: int, 
                      service_type: str = "ClusterIP"):
        """
        Create Kubernetes service.
        
        Args:
            name: Service name
            port: Service port
            target_port: Container port
            service_type: Service type (ClusterIP, NodePort, LoadBalancer)
        """
        spec = client.V1ServiceSpec(
            ports=[client.V1ServicePort(port=port, target_port=target_port)],
            selector={"app": name},
            type=service_type
        )
        
        service = client.V1Service(
            metadata=client.V1ObjectMeta(name=name, namespace=self.namespace),
            spec=spec
        )
        
        try:
            self.api.create_namespaced_service(
                namespace=self.namespace,
                body=service
            )
            logger.info(f"Created service {name}")
        except kubernetes.client.exceptions.ApiException as e:
            if e.status == 409:
                logger.info(f"Service {name} already exists")
            else:
                raise
    
    def create_configmap(self, name: str, data: Dict[str, str]):
        """
        Create ConfigMap.
        
        Args:
            name: ConfigMap name
            data: Configuration data
        """
        configmap = client.V1ConfigMap(
            metadata=client.V1ObjectMeta(name=name, namespace=self.namespace),
            data=data
        )
        
        try:
            self.api.create_namespaced_config_map(
                namespace=self.namespace,
                body=configmap
            )
            logger.info(f"Created ConfigMap {name}")
        except kubernetes.client.exceptions.ApiException as e:
            if e.status == 409:
                logger.info(f"ConfigMap {name} already exists")
            else:
                raise
    
    def create_secret(self, name: str, data: Dict[str, bytes], secret_type: str = "Opaque"):
        """
        Create Secret.
        
        Args:
            name: Secret name
            data: Secret data (base64 encoded)
            secret_type: Secret type
        """
        secret = client.V1Secret(
            metadata=client.V1ObjectMeta(name=name, namespace=self.namespace),
            type=secret_type,
            data=data
        )
        
        try:
            self.api.create_namespaced_secret(
                namespace=self.namespace,
                body=secret
            )
            logger.info(f"Created Secret {name}")
        except kubernetes.client.exceptions.ApiException as e:
            if e.status == 409:
                logger.info(f"Secret {name} already exists")
            else:
                raise
    
    def scale_deployment(self, name: str, replicas: int):
        """
        Scale deployment.
        
        Args:
            name: Deployment name
            replicas: Number of replicas
        """
        try:
            body = {"spec": {"replicas": replicas}}
            self.apps_api.patch_namespaced_deployment_scale(
                name=name,
                namespace=self.namespace,
                body=body
            )
            logger.info(f"Scaled deployment {name} to {replicas} replicas")
        except kubernetes.client.exceptions.ApiException as e:
            logger.error(f"Failed to scale deployment {name}: {e}")
            raise
    
    def get_deployment_status(self, name: str) -> Dict[str, Any]:
        """
        Get deployment status.
        
        Args:
            name: Deployment name
            
        Returns:
            Deployment status dictionary
        """
        try:
            deployment = self.apps_api.read_namespaced_deployment(
                name=name,
                namespace=self.namespace
            )
            
            return {
                "name": deployment.metadata.name,
                "replicas": deployment.spec.replicas,
                "available_replicas": deployment.status.available_replicas or 0,
                "ready_replicas": deployment.status.ready_replicas or 0,
                "updated_replicas": deployment.status.updated_replicas or 0,
                "conditions": [
                    {
                        "type": cond.type,
                        "status": cond.status,
                        "reason": cond.reason,
                        "message": cond.message
                    }
                    for cond in deployment.status.conditions or []
                ]
            }
        except kubernetes.client.exceptions.ApiException as e:
            logger.error(f"Failed to get deployment status for {name}: {e}")
            raise
    
    def delete_deployment(self, name: str):
        """
        Delete deployment.
        
        Args:
            name: Deployment name
        """
        self.apps_api.delete_namespaced_deployment(
            name=name,
            namespace=self.namespace
        )
        logger.info(f"Deleted deployment {name}")


# Kopf handlers for custom resources

@kopf.on.create('omaya.io', 'v1', 'omayadeployments')
def handle_omaya_deployment_create(spec, name, namespace, logger, **kwargs):
    """Handle OMAYA deployment creation."""
    logger.info(f"Creating OMAYA deployment {name}")
    
    operator = OMAYAOperator(namespace=namespace)
    operator.create_namespace()
    
    # Create backend deployment
    operator.create_deployment(
        name=f"{name}-backend",
        image=spec.get('backendImage', 'omaya-backend:2.5.0'),
        replicas=spec.get('backendReplicas', 2),
        env_vars=spec.get('backendEnv', {}),
        resources=spec.get('backendResources')
    )
    
    # Create frontend deployment
    operator.create_deployment(
        name=f"{name}-frontend",
        image=spec.get('frontendImage', 'omaya-frontend:2.5.0'),
        replicas=spec.get('frontendReplicas', 1),
        env_vars=spec.get('frontendEnv', {}),
        resources=spec.get('frontendResources')
    )
    
    # Create services
    operator.create_service(f"{name}-backend", 8000, 8000)
    operator.create_service(f"{name}-frontend", 80, 80, "LoadBalancer")
    
    # Create ConfigMaps
    if spec.get('config'):
        operator.create_configmap(f"{name}-config", spec['config'])
    
    # Create Secrets
    if spec.get('secrets'):
        operator.create_secret(f"{name}-secrets", spec['secrets'])


@kopf.on.update('omaya.io', 'v1', 'omayadeployments')
def handle_omaya_deployment_update(spec, old, name, namespace, logger, **kwargs):
    """Handle OMAYA deployment update."""
    logger.info(f"Updating OMAYA deployment {name}")
    
    operator = OMAYAOperator(namespace=namespace)
    
    # Scale deployments if replicas changed
    new_backend_replicas = spec.get('backendReplicas')
    if new_backend_replicas is not None and new_backend_replicas != old.get('backendReplicas'):
        operator.scale_deployment(f"{name}-backend", new_backend_replicas)
    
    new_frontend_replicas = spec.get('frontendReplicas')
    if new_frontend_replicas is not None and new_frontend_replicas != old.get('frontendReplicas'):
        operator.scale_deployment(f"{name}-frontend", new_frontend_replicas)
    
    # Update ConfigMaps if config changed
    new_config = spec.get('config')
    if new_config != old.get('config'):
        try:
            operator.api.delete_namespaced_config_map(
                name=f"{name}-config",
                namespace=namespace
            )
        except kubernetes.client.exceptions.ApiException as e:
            if e.status != 404:
                raise
        
        if new_config:
            operator.create_configmap(f"{name}-config", new_config)


@kopf.on.delete('omaya.io', 'v1', 'omayadeployments')
def handle_omaya_deployment_delete(name, namespace, logger, **kwargs):
    """Handle OMAYA deployment deletion."""
    logger.info(f"Deleting OMAYA deployment {name}")
    
    operator = OMAYAOperator(namespace=namespace)
    
    # Delete deployments
    try:
        operator.delete_deployment(f"{name}-backend")
    except kubernetes.client.exceptions.ApiException as e:
        if e.status != 404:
            logger.warning(f"Failed to delete backend deployment: {e}")
    
    try:
        operator.delete_deployment(f"{name}-frontend")
    except kubernetes.client.exceptions.ApiException as e:
        if e.status != 404:
            logger.warning(f"Failed to delete frontend deployment: {e}")
    
    # Delete services
    try:
        operator.api.delete_namespaced_service(
            name=f"{name}-backend",
            namespace=namespace
        )
    except kubernetes.client.exceptions.ApiException as e:
        if e.status != 404:
            logger.warning(f"Failed to delete backend service: {e}")
    
    try:
        operator.api.delete_namespaced_service(
            name=f"{name}-frontend",
            namespace=namespace
        )
    except kubernetes.client.exceptions.ApiException as e:
        if e.status != 404:
            logger.warning(f"Failed to delete frontend service: {e}")


@kopf.on.field('omaya.io', 'v1', 'omayadeployments', field='status.replicas')
def handle_replicas_change(old, new, name, namespace, logger, **kwargs):
    """Handle replicas field change."""
    logger.info(f"Replicas changed for {name}: {old} -> {new}")
    
    operator = OMAYAOperator(namespace=namespace)
    operator.scale_deployment(f"{name}-backend", new)


def generate_crd():
    """Generate Custom Resource Definition for OMAYA deployments."""
    crd = {
        "apiVersion": "apiextensions.k8s.io/v1",
        "kind": "CustomResourceDefinition",
        "metadata": {
            "name": "omayadeployments.omaya.io"
        },
        "spec": {
            "group": "omaya.io",
            "versions": [
                {
                    "name": "v1",
                    "served": True,
                    "storage": True,
                    "schema": {
                        "openAPIV3Schema": {
                            "type": "object",
                            "properties": {
                                "spec": {
                                    "type": "object",
                                    "properties": {
                                        "backendImage": {"type": "string"},
                                        "backendReplicas": {"type": "integer"},
                                        "frontendImage": {"type": "string"},
                                        "frontendReplicas": {"type": "integer"},
                                        "backendEnv": {"type": "object"},
                                        "frontendEnv": {"type": "object"},
                                        "backendResources": {
                                            "type": "object",
                                            "properties": {
                                                "requests": {"type": "object"},
                                                "limits": {"type": "object"}
                                            }
                                        },
                                        "frontendResources": {
                                            "type": "object",
                                            "properties": {
                                                "requests": {"type": "object"},
                                                "limits": {"type": "object"}
                                            }
                                        },
                                        "config": {"type": "object"},
                                        "secrets": {"type": "object"}
                                    }
                                },
                                "status": {
                                    "type": "object",
                                    "properties": {
                                        "replicas": {"type": "integer"},
                                        "backendStatus": {"type": "string"},
                                        "frontendStatus": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            ],
            "scope": "Namespaced",
            "names": {
                "plural": "omayadeployments",
                "singular": "omayadeployment",
                "kind": "OMAYADeployment",
                "shortNames": ["omaya"]
            }
        }
    }
    
    return crd


def generate_example_cr():
    """Generate example Custom Resource."""
    cr = {
        "apiVersion": "omaya.io/v1",
        "kind": "OMAYADeployment",
        "metadata": {
            "name": "omaya-production",
            "namespace": "omaya"
        },
        "spec": {
            "backendImage": "omaya-backend:2.5.0",
            "backendReplicas": 3,
            "frontendImage": "omaya-frontend:2.5.0",
            "frontendReplicas": 2,
            "backendEnv": {
                "REDIS_HOST": "redis",
                "KAFKA_BROKERS": "kafka:9092",
                "DATABASE_URL": "postgresql://user:pass@timescaledb:5432/omaya"
            },
            "frontendEnv": {
                "VITE_API_URL": "http://omaya-production-backend:8000"
            },
            "backendResources": {
                "requests": {
                    "cpu": "500m",
                    "memory": "512Mi"
                },
                "limits": {
                    "cpu": "2000m",
                    "memory": "2Gi"
                }
            },
            "frontendResources": {
                "requests": {
                    "cpu": "100m",
                    "memory": "128Mi"
                },
                "limits": {
                    "cpu": "500m",
                    "memory": "512Mi"
                }
            }
        }
    }
    
    return cr


def main():
    """Main entry point for the operator."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting OMAYA Kubernetes Operator")
    
    # Create operator instance
    operator = OMAYAOperator()
    operator.create_namespace()
    
    # Start Kopf operator
    kopf.run()


if __name__ == "__main__":
    main()
