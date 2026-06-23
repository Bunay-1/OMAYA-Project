"""
Tests for Multi-modal Fusion Module
"""
import pytest
from backend.multi_modal_fusion import (
    MultiModalInput,
    LateFusion,
    EarlyFusion,
    AdaptiveFusion
)
import numpy as np


def test_multi_modal_input():
    """Test multi-modal input dataclass."""
    telemetry = np.random.rand(100, 10)
    input_data = MultiModalInput(
        telemetry=telemetry,
        audio=None,
        video=None,
        text=None,
        metadata={"machine_id": "M001"}
    )
    assert input_data.telemetry.shape == (100, 10)
    assert input_data.audio is None
    assert input_data.metadata["machine_id"] == "M001"


def test_late_fusion_init():
    """Test late fusion initialization."""
    fusion = LateFusion(num_modalities=4)
    assert fusion.num_modalities == 4
    assert len(fusion.weights) == 4


def test_late_fusion_fuse():
    """Test late fusion."""
    fusion = LateFusion(num_modalities=3)
    predictions = [
        np.array([0.8]),
        np.array([0.7]),
        np.array([0.9])
    ]
    result = fusion.fuse(predictions)
    assert result[0] == pytest.approx(0.8, abs=0.01)


def test_late_fusion_learn_weights():
    """Test learning fusion weights."""
    fusion = LateFusion(num_modalities=3)
    predictions = [
        np.array([0.8, 0.7, 0.6]),
        np.array([0.7, 0.6, 0.5]),
        np.array([0.9, 0.8, 0.7])
    ]
    ground_truth = np.array([1, 1, 0])
    
    fusion.learn_weights(predictions, ground_truth)
    assert np.sum(fusion.weights) == pytest.approx(1.0, abs=0.01)


def test_early_fusion_fuse():
    """Test early fusion."""
    fusion = EarlyFusion()
    features = [
        np.array([[0.1, 0.2]]),
        np.array([[0.3, 0.4]])
    ]
    result = fusion.fuse(features)
    assert result.shape == (1, 4)


def test_adaptive_fusion_init():
    """Test adaptive fusion initialization."""
    fusion = AdaptiveFusion(num_modalities=3)
    assert fusion.num_modalities == 3
    assert all(fusion.reliability_scores == 1.0)


def test_adaptive_fusion_update_reliability():
    """Test updating reliability scores."""
    fusion = AdaptiveFusion(num_modalities=3)
    fusion.update_reliability(0, 0.95)
    assert fusion.reliability_scores[0] == 0.95


def test_adaptive_fusion_fuse():
    """Test adaptive fusion."""
    fusion = AdaptiveFusion(num_modalities=3)
    fusion.reliability_scores = np.array([0.9, 0.7, 0.8])
    
    predictions = [
        np.array([0.8]),
        np.array([0.7]),
        np.array([0.9])
    ]
    result = fusion.fuse(predictions)
    assert result is not None


def test_multi_modal_input_with_all_modalities():
    """Test multi-modal input with all modalities."""
    telemetry = np.random.rand(100, 10)
    audio = np.random.rand(50, 20)
    video = np.random.rand(16, 64, 64, 3)
    
    input_data = MultiModalInput(
        telemetry=telemetry,
        audio=audio,
        video=video,
        text="Test description"
    )
    assert input_data.telemetry is not None
    assert input_data.audio is not None
    assert input_data.video is not None
    assert input_data.text == "Test description"


def test_late_fusion_single_modality():
    """Test late fusion with single modality."""
    fusion = LateFusion(num_modalities=1)
    predictions = [np.array([0.5])]
    result = fusion.fuse(predictions)
    assert result[0] == 0.5


def test_early_fusion_single_feature():
    """Test early fusion with single feature."""
    fusion = EarlyFusion()
    features = [np.array([[0.1, 0.2, 0.3]])]
    result = fusion.fuse(features)
    assert result.shape == (1, 3)
