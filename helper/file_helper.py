import json

class Helper:
    def read_file(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()
    
    def build_prompt(self, config, data):
        with open(config["prompt_path"], 'r') as file:
            prompt_template = file.read()
        prompt = prompt_template.format(**data)
        return prompt

    def save_analysis_report(self, content, file_name):
        with open(file_name, 'w') as file:
            file.write(content)
