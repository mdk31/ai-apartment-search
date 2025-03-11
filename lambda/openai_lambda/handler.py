import json
import os
import boto3

sfn_client = boto3.client('stepfunctions')

STEP_FUNCTION_ARN = os.getenv('STEP_FUNCTION_ARN')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    user_query = body.get('query')

    response = sfn_client.start_execution(
        stateMachineArn=STEP_FUNCTION_ARN,
        input = json.dumps({'query': user_query})
        
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Workflow started", "executionArn": response["executionArn"]})
    }