import os
from utils.file_helper import Helper
from utils.logger_util import LoggerUtility
from awsbedrockservice import AWSBedrockService

class PLSQLtoJava:
    file_helper_obj = Helper()
    aws_bedrock_serv_obj = AWSBedrockService()
    file_path = "/Users/rakesh.tripathi/Desktop/Allianz/bedrock-testing/sample-sql1.sql"
    expected_path = "/Users/rakesh.tripathi/Desktop/Allianz/bedrock-testing/mdb.json"
    logger = LoggerUtility.setup_logger("PLSQLtoJava")  
    
    def plsqlToJava(self):
        messages = []
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
        PROMPTS_DIR = os.path.join(ROOT_DIR, "prompts")
        code = self.file_helper_obj.read_file(self.file_path)
        expected = self.file_helper_obj.read_file(self.expected_path)
        prompt_data = {
            "source_framework": "sql",
            "target_framework": "mql",
            "target_database": "MongoDB aggregation",
            "source_code": code,
            "expected_output": expected,
        }
        CONVERT_CODE = {
            "prompt_path": os.path.join(PROMPTS_DIR, "convert_code_prompt"),
            "function_path": os.path.join(PROMPTS_DIR, "list_framework_changes_function.json"),
            "required_vars": ['source_code'],
        }

        prompt = self.file_helper_obj.build_prompt(CONVERT_CODE, prompt_data)
        messages.append({"role": "user", "content": prompt})
        target_code = self.aws_bedrock_serv_obj.do_completion(messages)
        # print(target_code)
        self.file_helper_obj.save_analysis_report(str(target_code), "convert_code_prompt_SQLtoJava_code.md")
        
        return True
