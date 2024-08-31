from dotenv import load_dotenv
import os
import httpx
import json
import openai


class OpenAIService:
    load_dotenv()
    GTP4_32K = os.environ["AZURE_OPENAI_API_COMPLETIONS_MODEL_LARGE"]

    openai = openai.AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ["API_VERSION"],
        http_client=httpx.Client(verify=False),
    )
    
    def do_function_completion(self,messages, function, model=GTP4_32K, temperature=0, top_p=0):

        response = self.openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            functions=[function],
            function_call="auto",
        )

        json_output = response.choices[0].message.function_call.arguments
        data = json.loads(json_output, strict=False)
        return data


    def do_completion(self,messages, model=GTP4_32K, temperature=0, top_p=0):

        response = self.openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
        )

        return response.choices[0].message.content