import os
import boto3
import json
from dotenv import load_dotenv
from botocore.config import Config

class AWSBedrockService:
    load_dotenv()
    
    def __init__(self):
        self.config = Config(read_timeout=172324)  # Configure read timeout
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=os.environ['AWS_REGION'],
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            aws_session_token=os.environ['AWS_SESSION_TOKEN'],
            config=self.config
        )
        self.model_id = os.environ['AWS_BEDROCK_MODEL_ID']  #  Model ID from environment variables
        self.anthropic_version = "bedrock-2023-05-31"

    def do_function_completion(self, messages, function, temperature=0, top_p=0):
        body = {
            'prompt': messages[0]['content'],
            'max_tokens_to_sample': 1000,
            'temperature': temperature,
            'top_p': top_p,
            'function_call': 'auto',
            'functions': [function],
        }
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)  # Convert dictionary to JSON string
        )

        json_output = response['output']
        data = json.loads(json_output, strict=False)
        return data

    def do_completion(self, messages, temperature=0, top_p=0):
        # body = {
        #     'prompt': messages[0]['content'],
        #     'max_tokens_to_sample': 1000,
        #     'temperature': temperature,
        #     'top_p': top_p,
        # }
        body = json.dumps({
            "max_tokens": 10000,
            'temperature': temperature,
            'top_p': top_p,
            "messages": [{"role": "user", "content": messages[0]['content']}],
            "anthropic_version": self.anthropic_version
        })

        # response = self.client.invoke_model(
        #     modelId=self.model_id,
        #     body=json.dumps(body)  # Convert dictionary to JSON string
        # )

        # # print json.loads(response["body"].read()
        # return json.loads(response["body"].read())["completion"]
        response = self.client.invoke_model(body=body, modelId=self.model_id)
 
        response_body = json.loads(response.get("body").read())
        return response_body.get("content")[0]["text"]
