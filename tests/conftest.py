import pytest

import model_training


@pytest.fixture(autouse=True)
def set_environment_name(monkeypatch):
    monkeypatch.setattr(model_training, "SERVERLESS_ENVIRONMENT", "local")
