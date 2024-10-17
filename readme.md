# `view-migration-tool`

## Introduction

The `view-migration-tool` is a modernization framework that supports the migration of views from the Oracle to MongoDB view or in spring boot Java layer. Not only the view but also the triggers get convertted into the change stream spring boot java function.

## Features

### 1. Convert Oracle View into the MongoDB view
The framework can modernize oracle views into the mongoDB view and automatically execute the MongoDB view into the database. It uses the AWS Bedrock LLM API and modernize it.

### 2. Convert Oracle View into the Spring boot Java layer
Not only this framework modernize the oracle view into the MongoDB view but also able to modernize the oracle view into the Spring boot java layer.

### 3. Perform validation
Once the oracle views get migrated into the MongoDB view's successfully, it then start performing the validation if both the side (Oracle, MongoDB) has the same count.

### 4. Find missing tables
If the MongoDB view is not working, thene could be several reasons and 1 of the reason is missing tables or dependent views. It finds all the missing views, dependent views, tables and share the list.

## Environment Setup

### Pre-requisites
Ensure you have the following installed on your machine:
- Python 3.9 or higher
- pip

### Dependencies Installation
To install the necessary dependencies, use the following command:
```bash
pip install -r requirements.txt
```

### Environment Variables Setup
To set up your environment variables, copy the `.sample.env` file to `.env`:
```bash
cp .sample.env .env
```
Then, fill in the required values in the `.env` file.

##### AWS Deployment 
- `AWS_REGION`: The AWS region for deployment.
- `AWS_BEDROCK_ANTHROPIC_VERSION`: Version identifier for the AWS Bedrock service.
- `AWS_BEDROCK_MODEL_ID`: Model ID for the AI service on AWS.
- `AWS_ACCESS_KEY_ID`: AWS access key ID.
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key.

## Ideal Business Flow Example
```
The file called input.txt will consists all your list of views and trigger.txt will consists all your list of triggers.
```

#### 1. Convert & execute Oracle view into MongoDB
To read the oracle view directly from the sql developer, modernize it and then execute it into the MongoDB.

```bash
python main.py --intent=vmt
```

#### 2. Validate the MongoDB view
Once Oracle view got migrated, it will validate the count of view on both the side i.e Oracle & MongoDB. 

```bash
python main.py --intent=viewValidation
```

#### 3. Find the missing dependent tables/views
To read the views from the list and find it in the MongoDB if it is already present and then extract all the dependent views/tables and to check if they are already present into the MongoDB

```bash
python main.py --intent=viewCollectionList
```

#### 4. Modernize the Oracle view into the Spring boot Java layer
To read the view from the oracle and modernize it into the spring boot java layer, if incase MongoDB view is not required.

```bash
python main.py --intent=SQLToMDB
```

#### 5. Modernize the Oracle trigger into the Change stream Spring boot Java layer
To read the trigger from the oracle and modernize it into the change stream spring boot java layer, if incase MongoDB trigger is not required.

```bash
python main.py --intent=tmt
```