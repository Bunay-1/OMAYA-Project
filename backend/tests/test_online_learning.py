"""
Tests for Online Learning v2.0 Module
"""
import pytest
from backend.online_learning_v2 import (
    ConceptDriftDetector,
    DriftDetectionResult,
    ModelMetrics,
    ModelVersioning
)
from unittest.mock import Mock
import numpy as np
from datetime import datetime


def test_concept_drift_detector_init():
    """Test concept drift detector initialization."""
    detector = ConceptDriftDetector(threshold=0.1, window_size=1000)
    assert detector.threshold == 0.1
    assert detector.window_size == 1000


def test_concept_drift_detector_add_reference_data():
    """Test adding reference data."""
    detector = ConceptDriftDetector(threshold=0.1, window_size=10)
    data = np.random.rand(10, 5)
    detector.add_reference_data(data)
    assert len(detector.reference_data) == 1


def test_concept_drift_detector_add_current_data():
    """Test adding current data."""
    detector = ConceptDriftDetector(threshold=0.1, window_size=10)
    data = np.random.rand(10, 5)
    detector.add_current_data(data)
    assert len(detector.current_data) == 1


def test_concept_drift_detector_no_drift():
    """Test drift detection with no drift."""
    detector = ConceptDriftDetector(threshold=0.1, window_size=10)
    data = np.random.rand(10, 5)
    detector.add_reference_data(data)
    detector.add_current_data(data)
    
    result = detector.detect_drift()
    assert result.has_drift is False
    assert result.drift_type == 'none'


def test_drift_detection_result():
    """Test drift detection result dataclass."""
    result = DriftDetectionResult(
        has_drift=True,
        drift_score=0.5,
        drift_type='concept',
        timestamp=datetime.now()
    )
    assert result.has_drift is True
    assert result.drift_score == 0.5
    assert result.drift_type == 'concept'


def test_model_metrics():
    """Test model metrics dataclass."""
    metrics = ModelMetrics(
        accuracy=0.95,
        precision=0.93,
        recall=0.91,
        f1_score=0.92,
        auc=0.97,
        timestamp=datetime.now()
    )
    assert metrics.accuracy == 0.95
    assert metrics.precision == 0.93
    assert metrics.recall == 0.91


def test_model_versioning_init():
    """Test model versioning initialization."""
    versioning = ModelVersioning(storage_path="test_versions")
    assert versioning.storage_path == "test_versions"


def test_model_versioning_list_versions():
    """Test listing model versions."""
    versioning = ModelVersioning(storage_path="test_versions")
    versions = versioning.list_versions()
    assert isinstance(versions, list)


def test_concept_drift_detector_window_size_limit():
    """Test window size limit."""
    detector = ConceptDriftDetector(threshold=0.1, window_size=5)
    for i in range(10):
        detector.add_reference_data(np.random.rand(10, 5))
    assert len(detector.reference_data) <= 5


def test_concept_drift_detector_empty_data():
    """Test drift detection with empty data."""
    detector = ConceptDriftDetector(threshold=0.1, window_size=10)
    result = detector.detect_drift()
    assert result.has_drift is False
    assert result.drift_score == 0.0
