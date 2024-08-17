import io
import logging
import os  # For manipulating filepath names
from datetime import datetime
from typing import Any

import boto3
import numpy as np  # For matrix operations and numerical processing
import pandas as pd  # For munging tabular data
import sagemaker

from models import S3Record

# The AWS region
aws_region = os.environ.get("AWS_REGION", "eu-west-2")

# Configure S3 client
s3_client = boto3.client(service_name="s3", region_name=aws_region)

# Configure logging
logger = logging.getLogger("model-training")
logger.setLevel(logging.INFO)

# The environment the lambda is currently deployed in
SERVERLESS_ENVIRONMENT = os.environ.get("SERVERLESS_ENVIRONMENT")

# Filepath formatting when uploading to S3 bucket
training_output_path_dir = "automl/%s/training" % str(
    datetime.now().strftime("%Y-%m-%d")
)
training_file_name = "/train/train_%s.csv" % str(datetime.now().strftime("%H_%M_%S"))
validation_file_name = "/validation/validation_%s.csv" % str(
    datetime.now().strftime("%H_%M_%S")
)
testing_file_name = "/testing/test_%s.csv" % str(datetime.now().strftime("%H_%M_%S"))

ssm_preprocessed_output_bucket_name = (
    "mlops-eu-west-2-%s-automl-data" % SERVERLESS_ENVIRONMENT
)
ssm_model_output_bucket_name = (
    "mlops-eu-west-2-%s-model-output" % SERVERLESS_ENVIRONMENT
)

# Bucket name containing training data
s3_bucket_interpolation = "s3://{}/{}"


def lambda_handler(event, context):
    """
    Split preprocessed data into training and validation for training job.

    :param event: S3 Event
    :param context:
    :return:
    """
    s3_record = S3Record(event=event)
    logger.info(
        "Received event: %s on bucket: %s for object: %s",
        s3_record.event_name,
        s3_record.bucket_name,
        s3_record.object_key,
    )

    # Check the object is not something previously created by training lambda.
    if "training" in s3_record.object_key:
        logger.info(
            "Will not process object: %s as this was previously created "
            "for training",
            s3_record.object_key,
        )
        return

    # Read CSV file from S3 Bucket
    data = pd.read_csv(
        filepath_or_buffer="s3://" + s3_record.bucket_name + "/" + s3_record.object_key
    )

    # Randomly sort the data then split out first 70%, second 20%, and last 10%
    # Ignore warning message output when running `np.split()` see GitHub issue:
    # https://github.com/numpy/numpy/issues/24889
    train_data, validation_data, test_data = np.split(
        ary=data.sample(frac=1, random_state=1729),
        indices_or_sections=[int(0.7 * len(data)), int(0.9 * len(data))],
    )
    logger.info("Finished splitting data into training, validation and testing")

    # Create readable file-like object for training and validation comma-separated values (csv)
    file_obj_training = io.BytesIO()
    file_obj_validation = io.BytesIO()
    file_obj_test = io.BytesIO()

    # Get output bucket name from parameter store for csvs
    preprocessed_output_bucket_name = get_parameter_store_value(
        name=ssm_preprocessed_output_bucket_name
    )

    # Concatenate pandas objects and write to csv file
    pd.concat(
        [train_data["y_yes"], train_data.drop(["y_no", "y_yes"], axis=1)], axis=1
    ).to_csv(path_or_buf=file_obj_training, index=False, header=False)
    file_obj_training.seek(0)
    pd.concat(
        [validation_data["y_yes"], validation_data.drop(["y_no", "y_yes"], axis=1)],
        axis=1,
    ).to_csv(path_or_buf=file_obj_validation, index=False, header=False)
    file_obj_validation.seek(0)
    pd.concat([test_data]).to_csv(path_or_buf=file_obj_test)
    file_obj_test.seek(0)

    # Upload the file to S3 for training
    upload_to_output_bucket(
        bucket_name=preprocessed_output_bucket_name,
        file_obj=file_obj_training,
        key=training_output_path_dir + training_file_name,
    )
    upload_to_output_bucket(
        bucket_name=preprocessed_output_bucket_name,
        file_obj=file_obj_validation,
        key=training_output_path_dir + validation_file_name,
    )

    # Upload test data to S3 for testing
    upload_to_output_bucket(
        bucket_name=preprocessed_output_bucket_name,
        file_obj=file_obj_test,
        key=training_output_path_dir + testing_file_name,
    )

    logger.info(
        "Finished uploading train: %s, validation: %s and test: %s files",
        training_file_name,
        validation_file_name,
        testing_file_name,
    )

    # Get model output bucket name
    model_bucket_name = get_parameter_store_value(name=ssm_model_output_bucket_name)

    # Start SageMaker Training job
    start_sagemaker_training_job(
        region=aws_region,
        framework="xgboost",
        version="latest",
        bucket_name=preprocessed_output_bucket_name,
        model_output_bucket_name=model_bucket_name,
    )

    logger.info(
        "Training job started, model output can be found in bucket: %s",
        model_bucket_name,
    )
    return event


def upload_to_output_bucket(
    bucket_name: str, file_obj: io.BytesIO, key: str, client: Any = s3_client
) -> None:
    """
    Upload the file object to the output s3 bucket.

    :param bucket_name: The bucket name to upload the object.
    :param client: boto3 client configured to use s3
    :param file_obj: The DataFrame as a csv
    :param key: The full path to the object destination
    """
    client.put_object(
        Body=file_obj,
        Bucket=bucket_name,
        Tagging="ProcessedTime=%s" % str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        Key=key,
    )


def start_sagemaker_training_job(
    region: str,
    framework: str,
    version: str,
    bucket_name: str,
    model_output_bucket_name: str,
    sagemaker_role: str = "SageMakerExecutionRole",
    instance_count: int = 1,
    instance_type: str = "ml.m4.xlarge",
) -> None:
    """
    Start a training job within AWS SageMaker, using training and validation data previously
    uploaded to S3 buckets. Ensure a SageMaker role is available and has permission to
    start a training job and access to bucket(s).

    :param region: The AWS region.
    :param framework: The name of the framework or algorithm.
    :param version: The framework or algorithm version.
    :param bucket_name: The bucket containing the training / validation data.
    :param model_output_bucket_name: The S3 bucket name for saving the training result.
    :param sagemaker_role: An AWS IAM role (either name or full ARN).
    :param instance_count: Number of Amazon EC2 instances to use for training.
    :param instance_type: Type of EC2 instance to use for training.
    """

    # Specify the algorithm container
    # https://sagemaker.readthedocs.io/en/stable/api/utility/image_uris.html#sagemaker.image_uris.retrieve
    container = sagemaker.image_uris.retrieve(
        region=region, framework=framework, version=version
    )

    # Create a definition for input data used by an SageMaker training job.
    # https://sagemaker.readthedocs.io/en/stable/api/utility/inputs.html
    s3_input_train = sagemaker.inputs.TrainingInput(
        s3_data=s3_bucket_interpolation.format(
            bucket_name,
            training_output_path_dir + training_file_name,
        ),
        content_type="csv",
    )

    s3_input_validation = sagemaker.inputs.TrainingInput(
        s3_data=s3_bucket_interpolation.format(
            bucket_name,
            training_output_path_dir + validation_file_name,
        ),
        content_type="csv",
    )

    sagemaker_session = sagemaker.Session()

    # Documentation on available options.
    # https://sagemaker.readthedocs.io/en/stable/api/training/estimators.html#sagemaker.estimator.Estimator
    xgb = sagemaker.estimator.Estimator(
        image_uri=container,
        role=sagemaker_role,
        instance_count=instance_count,
        instance_type=instance_type,
        output_path="s3://{}/{}/output".format(
            model_output_bucket_name, str(datetime.now().strftime("%Y-%m-%d"))
        ),
        tags=[
            {"Key": "Project", "Value": "MLOps"},
            {"Key": "Region", "Value": aws_region},
            {
                "Key": "Testing",
                "Value": s3_bucket_interpolation.format(
                    bucket_name,
                    training_output_path_dir + testing_file_name,
                ),
            },
        ],
        sagemaker_session=sagemaker_session,
    )

    # Sets the hyperparameter dictionary to use for training.
    # https://sagemaker.readthedocs.io/en/stable/api/training/estimators.html#sagemaker.estimator.Estimator.set_hyperparameters
    xgb.set_hyperparameters(
        max_depth=5,
        eta=0.2,
        gamma=4,
        min_child_weight=6,
        subsample=0.8,
        silent=0,
        objective="binary:logistic",
        num_round=100,
    )

    # Don't wait for training job to finish, lambda limit is max 15 minutes.
    # https://sagemaker.readthedocs.io/en/stable/api/training/estimators.html#sagemaker.estimator.EstimatorBase.fit
    xgb.fit(
        inputs={"train": s3_input_train, "validation": s3_input_validation}, wait=False
    )


def get_parameter_store_value(
    name: str, client: Any = boto3.client(service_name="ssm", region_name=aws_region)
) -> str:
    """
    Get a parameter store value from AWS.

    :param name: The name or Amazon Resource Name (ARN) of the parameter that you want to query
    :param client: boto3 client configured to use ssm
    :return: value
    """
    logger.info("Retrieving %s from parameter store", name)
    return client.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]
