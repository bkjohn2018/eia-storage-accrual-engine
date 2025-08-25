"""Tests for configuration module."""

import pytest
from eia_sa.config import Settings


def test_settings_initialization():
    """Test that settings can be initialized."""
    # This will fail without proper environment setup, but we can test the structure
    with pytest.raises(ValueError):
        # Should fail because EIA_API_KEY is required
        Settings()


def test_estimator_weights_validation():
    """Test estimator weights validation."""
    # Test valid weights
    valid_weights = "0.3,0.2,0.5"
    settings = Settings(eia_api_key="test_key", default_estimator_weights=valid_weights)
    assert settings.estimator_weights_tuple == (0.3, 0.2, 0.5)
    
    # Test invalid weights (don't sum to 1.0)
    with pytest.raises(ValueError):
        Settings(eia_api_key="test_key", default_estimator_weights="0.5,0.5,0.5")
    
    # Test invalid weights (wrong number)
    with pytest.raises(ValueError):
        Settings(eia_api_key="test_key", default_estimator_weights="0.5,0.5")


def test_estimator_weights_dict():
    """Test estimator weights dictionary conversion."""
    settings = Settings(eia_api_key="test_key", default_estimator_weights="0.3,0.2,0.5")
    expected = {
        "method_a": 0.3,
        "method_b": 0.2,
        "method_c": 0.5
    }
    assert settings.estimator_weights_dict == expected
