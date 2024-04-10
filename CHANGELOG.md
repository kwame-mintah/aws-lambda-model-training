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
