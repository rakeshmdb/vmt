import os
from utils.file_helper import Helper
from utils.logger_util import LoggerUtility
from awsbedrockservice import AWSBedrockService

class PLSQLtoJava:
    file_helper_obj = Helper()
    aws_bedrock_serv_obj = AWSBedrockService()
    
    expected_path = r"C:\code\vmt-main\mdb.json"
    expected_trigger_path = r"C:\code\vmt-main\trigger.java"
    # logger = LoggerUtility.setup_logger("PLSQLtoJava")  
    
    def plsqlToJava(self, view_name, intent):
        messages = []
        file_path = f"C:\\code\\vmt-main\\{view_name}_definition.sql"
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
        PROMPTS_DIR = os.path.join(ROOT_DIR, r"vmt-main\prompts")
        code = self.file_helper_obj.read_file(file_path)
        expected = self.file_helper_obj.read_file(self.expected_path)
        trigger_expected = self.file_helper_obj.read_file(self.expected_trigger_path)

        if(intent != 'triggers'):
            prompt_data = {
                "source_framework": "sql",
                "target_framework": "mql",
                "target_database": "MongoDB aggregation",
                "view_name": view_name,
                "source_code": code,
                "expected_output": expected,
            }

            CONVERT_CODE = {
                "prompt_path": os.path.join(PROMPTS_DIR, "convert_code_prompt"),
                "function_path": os.path.join(PROMPTS_DIR, "list_framework_changes_function.json"),
                "required_vars": ['source_code'],
            }
        else:
            prompt_data = {
                "source_framework": "oracle trigger",
                "target_framework": "change stream spring boot java",
                "target_database": "MongoDB aggregation",
                "trigger_name": view_name,
                "source_code": code,
                "trigger_expected_output": trigger_expected,
            }
            
            CONVERT_CODE = {
                "prompt_path": os.path.join(PROMPTS_DIR, "convert_triggers_prompt"),
                "function_path": os.path.join(PROMPTS_DIR, "list_framework_changes_function.json"),
                "required_vars": ['source_code'],
            }

        prompt = self.file_helper_obj.build_prompt(CONVERT_CODE, prompt_data)
        messages.append({"role": "user", "content": prompt})
        target_code = self.aws_bedrock_serv_obj.do_completion(messages)
        # print(target_code)
        self.file_helper_obj.save_analysis_report(str(target_code), "convert_"+str(view_name)+"_code.md")
        
        return True
