import pytest

import model_training


@pytest.fixture(autouse=True)
def set_bucket_name(monkeypatch):
    """

    :param monkeypatch:
    """
    monkeypatch.setattr(model_training, "MODEL_OUTPUT_BUCKET_NAME", "unit-test")
    monkeypatch.setattr(model_training, "PREPROCESSED_OUTPUT_BUCKET_NAME", "unit-test")
