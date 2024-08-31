from openai import AzureOpenAI
import json
import os
from dotenv import load_dotenv
import httpx
import json
from pymongo import MongoClient
import re
from utils.file_helper import Helper
from openaiservice import OpenAIService
 

class HARConverter:
    helper_obj = Helper()
    openai_serv_obj = OpenAIService()
    file_path = os.environ["FILE_TO_ANALYSE"]

    # CONVERT_HAR_TO_MERMAID = "prompts/convert_har_to_mermaid"

    def parseHARfile(self,api_limit=7,file_path=os.environ["FILE_TO_ANALYSE"]):
        file_path = os.environ["FILE_TO_ANALYSE"]
        CONVERT_HAR_TO_MERMAID = self.helper_obj.read_file("prompts/convert_har_to_mermaid")

        code = self.helper_obj.read_file(file_path)
        code_json = json.loads(code)
        agl_apis = []
        messages =[]
        num_of_requests=0
        for i in code_json["log"]["entries"] :
            request = i["request"]
            response = i["response"]
            uri = request["url"]
            if "aglservice" in uri:
                if num_of_requests < api_limit:
                    api = {}
                    api["request"] = {}
                    api["request"]["method"] = request["method"]
                    api["request"]["url"] = request["url"]
                    api["request"]["queryString"] = request["queryString"]
                    api["response"] = {}
                    api["response"]["status"] = response["status"]
                    #api["response"]["content"] = response["content"]
                    api["response"]["time"] = i["time"]
                    agl_apis.append(api)
                    num_of_requests = num_of_requests+1       
       
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        PROMPTS_DIR = os.path.join(ROOT_DIR, "prompts")
        
        prompt_data = {
            'content': agl_apis,
        }
        EXPLAIN_CHANGES_FROM_DIFF = {
            "prompt_path": os.path.join(PROMPTS_DIR, "convert_har_to_mermaid_prompt"),
            "function_path": os.path.join(PROMPTS_DIR, "convert_har_to_mermaid.json"),
            "required_vars": ['content'],
        }
        prompt = self.helper_obj.build_prompt(EXPLAIN_CHANGES_FROM_DIFF, prompt_data)
        #prompt, function = self.helper_obj.build_prompt_and_function(EXPLAIN_CHANGES_FROM_DIFF, prompt_data)
       
        messages.append({"role": "user", "content": prompt})
        #res_str = self.openai_serv_obj.do_completion(messages)
        res_str = self.openai_serv_obj.do_function_completion(messages)

        print(res_str)
        return True








# load_dotenv()
# GTP4_32K = os.environ["AZURE_OPENAI_API_COMPLETIONS_MODEL_LARGE"]


# openai = AzureOpenAI(
#     api_key=os.environ["AZURE_OPENAI_API_KEY"],
#     azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
#     api_version=os.environ["API_VERSION"],
#     http_client=httpx.Client(verify=False),
# )


# def do_function_completion(prompt, function, model=GTP4_32K, temperature=0, top_p=0):
#     messages = [{"role": "user", "content": prompt}]

#     response = openai.chat.completions.create(
#         model=model,
#         messages=messages,
#         temperature=temperature,
#         top_p=top_p,
#         functions=[function],
#         function_call="auto",
#     )

#     json_output = response.choices[0].message.function_call.arguments
#     data = json.loads(json_output, strict=False)
#     return data


# def do_completion(messages, model=GTP4_32K, temperature=0, top_p=0):

#     response = openai.chat.completions.create(
#         model=model,
#         messages=messages,
#         temperature=temperature,
#         top_p=top_p,
#     )

#     return response.choices[0].message.content


# def save_analysis_report(report, file_name):
#     analysis_report_path = os.path.join(file_name)
#     with open(analysis_report_path, "w") as f:
#         json.dump(report, f, indent=4)


# def read_file(file_path):
#     with open(file_path, "r") as file:
#         the_file = file.read()
#         return the_file

    
# def parseHARfile(api_limit=100,file_path=os.environ["FILE_TO_ANALYSE"]):
#     file_path = os.environ["FILE_TO_ANALYSE"]
    
#     code = read_file(file_path)
#     code_json = json.loads(code)
#     agl_apis = []
#     messages =[]
#     num_of_requests=0
#     for i in code_json["log"]["entries"] :
#         request = i["request"]
#         response = i["response"]
#         uri = request["url"]
#         if "aglservice" in uri:
#             if num_of_requests < api_limit:
#                 api = {}
#                 api["request"] = {}
#                 api["request"]["method"] = request["method"]
#                 api["request"]["url"] = request["url"]
#                 api["request"]["queryString"] = request["queryString"]
#                 api["response"] = {}
#                 api["response"]["status"] = response["status"]
#                 #api["response"]["content"] = response["content"]
#                 api["response"]["time"] = i["time"]
#                 agl_apis.append(api)
#                 num_of_requests = num_of_requests+1
            
#     prompt = "can you create sequence diagram in mermaid based to get api flow diagra based on content as followed with time recorded" + str(agl_apis)
#     messages.append({"role": "user", "content": prompt})
#     res_str = do_completion(messages)
    
#     save_analysis_report(res_str, "api_flow_mermaid.mmd")
#     print(res_str)


# parseHARfile(100,os.environ["FILE_TO_ANALYSE"])



