import json
import os
import boto3

sfn_client = boto3.client('stepfunctions')
STEP_FUNCTION_ARN = os.getenv('STEP_FUNCTION_ARN')
REQUEST_LIMIT_TABLE = os.getenv('REQUEST_LIMIT_TABLE')
DAILY_REQUEST_LIMIT = int(os.getenv('DAILY_REQUEST_LIMIT'))

def lambda_handler(event, context):

    try:
        body = json.loads(event['body'])

        if 'query' not in body:
            return {
                'statusCode': 400,
                "body": json.dumps({"error": "Missing 'query' in request body"})
            }
        
        response = sfn_client.start_sync_execution(
            stateMachineArn=STEP_FUNCTION_ARN,
            input=json.dumps(body)
        )
        # The actual result of the workflow is in response["output"]
        result = json.loads(response["output"])

        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }