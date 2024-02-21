import io
import logging
import os  # For manipulating filepath names
from datetime import datetime
from typing import Any

import boto3
import numpy as np  # For matrix operations and numerical processing
import pandas as pd  # For munging tabular data

from models import S3Record

# Configure S3 client
s3_client = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "eu-west-2"))

# Configure logging
logger = logging.getLogger("model-training")
logger.setLevel(logging.INFO)

# The model output bucket name
MODEL_OUTPUT_BUCKET_NAME = os.environ.get("MODEL_OUTPUT_BUCKET_NAME")

# The output bucket name
PREPROCESSED_OUTPUT_BUCKET_NAME = os.environ.get("PREPROCESSED_OUTPUT_BUCKET_NAME")

# Filepath formatting when uploading to S3 bucket
training_output_path_dir = "training/%s" % str(datetime.now().strftime("%Y-%m-%d"))
training_file_name = "/training_%s.csv" % str(datetime.now().strftime("%H_%M_%S"))
validation_file_name = "/validation_%s.csv" % str(datetime.now().strftime("%H_%M_%S"))


def lambda_handler(event, context):
    s3_record = S3Record(event)
    logger.info(
        "Received event: %s on bucket: %s for object: %s",
        s3_record.event_name,
        s3_record.bucket_name,
        s3_record.object_key,
    )
    # Read CSV file for S3 Bucket
    data = pd.read_csv("s3://" + s3_record.bucket_name + "/" + s3_record.object_key)
    # Make sure we can see all the columns
    pd.set_option("display.max_columns", 500)
    # Keep the output on one page
    pd.set_option("display.max_rows", 20)
    model_data = pd.get_dummies(data, dtype=float)
    # Randomly sort the data then split out first 70%, second 20%, and last 10%
    train_data, validation_data, test_data = np.split(
        model_data.sample(frac=1, random_state=1729),
        [int(0.7 * len(model_data)), int(0.9 * len(model_data))],
    )
    # Create readable file-like object for training and validation comma-separated values (csv)
    file_obj_training = io.BytesIO()
    file_obj_validation = io.BytesIO()
    # Concatenate pandas objects and write to csv file.
    pd.concat(
        [train_data["y_yes"], train_data.drop(["y_no", "y_yes"], axis=1)], axis=1
    ).to_csv(file_obj_training, index=False, header=False)
    file_obj_training.seek(0)
    pd.concat(
        [validation_data["y_yes"], validation_data.drop(["y_no", "y_yes"], axis=1)],
        axis=1,
    ).to_csv(file_obj_validation, index=False, header=False)
    file_obj_validation.seek(0)

    # Copy the file to S3 for training to pick up
    upload_to_output_bucket(
        file_obj_training, training_output_path_dir + training_file_name, s3_client
    )
    upload_to_output_bucket(
        file_obj_validation, training_output_path_dir + validation_file_name, s3_client
    )

    # Trigger training job ...
    # ....

    return event


def upload_to_output_bucket(file_obj: io.BytesIO, key: str, client: Any = s3_client):
    """
    Upload the file object to the output s3 bucket.

    :param client: boto3 client configured to use s3
    :param file_obj: The DataFrame as a csv
    :param key: The full path to the object destination
    :return:
    """
    client.put_object(
        Body=file_obj,
        Bucket=PREPROCESSED_OUTPUT_BUCKET_NAME,
        Tagging="ProcessedTime=%s" % str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        Key=key,
    )
