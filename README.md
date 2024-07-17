# AWS Lambda Model Training

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3121/)
[![🚧 Bump version](https://github.com/kwame-mintah/aws-lambda-model-training/actions/workflows/bump-repository-version.yml/badge.svg)](https://github.com/kwame-mintah/aws-lambda-model-training/actions/workflows/bump-repository-version.yml)
[![🚀 Push Docker image to AWS ECR](https://github.com/kwame-mintah/aws-lambda-model-training/actions/workflows/push-docker-image-to-aws-ecr.yml/badge.svg)](https://github.com/kwame-mintah/aws-lambda-model-training/actions/workflows/push-docker-image-to-aws-ecr.yml)
[![🧹 Run linter](https://github.com/kwame-mintah/aws-lambda-model-training/actions/workflows/run-python-linter.yml/badge.svg)](https://github.com/kwame-mintah/aws-lambda-model-training/actions/workflows/run-python-linter.yml)

A lambda to split pre-processed data into, training and validation then uploaded to an S3 bucket. Training and validation
data uploaded to the bucket will be used when triggering the training job.

This repository does not create the S3 Bucket, this is created via Terraform found here [terraform-aws-machine-learning-pipeline](https://github.com/kwame-mintah/terraform-aws-machine-learning-pipeline).
For more details on the entire flow and how this lambda is deployed, see [aws-automlops-serverless-deployment](https://github.com/kwame-mintah/aws-automlops-serverless-deployment).

# Flowchart

The [diagram below](https://mermaid.js.org/syntax/flowchart.html#flowcharts-basic-syntax) demonstrates what happens when the lambda is trigger, when a new `.csv` object has been uploaded to the S3 Bucket.

```mermaid
graph LR
  S0(Start)
  T1(Dataset pulled from S3 Bucket)
  T2(Random split and sort using Numpy)
  T3[["`70% training data
    20% validation data
    10% test data`"]]
  T4("Upload split data into S3 Bucket as `.csv`")
  T5("Start training job with training and validation data")
  E0(End)

  S0-->T1
  T1-->T2
  T2-->T3
  T3-->T4
  T4-->T5
  T5-->E0
```

## Development

### Dependencies

- [Python](https://www.python.org/downloads/release/python-3121/)
- [Docker for Desktop](https://www.docker.com/products/docker-desktop/)
- [Amazon Web Services](https://aws.amazon.com/?nc2=h_lg)

## Usage

1. Build the docker image locally:

   ```commandline
   docker build --no-cache -t model_training:local .
   ```

2. Run the docker image built:

   ```commandline
   docker run --platform linux/amd64 -p 9000:8080 model_training:local
   ```

3. Send an event to the lambda via curl:
   ```commandline
   curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{<REPLACE_WITH_JSON_BELOW>}'
   ```
   ```json
   {
     "Records": [
       {
         "eventVersion": "2.0",
         "eventSource": "aws:s3",
         "awsRegion": "us-east-1",
         "eventTime": "1970-01-01T00:00:00.000Z",
         "eventName": "ObjectCreated:Put",
         "userIdentity": { "principalId": "EXAMPLE" },
         "requestParameters": { "sourceIPAddress": "127.0.0.1" },
         "responseElements": {
           "x-amz-request-id": "EXAMPLE123456789",
           "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
         },
         "s3": {
           "s3SchemaVersion": "1.0",
           "configurationId": "testConfigRule",
           "bucket": {
             "name": "example-bucket",
             "ownerIdentity": { "principalId": "EXAMPLE" },
             "arn": "arn:aws:s3:::example-bucket"
           },
           "object": {
             "key": "data/example-bank-file.csv",
             "size": 515246,
             "eTag": "0e29c0d99c654bbe83c42097c97743ed",
             "sequencer": "00656A54CA3D69362D"
           }
         }
       }
     ]
   }
   ```

## GitHub Action (CI/CD)

The GitHub Action "🚀 Push Docker image to AWS ECR" will check out the repository and push a docker image to the chosen AWS ECR using
[configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials/tree/v4.0.1/) action. The following repository secrets need to be set:

| Secret             | Description                  |
| ------------------ | ---------------------------- |
| AWS_REGION         | The AWS Region.              |
| AWS_ACCOUNT_ID     | The AWS account ID.          |
| AWS_ECR_REPOSITORY | The AWS ECR repository name. |
