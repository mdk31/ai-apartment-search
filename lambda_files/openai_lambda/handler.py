import json
import os
import boto3
import boto3
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig
from langchain_openai import ChatOpenAI
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

# TODO: Add tests
# TODO: integrate get_openai with the rest of the function

sfn_client = boto3.client('secretsmanager')
cache_config = SecretCacheConfig()
cache = SecretCache(config=cache_config, client=sfn_client)

STEP_FUNCTION_ARN = os.getenv('STEP_FUNCTION_ARN')

def _load_prompt(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()

def get_openai_key():
    secret_name = os.environ["OPENAI_SECRET_NAME"]
    secret_value = cache.get_secret_string(secret_name)
    return json.loads(secret_value)["api_key"]

def lambda_handler(event, context):
    try:
        user_query = event.get('query', '')
        if not user_query:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': "Missing 'query'"})
            }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    
    llm = ChatOpenAI(
        model='gpt-4o-mini',
        api_key=get_openai_key(),
        max_retries=2
    )

    system_prompt = _load_prompt(os.path.join(os.path.dirname(__file__), 'system.txt'))
    task_prompt = _load_prompt(os.path.join(os.path.dirname(__file__), 'task.txt'))

    with open("", "r") as f:
        examples = json.load(example_file)

    example_prompt = PromptTemplate(template="Example:\nText: {text}\nOutput: {output}")

    fewshot = FewShotPromptTemplate(prefix="{system}\n{task}",
        examples=examples,
        example_prompt=example_prompt,
        suffix="{formatting_instructions}\nHere is your query:\n{query}\nOutput: ",
        input_variables=['query'],
        partial_variables = {'system': system_prompt,
                             'task': task_prompt
                             'formatting_instructions': '',
                             }
    ) 

    chain = fewshot | llm | json_parser
    output = chain.invoke({'query': user_query})







