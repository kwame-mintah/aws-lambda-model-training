import io
from unittest.mock import Mock

import botocore
import sagemaker
from botocore.stub import Stubber, ANY
from sagemaker import Session

from example_responses import (
    example_get_put_object,
    example_s3_event,
)
from model_training import (
    lambda_handler,
    upload_to_output_bucket,
    start_sagemaker_training_job,
)


def _test_lambda():
    event = example_s3_event()
    result = lambda_handler(event, None)
    assert result["Records"][0]["eventName"] == "ObjectCreated:Put"


def test_upload_to_output_bucket():
    s3_client = botocore.session.get_session().create_client("s3")
    stubber = Stubber(s3_client)
    expected_params = {"Body": ANY, "Bucket": ANY, "Key": ANY, "Tagging": ANY}
    stubber.add_response("put_object", example_get_put_object(), expected_params)
    file_obj = io.BytesIO()

    with stubber:
        assert (
            upload_to_output_bucket(file_obj, "LOCAL_TEST_FILENAME", s3_client) is None
        )


def test_start_sagemaker_training_job():
    # Mock Sagemaker library
    sagemaker.image_uris.retrieve = Mock()
    sagemaker.image_uris.retrieve.return_value = (
        "123456789012.dkr.ecr.eu-west-2.amazonaws.com/xgboost:latest"
    )

    sagemaker.inputs.TrainingInput = Mock()
    sagemaker.inputs.TrainingInput.return_value = None

    sagemaker.Session = Mock()
    sagemaker.Session.return_value = {
        "boto_session": Session,
        "boto_region_name": "eu-west-2",
    }

    # Mock  Estimator object
    Estimator = Mock()

    sagemaker.estimator.Estimator = Mock()
    sagemaker.estimator.Estimator.return_value = Estimator

    sagemaker.estimator.Estimator.set_hyperparameters = Mock()
    sagemaker.estimator.Estimator.set_hyperparameters().return_value = None

    sagemaker.estimator.Estimator.fit = Mock()
    sagemaker.estimator.Estimator.fit.return_value = None

    assert (
        start_sagemaker_training_job(
            region="eu-west-2", framework="xgboost", version="latest"
        )
        is None
    )
