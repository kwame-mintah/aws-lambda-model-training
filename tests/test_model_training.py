import io

import botocore
from botocore.stub import Stubber, ANY

from model_training import lambda_handler, upload_to_output_bucket
from example_responses import (
    example_get_put_object,
    example_s3_event,
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
