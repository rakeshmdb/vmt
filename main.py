import time
import argparse
import os
import re
import json
import oracledb
import pymongo
import sys
import logging
import ast
from dotenv import load_dotenv
# from scripts.har2mmd import HARConverter
from scripts.python2java import PythontoJava
from plsqltojava import PLSQLtoJava

load_dotenv()

dsn_tns = oracledb.makedsn(os.environ['ORACLE_HOST'], os.environ['ORACLE_PORT'], service_name=os.environ['ORACLE_SERVICE_NAME'])
connection = oracledb.connect(user=os.environ['ORACLE_USERNAME'], password=os.environ['ORACLE_PASSWORD'], dsn=dsn_tns)

def read_view_names_from_file(file_path):
    with open(file_path, 'r') as file:
        view_names = [line.strip() for line in file if line.strip()]
    return view_names

def read_trigger_names_from_file(file_path):
    with open(file_path, 'r') as file:
        trigger_names = [line.strip() for line in file if line.strip()]
    return trigger_names

def extract_mql_code(markdown_content):
    """
    Extract the MQL code block from the markdown content.
    Handles both `javascript` and `mongodb` code blocks.
    """
    mql_code_match = re.search(r'```(javascript|mongodb|sql)\s*(.*?)\s*```', markdown_content, re.DOTALL)
    if not mql_code_match:
        raise ValueError("No MQL code block found in the markdown file.")

    mql_code = mql_code_match.group(2).strip()
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

def fetch_view_definition(connection, view_name):
    try:
        cursor = connection.cursor()
        sql_query = f"""
        SELECT TEXT
        FROM USER_VIEWS
        WHERE VIEW_NAME = '{view_name.upper()}'
        """

        cursor.execute(sql_query)
        view_definition = cursor.fetchone()
        cursor.close()

        if view_definition:
            return view_definition[0]
        else:
            print(f"View {view_name} not found.")
            return None
    except oracledb.DatabaseError as e:
        print(f"Error fetching view {view_name}: {e}")
        return None

def fetch_trigger_definition(connection, trigger_name):
    try:
        cursor = connection.cursor()
        
        # Fetch the trigger details
        sql_query = f"""
        SELECT TRIGGER_NAME, TRIGGER_TYPE, TRIGGERING_EVENT, TABLE_NAME, STATUS
        FROM USER_TRIGGERS
        WHERE TRIGGER_NAME = '{trigger_name.upper()}'
        """
        cursor.execute(sql_query)
        trigger_details = cursor.fetchone()

        if not trigger_details:
            print(f"Trigger {trigger_name} not found.")
            return None

        # Fetch the trigger source code
        sql_query = f"""
        SELECT TEXT
        FROM USER_SOURCE
        WHERE NAME = '{trigger_name.upper()}' AND TYPE = 'TRIGGER'
        ORDER BY LINE
        """
        cursor.execute(sql_query)
        trigger_source = cursor.fetchall()
        cursor.close()

        if trigger_source:
            trigger_definition = ''.join([line[0] for line in trigger_source])
            return {
                'trigger_details': {
                    'trigger_name': trigger_details[0],
                    'trigger_type': trigger_details[1],
                    'triggering_event': trigger_details[2],
                    'table_name': trigger_details[3],
                    'status': trigger_details[4]
                },
                'trigger_source': trigger_definition
            }
        else:
            print(f"Source code for trigger {trigger_name} not found.")
            return None
    except oracledb.DatabaseError as e:
        print(f"Error fetching trigger {trigger_name}: {e}")
        return None
 
    
def process_views(view_names, intent):
    try:
        for view_name in view_names:
            if(intent != "triggers"):
                print(f"Processing view: {view_name}")
                view_definition = fetch_view_definition(connection, view_name)

                if view_definition:
                    file_name = f"{view_name}_definition.sql"
                    file_path = os.path.join(os.getcwd(), file_name)
                    with open(file_path, "w") as file:
                        file.write(view_definition)
                    print(f"View definition written to {file_path}")
            else:
                print(f"Processing view: {view_name}")
                view_definition = fetch_trigger_definition(connection, view_name)

                if view_definition:
                    file_name = f"{view_name}_definition.sql"
                    file_path = os.path.join(os.getcwd(), file_name)
                    with open(file_path, "w") as file:
                        file.write(view_definition['trigger_source'])
                    print(f"View definition written to {file_path}")

            genai_obj = PLSQLtoJava()
            genai_obj.plsqlToJava(view_name, intent)
    except oracledb.DatabaseError as e:
        print(f"Error: {e}")
    finally:
        connection.close()

def rename_variables(pipeline):
    """
    Rename variables in the pipeline to ensure they start with a valid character.
    """
    def rename_var(var):
        if var.startswith('$'):
            return '$' + var[1].lower() + var[2:]
        return var

    def rename_dict(d):
        if isinstance(d, dict):
            return {rename_var(k): rename_dict(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [rename_dict(i) for i in d]
        else:
            return d

    return rename_dict(pipeline)

def remove_comments(command):
    """
    Remove comments from the command string.
    """
    command = re.sub(r'//.*', '', command)  # Remove single-line comments
    command = re.sub(r'/\*.*?\*/', '', command, flags=re.DOTALL)  # Remove multi-line comments
    return command

# def execute_mql_code(mql_code, db):
#     """
#     Execute the MQL code in the MongoDB database.
#     """
#     try:
#         # Assuming MQL code is a series of MongoDB commands in JavaScript format
#         commands = mql_code
#         # print(commands)
#         exec_command(commands, db)
#         print("MQL code executed successfully.")
#     except Exception as e:
#         print(f"Error executing MQL code: {e}")

def execute_mql_code(mql_code, db):
    """
    Execute the MQL code in the MongoDB database.
    """
    try:
        commands = mql_code.split(';')
        for command in commands:
            if command.strip():
                exec_command(command.strip(), db)
        print("MQL code executed successfully.")
    except Exception as e:
        print(f"Error executing MQL code: {e}")

def exec_command(command, db):
    """
    Parse and execute a single MongoDB command.
    """
    try:
        # print(f"Executing command: {command}")  # Debugging line
        command = remove_comments(command)

        if command.startswith('db.createCollection'):
            collection_name = re.search(r'db.createCollection\("([^"]+)"\)', command).group(1)
            
            if collection_name in db.list_collection_names():
                print(f"Collection {collection_name} already exists. Skipping creation.")
            else:
                db.create_collection(collection_name)
                print(f"Collection {collection_name} created successfully.")
        elif command.startswith('db.createView'):
            match = re.search(r'db.createView\(\s*"([^"]+)",\s*"([^"]+)",\s*(\[.*\])\s*\)', command, re.DOTALL)
            # # match = re.search(r'db.createView\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*(\[.*\])\s*\)', command, re.DOTALL)
            # # match = re.search(r'db.createView\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*(\[[\s\S]*\])\s*\)', command, re.DOTALL)
            # match = re.search(r'db.createView\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*(\[[\s\S]*?\])\s*\)', command, re.DOTALL)

            if match:
                view_name = match.group(1)
                source_collection = match.group(2)
                pipeline_str = match.group(3)

                # Replace JavaScript booleans with Python booleans
                pipeline_str = pipeline_str.replace('true', 'true').replace('false', 'false')
                # pipeline = ast.literal_eval(pipeline_str)
                # print(pipeline_str)
                pipeline = json.loads(pipeline_str)

                # Rename variables in the pipeline
                pipeline = rename_variables(pipeline)
                # print(pipeline)
                if view_name in db.list_collection_names():
                    print(f"View {view_name} already exists. Skipping creation.")
                else:
                    # db.create_collection(view_name, viewOn=source_collection, pipeline=eval(pipeline))
                    print(f"View {view_name} created successfully.")
                    db.command({
                        "create": view_name,
                        "viewOn": source_collection,
                        "pipeline": pipeline
                    })
                    print(f"View {view_name} created successfully.")
        else:
            raise ValueError(f"Unsupported command: {command}")
    except Exception as e:
        print(f"Error executing command '{command}': {e}")

def get_view_info(client, database_name, views_list):
    db = client[database_name]
    views_info = {}
    existing_collections = db.list_collection_names()

    collections = db.list_collections()
    for collection in collections:
        if collection["name"] in views_list:
            if collection["type"] == "view":
                views_info[collection["name"]] = {
                    "viewOn": collection["options"]["viewOn"],
                    "pipeline": collection["options"].get("pipeline", [])
                }
            else:
                views_info[collection["name"]] = None

    return views_info, existing_collections

def check_views_and_collections_existence(client, database_name, views_info, existing_collections):
    existing_collections_lower = [collection.lower() for collection in existing_collections] #lower
    
    for view, info in views_info.items():
        if info is not None:
            print(f"View '{view}' exists in the database.")
            print(f"  - View on: {info['viewOn']}")
            view_on_lower = info['viewOn'].lower()
            if view_on_lower in existing_collections_lower:
                print(f"  - Underlying collection '{info['viewOn']}' exists in the database.")
            else:
                print(f"  - Underlying collection '{info['viewOn']}' does not exist in the database.")
                
            for stage in info["pipeline"]:
                if "$lookup" in stage:
                    lookup_collection = stage['$lookup']['from']
                    lookup_collection_lower = lookup_collection.lower()
                    if lookup_collection_lower in existing_collections_lower:
                        print(f"  - Lookup from collection '{lookup_collection}' exists in the database.")
                    else:
                        print(f"  - Lookup from collection '{lookup_collection}' does not exist in the database.")
        else:
            print(f"View '{view}' does not exist in the database.")

def get_oracle_view_count(connection, view_name):
    cursor = connection.cursor()
    query = f"SELECT COUNT(*) FROM {view_name}"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def get_mongo_view_count(client, db_name, collection_name):
    db = client[db_name]
    collection = db[collection_name]
    return collection.count_documents({})

def compare_view_counts(oracle_conn, mongo_client, oracle_views, mongo_db_name):
    for view_name in oracle_views:
        oracle_count = get_oracle_view_count(oracle_conn, view_name)
        mongo_count = get_mongo_view_count(mongo_client, mongo_db_name, view_name)

        print(f"View: {view_name}")
        print(f"Oracle Count: {oracle_count}")
        print(f"MongoDB Count: {mongo_count}")

        if oracle_count == mongo_count:
            print("Counts match.\n")
        else:
            print("Counts do not match.\n")


if __name__ == "__main__":

    load_dotenv()

    view_names = read_view_names_from_file('input.txt')

    # Path to the oracle triggers
    triggers_names = read_trigger_names_from_file('trigger.txt')

  # Add your view names here
    markdown_file_path = r'C:\code\vmt-main\convert_code_prompt_SQLtoJava_code.md'

    output_file_path = 'extracted_mql_code.js'
    client = pymongo.MongoClient(os.environ['MONGODB_CONNECTION_URI'])  # Update with your MongoDB connection string
    db = client[os.environ['MONGODB_DB_NAME']]
    db_name = os.environ['MONGODB_DB_NAME']

    parser = argparse.ArgumentParser(description="Tools for genai module")
    start_time = time.time()
    parser.add_argument("--intent", type=str, help="intent of the script")
    args = parser.parse_args()

    if args.intent == "viewValidation":
        compare_view_counts(connection, client, view_names, db_name)
        connection.close()

    if args.intent == "viewCollectionList":
        views_info, existing_collections = get_view_info(client, db_name, view_names)
        check_views_and_collections_existence(client, db_name, views_info, existing_collections)

    if args.intent == "vmt":
        print("vmt")
        process_views(view_names, 'views')

        try:
            for view_name in view_names:
                markdown_f_path = os.path.join(os.getcwd(), f'convert_{view_name}_code.md')
                output_file_path = 'extracted_'+view_name+'_code.js'
                with open(markdown_f_path, 'r') as file:
                    markdown_content = file.read()

                mql_code = extract_mql_code(markdown_content)
                save_mql_to_file(mql_code, output_file_path)
                # print(mql_code)
                execute_mql_code(mql_code, db)
        except FileNotFoundError:
            print(f"File {markdown_f_path} not found.")
            exit(1)

    if args.intent == "tmt":
        print("tmt")
        process_views(triggers_names, 'triggers')

    # if args.intent == "vmtExecution":
    #     try:
    #         for view_name in view_names:
    #             markdown_f_path = os.path.join(os.getcwd(), f'convert_{view_name}_code.md')
    #             output_file_path = 'extracted_'+view_name+'_code.js'
    #             with open(markdown_f_path, 'r') as file:
    #                 markdown_content = file.read()

    #             mql_code = extract_mql_code(markdown_content)
    #             save_mql_to_file(mql_code, output_file_path)
    #             # print(mql_code)
    #             execute_mql_code(mql_code, db)
    #     except FileNotFoundError:
    #         print(f"File {markdown_f_path} not found.")
    #         exit(1)        

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
            current_dir = os.getcwd()

            sql_file_path = os.path.join(current_dir, 'sample-sql1.sql')
            fields = extract_fields_from_sql(sql_file_path)
            java_code = add_project_stage_to_java(java_code, fields)

        # Save the Java code to a new file
        save_java_file(java_code, 'output.java')
        