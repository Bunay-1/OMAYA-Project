"""
Data Lake Integration
S3/MinIO storage for long-term data archival
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from io import BytesIO

logger = logging.getLogger(__name__)

class DataLakeClient:
    """
    Data Lake client for S3/MinIO integration
    Handles long-term storage of telemetry, predictions, and models
    """
    
    def __init__(self):
        self.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
        
        self.client = None
        self.connected = False
        
        self._connect()
    
    def _connect(self):
        """Connect to MinIO/S3"""
        try:
            from minio import Minio
            
            self.client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            
            # Test connection
            self.client.list_buckets()
            self.connected = True
            logger.info(f"✅ Connected to Data Lake: {self.endpoint}")
            
            # Ensure buckets exist
            self._ensure_buckets()
            
        except Exception as e:
            logger.warning(f"⚠️  Data Lake not available: {e}")
            self.connected = False
    
    def _ensure_buckets(self):
        """Ensure required buckets exist"""
        buckets = [
            "omaya-telemetry",
            "omaya-predictions",
            "omaya-alerts",
            "omaya-models",
            "omaya-reports"
        ]
        
        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    logger.info(f"Created bucket: {bucket}")
            except Exception as e:
                logger.error(f"Error creating bucket {bucket}: {e}")
    
    def store_telemetry(self, machine_id: str, data: Dict[str, Any]) -> bool:
        """
        Store telemetry data in Data Lake
        
        Args:
            machine_id: Machine identifier
            data: Telemetry data
            
        Returns:
            True if successful
        """
        if not self.connected:
            return False
        
        try:
            timestamp = datetime.now()
            path = f"telemetry/{machine_id}/{timestamp.strftime('%Y/%m/%d')}/{timestamp.strftime('%H%M%S')}.json"
            
            # Add metadata
            record = {
                **data,
                "machine_id": machine_id,
                "timestamp": timestamp.isoformat(),
                "stored_at": datetime.now().isoformat()
            }
            
            content = json.dumps(record).encode('utf-8')
            
            self.client.put_object(
                "omaya-telemetry",
                path,
                BytesIO(content),
                len(content),
                content_type="application/json"
            )
            
            logger.debug(f"Stored telemetry: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing telemetry: {e}")
            return False
    
    def store_prediction(self, machine_id: str, prediction: Dict[str, Any]) -> bool:
        """
        Store AI prediction in Data Lake
        
        Args:
            machine_id: Machine identifier
            prediction: Prediction result
            
        Returns:
            True if successful
        """
        if not self.connected:
            return False
        
        try:
            timestamp = datetime.now()
            path = f"predictions/{machine_id}/{timestamp.strftime('%Y/%m/%d')}/{timestamp.strftime('%H%M%S')}.json"
            
            record = {
                **prediction,
                "machine_id": machine_id,
                "predicted_at": timestamp.isoformat()
            }
            
            content = json.dumps(record).encode('utf-8')
            
            self.client.put_object(
                "omaya-predictions",
                path,
                BytesIO(content),
                len(content),
                content_type="application/json"
            )
            
            logger.debug(f"Stored prediction: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing prediction: {e}")
            return False
    
    def store_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Store alert in Data Lake for compliance/audit
        
        Args:
            alert: Alert data
            
        Returns:
            True if successful
        """
        if not self.connected:
            return False
        
        try:
            timestamp = datetime.now()
            severity = alert.get("severity", "info")
            path = f"alerts/{severity}/{timestamp.strftime('%Y/%m/%d')}/{alert.get('id', timestamp.strftime('%H%M%S'))}.json"
            
            record = {
                **alert,
                "archived_at": timestamp.isoformat()
            }
            
            content = json.dumps(record).encode('utf-8')
            
            self.client.put_object(
                "omaya-alerts",
                path,
                BytesIO(content),
                len(content),
                content_type="application/json"
            )
            
            logger.debug(f"Stored alert: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing alert: {e}")
            return False
    
    def store_model(self, model_name: str, model_bytes: bytes, metadata: Dict) -> bool:
        """
        Store trained model in Data Lake
        
        Args:
            model_name: Name of the model
            model_bytes: Serialized model bytes
            metadata: Model metadata
            
        Returns:
            True if successful
        """
        if not self.connected:
            return False
        
        try:
            timestamp = datetime.now()
            version = timestamp.strftime('%Y%m%d_%H%M%S')
            path = f"models/{model_name}/{version}/model.pkl"
            meta_path = f"models/{model_name}/{version}/metadata.json"
            
            # Store model
            self.client.put_object(
                "omaya-models",
                path,
                BytesIO(model_bytes),
                len(model_bytes),
                content_type="application/octet-stream"
            )
            
            # Store metadata
            meta_content = json.dumps({
                **metadata,
                "model_name": model_name,
                "version": version,
                "stored_at": timestamp.isoformat()
            }).encode('utf-8')
            
            self.client.put_object(
                "omaya-models",
                meta_path,
                BytesIO(meta_content),
                len(meta_content),
                content_type="application/json"
            )
            
            logger.info(f"✅ Stored model: {model_name} v{version}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing model: {e}")
            return False
    
    def get_telemetry_history(
        self, 
        machine_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict]:
        """
        Retrieve historical telemetry data
        
        Args:
            machine_id: Machine identifier
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of telemetry records
        """
        if not self.connected:
            return []
        
        try:
            records = []
            prefix = f"telemetry/{machine_id}/"
            
            objects = self.client.list_objects(
                "omaya-telemetry",
                prefix=prefix,
                recursive=True
            )
            
            for obj in objects:
                # Parse date from path
                try:
                    response = self.client.get_object("omaya-telemetry", obj.object_name)
                    record = json.loads(response.read())
                    
                    record_date = datetime.fromisoformat(record.get("timestamp", ""))
                    
                    if start_date <= record_date <= end_date:
                        records.append(record)
                        
                except Exception as e:
                    logger.debug(f"Error reading object {obj.object_name}: {e}")
                    continue
            
            return records
            
        except Exception as e:
            logger.error(f"Error retrieving telemetry history: {e}")
            return []
    
    def generate_report(
        self, 
        report_type: str, 
        data: Dict[str, Any],
        format: str = "json"
    ) -> Optional[str]:
        """
        Generate and store a report
        
        Args:
            report_type: Type of report (daily, weekly, compliance)
            data: Report data
            format: Output format (json, csv)
            
        Returns:
            Path to stored report or None
        """
        if not self.connected:
            return None
        
        try:
            timestamp = datetime.now()
            extension = "json" if format == "json" else "csv"
            path = f"reports/{report_type}/{timestamp.strftime('%Y/%m')}/{timestamp.strftime('%Y%m%d_%H%M%S')}.{extension}"
            
            if format == "json":
                content = json.dumps(data, indent=2).encode('utf-8')
                content_type = "application/json"
            else:
                # Convert to CSV
                import csv
                from io import StringIO
                
                output = StringIO()
                if data.get("records"):
                    writer = csv.DictWriter(output, fieldnames=data["records"][0].keys())
                    writer.writeheader()
                    writer.writerows(data["records"])
                content = output.getvalue().encode('utf-8')
                content_type = "text/csv"
            
            self.client.put_object(
                "omaya-reports",
                path,
                BytesIO(content),
                len(content),
                content_type=content_type
            )
            
            logger.info(f"✅ Generated report: {path}")
            return path
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return None
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        if not self.connected:
            return {"connected": False}
        
        stats = {"connected": True, "buckets": {}}
        
        try:
            for bucket in self.client.list_buckets():
                objects = list(self.client.list_objects(bucket.name, recursive=True))
                total_size = sum(obj.size for obj in objects)
                
                stats["buckets"][bucket.name] = {
                    "object_count": len(objects),
                    "total_size_mb": round(total_size / (1024 * 1024), 2)
                }
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
        
        return stats

# Singleton instance
data_lake = DataLakeClient()
