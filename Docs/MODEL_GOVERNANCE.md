# Model Governance and Data Retention

OMAYA Platform maintains an enterprise-grade AI governance process to ensure model reliability, traceability, and compliance.

## Model versioning

- All deployed models should be versioned with semantic identifiers.
- Model metadata includes training data range, drift thresholds, performance metrics, and deployment timestamp.
- Recommended pattern: `omaya-model-v1.2.3`.

## Lineage and registry

- Use a model registry such as MLflow, Dagster, or equivalent to store:
  - model artifacts
  - training datasets
  - evaluation reports
  - deployment history
- Track which model version was active at each point in time for audit and rollback purposes.

## Drift monitoring

- PSI drift detection is implemented in the platform.
- Add automated alerts when PSI exceeds safe thresholds.
- Recommended follow-up: automated retraining workflows that trigger from `backend/online_learning_v2.py` and `backend/drift_detection.py`.

## Data retention policy

- **Raw telemetry**: retain for 90 days by default.
- **Aggregated metrics**: retain for 12 months.
- **Cold storage / archive**: move older data to MinIO or external archive.
- Use TimescaleDB compression policies to save storage and maintain query performance.

## Recommended controls

- Periodic review of model performance and retraining cadence.
- Audit logs for model changes and deployments.
- Data retention settings configurable via policy variables in `backend/docker/init-db.sql` and TimescaleDB policy scripts.
