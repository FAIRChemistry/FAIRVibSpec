import pytest

from fairvibspec.core.fairvibspec import FAIRVibSpec as FAIRVibSpecRoot
from fairvibspec.core.main import FAIRVibSpec


def test_fairvibspec_init():
    fairvibspec = FAIRVibSpec()
    assert fairvibspec.data_model is not None


def test_fairvibspec_data_model_setter():
    fairvibspec = FAIRVibSpec()
    del fairvibspec.data_model
    # Test setting a valid data model
    fairvibspec.data_model = FAIRVibSpecRoot()
    assert fairvibspec.data_model is not None
    assert fairvibspec.data_model.datetime_created is not None
    assert fairvibspec.data_model.datetime_modified is not None
    # Test setting None
    fairvibspec.data_model = None
    assert fairvibspec.data_model is None


def test_failed_fairvibspec_data_model_setter():
    fairvibspec = FAIRVibSpec()
    with pytest.raises(ValueError):
        fairvibspec.data_model = "not a FAIRVibSpecRoot object"


def test_fairvibspec_data_model_deleter():
    fairvibspec = FAIRVibSpec()
    del fairvibspec.data_model
    assert fairvibspec.data_model is None
