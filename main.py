import time
import argparse
import os
import re
import json
from dotenv import load_dotenv
# from scripts.har2mmd import HARConverter
from scripts.python2java import PythontoJava
from plsqltojava import PLSQLtoJava

def extract_mql_code(markdown_content):
    # Extract the MQL code block from the markdown content
    mql_code_match = re.search(r'```javascript\s*(.*?)\s*```', markdown_content, re.DOTALL)
    if not mql_code_match:
        raise ValueError("No MQL code block found in the markdown file.")

    mql_code = mql_code_match.group(1).strip()
    return mql_code

def save_mql_to_file(mql_code, output_file_path):
    with open(output_file_path, 'w') as file:
        file.write(mql_code)
    print(f"MQL code has been written to {output_file_path}")

def convert_mql_to_java(mql_code):
    # Simplify and format the MQL code
    mql_code = mql_code.replace('db.employees.aggregate([', '')
    mql_code = mql_code.rstrip('])')
    
    # Convert each MongoDB aggregation stage to corresponding Java code
    stages = {
        '$lookup': 'Aggregation.lookup',
        '$unwind': 'Aggregation.unwind',
        '$match': 'Aggregation.match',
        '$group': 'Aggregation.groupBy',
        '$sort': 'Aggregation.sort',
        '$project': 'Aggregation.project'
    }
    
    for stage, java_stage in stages.items():
        mql_code = mql_code.replace(stage, java_stage)
    
    # Handle the formatting of MQL stages for Java
    mql_code = re.sub(r'\{\s*([\w\$]+):\s*[^}]+\}', lambda m: f'new Aggregation.Stage({m.group(0)})', mql_code)
    
    # Prepare the Java code
    java_code = f"""
import org.springframework.data.mongodb.core.aggregation.Aggregation;
import org.springframework.data.mongodb.core.query.Criteria;

public class MongoDBQuery {{
    public static Aggregation getAggregation() {{
        return Aggregation.newAggregation(
{mql_code}
        );
    }}
}}
"""
    return java_code

def save_java_file(java_code, output_file_path):
    with open(output_file_path, 'w') as file:
        file.write(java_code)
    print(f"Java code has been written to {output_file_path}")

def check_for_project_stage(mql_code):
    return 'Aggregation.project' in mql_code

def extract_fields_from_sql(sql_file_path):
    # Basic extraction of fields from the SQL SELECT statement
    with open(sql_file_path, 'r') as file:
        sql_content = file.read()
    
    fields = re.findall(r'SELECT\s+(.*?)\s+FROM', sql_content, re.DOTALL)
    if fields:
        field_list = fields[0].split(',')
        field_list = [field.strip() for field in field_list]
        return field_list
    else:
        return []

def add_project_stage_to_java(java_code, fields):
    project_stage = "Aggregation.project: new Aggregation.Stage({\n"
    project_stage += ",\n".join([f'"{field}": 1' for field in fields])
    project_stage += "\n})"
    
    java_code = java_code.replace(");", f",\n{project_stage}\n        );")
    
    return java_code

if __name__ == "__main__":

    load_dotenv()

    # Path to the markdown file
    markdown_file_path = '/Users/rakesh.tripathi/Desktop/Allianz/bedrock-testing/convert_code_prompt_SQLtoJava_code.md'

    output_file_path = 'extracted_mql_code.js'

    parser = argparse.ArgumentParser(description="Tools for genai module")
    start_time = time.time()
    parser.add_argument("--intent", type=str, help="intent of the script")
    args = parser.parse_args()
    
    if args.intent == "HARtoSeq":
        genai_obj = HARConverter()
        genai_obj.parseHARfile()

    if args.intent == "PythonToJava":
        genai_obj = PythontoJava()
        genai_obj.pythonToJava()

    if args.intent == "PythonToPLSQL":
        genai_obj = PLSQLtoJava()
        genai_obj.plsqlToJava()

    if args.intent == "SQLToMDB":

        try:
            with open(markdown_file_path, 'r') as file:
                markdown_content = file.read()
        except FileNotFoundError:
            print(f"File {markdown_file_path} not found.")
            exit(1)

        # Extract MQL code and save it to a new file
        try:
            mql_code = extract_mql_code(markdown_content)
            save_mql_to_file(mql_code, output_file_path)
        except ValueError as e:
            print(f"Error: {e}")
            exit(1)

        # Read the MQL code from the extracted file
        try:
            with open(output_file_path, 'r') as file:
                mql_code = file.read()
        except FileNotFoundError:
            print(f"File {output_file_path} not found.")
            exit(1)
        
        # Convert MQL code to Java
        java_code = convert_mql_to_java(mql_code)

        if not check_for_project_stage(mql_code):
            sql_file_path = '/Users/rakesh.tripathi/Desktop/Allianz/bedrock-testing/sample-sql1.sql'
            fields = extract_fields_from_sql(sql_file_path)
            java_code = add_project_stage_to_java(java_code, fields)

        # Save the Java code to a new file
        save_java_file(java_code, 'output.java')
        