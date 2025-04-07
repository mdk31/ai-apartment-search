import json
import os
import boto3



sfn_client = boto3.client('stepfunctions')
STEP_FUNCTION_ARN = os.getenv('STEP_FUNCTION_ARN')

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
