## 0.7.6 (2024-08-17)

### Refactor

- **s3_bucket_interpolation**: reduce code duplication

## 0.7.5 (2024-07-23)

### Refactor

- **lambda_handler**: remove `set_option` from code

## 0.7.4 (2024-07-20)

### Refactor

- **test_data**: ensure test rows have same number of features used for training

## 0.7.3 (2024-07-17)

### Refactor

- **lambda_handler**: use named argument for pandas `to_csv`

## 0.7.2 (2024-05-08)

### Refactor

- **start_sagemaker_training_job**: dont set environment variable in training job

## 0.7.1 (2024-04-27)

### Refactor

- **start_sagemaker_training_job**: include location of test data in environment variables

## 0.7.0 (2024-04-22)

### Feat

- **get_parameter_store_value**: add function to get parameter store values

### Refactor

- **model_training**: no longer use env var for bucket names

## 0.6.1 (2024-04-10)

### Refactor

- **start_sagemaker_training_job**: add tagging to training jobs

## 0.6.0 (2024-04-07)

### Feat

- **pre-commit-config**: update black and commitizen versions

## 0.5.0 (2024-03-18)

### Feat

- **model_training**: upload test data for model evaluation

## 0.4.2 (2024-02-24)

### Refactor

- **lambda_handler**: remove `pre_checks_before_processing` function and only check object key

## 0.4.1 (2024-02-24)

### Refactor

- **pre_checks_before_processing**: move checking before reading to csv format

## 0.4.0 (2024-02-24)

### Feat

- **model_training**: check file has not already been processed

## 0.3.0 (2024-02-24)

### Feat

- **model_training**: change file directory for saving to bucket

## 0.2.0 (2024-02-23)

### Feat

- **model_training**: implement starting sagemaker training job

## 0.1.0 (2024-02-21)

### Feat

- **gitignore**: ignore local files created for development
- **requirements**: add python packages needed for project
- **model_training**: initial training and validation data split prep for training
