import json
import os
import boto3

sfn_client = boto3.client('stepfunctions')
STEP_FUNCTION_ARN = os.getenv('STEP_FUNCTION_ARN')

def lambda_handler(event, context):

    try:
        body = json.loads(event['body'])

        if 'query' not in body:
            return {
                'statusCode': 400,
                "body": json.dumps({"error": "Missing 'query' in request body"})
            }
        
        response = sfn_client.start_execution(
            stateMachineArn=STEP_FUNCTION_ARN,
            input=json.dumps(body)
        )
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Step function started",
                "executionArn": response["executionArn"]
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }