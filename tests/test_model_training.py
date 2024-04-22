import io
from unittest.mock import Mock

import botocore
import pandas as pd
import sagemaker
from botocore.stub import Stubber, ANY
from sagemaker import Session

import model_training
from example_responses import (
    example_get_put_object,
    example_s3_event,
)
from model_training import (
    lambda_handler,
    upload_to_output_bucket,
    start_sagemaker_training_job,
)

REGION = "eu-west-2"
LOCAL_TEST_FILENAME = "example-bank-file.csv"


def test_lambda_handler(monkeypatch):
    # Mock reading CSV from S3 Bucket, instead read from local
    data = pd.read_csv(LOCAL_TEST_FILENAME)
    pd.read_csv = Mock()
    pd.read_csv.return_value = data

    def uploaded_to_bucket(bucket_name, file_obj, key):
        """
        Stub uploading to bucket
        """
        return None

    def ssm_value(name):
        """
        Stub parameter store retrieval
        """
        return "value"

    def start_sagemaker_training(
        region, framework, version, bucket_name, model_output_bucket_name
    ):
        """
        Stub uploading to bucket
        """
        return None

    monkeypatch.setattr(model_training, "upload_to_output_bucket", uploaded_to_bucket)

    monkeypatch.setattr(
        model_training, "start_sagemaker_training_job", start_sagemaker_training
    )

    monkeypatch.setattr(model_training, "get_parameter_store_value", ssm_value)

    result = lambda_handler(example_s3_event(), None)
    assert result["Records"][0]["eventName"] == "ObjectCreated:Put"
    assert result["Records"][0]["s3"]["object"]["key"] == "data/" + LOCAL_TEST_FILENAME


def test_upload_to_output_bucket():
    s3_client = botocore.session.get_session().create_client("s3")
    stubber = Stubber(s3_client)
    expected_params = {"Body": ANY, "Bucket": ANY, "Key": ANY, "Tagging": ANY}
    stubber.add_response("put_object", example_get_put_object(), expected_params)
    file_obj = io.BytesIO()

    with stubber:
        assert (
            upload_to_output_bucket(
                bucket_name="bucket",
                file_obj=file_obj,
                key=LOCAL_TEST_FILENAME,
                client=s3_client,
            )
            is None
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
        "boto_region_name": REGION,
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
            region=REGION,
            framework="xgboost",
            version="latest",
            bucket_name="bucket",
            model_output_bucket_name="model-bucket",
        )
        is None
    )
