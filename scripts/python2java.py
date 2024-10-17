import os
from utils.file_helper import Helper
from utils.logger_util import LoggerUtility
from openaiservice import OpenAIService

class PythontoJava:
    file_helper_obj = Helper()
    openai_serv_obj = OpenAIService()
    file_path = "/Users/rakesh.tripathi/Desktop/Allianz/bedrock-testing/sample-sql1.sql"
    expected_path = "/Users/rakesh.tripathi/Desktop/Allianz/bedrock-testing/mdb.json"
    # logger = LoggerUtility.setup_logger("PythontoJava1")  

    def pythonToJava(self): 
        messages = []
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
    
        PROMPTS_DIR = os.path.join(ROOT_DIR, "prompts")
        code = self.file_helper_obj.read_file(self.file_path)
        prompt_data = {
            "source_framework": "sql",
            "target_framework": "MongoDB aggregation",
            "source_code": code,
            "expected_output": expected,
        }
        EXPLAIN_CHANGES_FROM_DIFF = {
            "prompt_path": os.path.join(PROMPTS_DIR, "list_framework_changes_prompt"),
            "function_path": os.path.join(PROMPTS_DIR, "list_framework_changes_function.json"),
            "required_vars": ['source_code'],
        }
        prompt = self.file_helper_obj.build_prompt(EXPLAIN_CHANGES_FROM_DIFF, prompt_data)
        prompt, afunc = self.file_helper_obj.build_prompt_and_function(EXPLAIN_CHANGES_FROM_DIFF, prompt_data)
        messages.append({"role": "user", "content": prompt})
        self.logger.info("Generating summary for migration")
        recommendations = self.openai_serv_obj.do_function_completion(messages,afunc)        
        self.file_helper_obj.save_analysis_report(recommendations, "list_framework_changes_prompt.txt")
        return True