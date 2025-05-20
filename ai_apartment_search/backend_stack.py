import aws_cdk as cdk
import os
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_cloudfront as cloudfront,
    aws_iam as iam,
    aws_cloudfront_origins as origins,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
    aws_lambda_python_alpha as lambda_python,
    aws_apigateway as apigateway,
    aws_wafv2 as wafv2,
    aws_secretsmanager as secretsmanager,
    aws_logs as logs,
    aws_dynamodb as dynamodb
)
from constructs import Construct

# TODO: Chain tasks in state machine correctlyc
class BackendStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        api = apigateway.RestApi(
            self, 'BackendAPI',
            rest_api_name='Backend Service',
        )

        plan = api.add_usage_plan(
            'UsagePlan',
            name='RateLimitPlan',
            throttle=apigateway.ThrottleSettings(
                rate_limit=10,
                burst_limit=20
            )
        )
        plan.add_api_stage(
            stage=api.deployment_stage
        )
        # rest_lambda_integration = apigateway.LambdaIntegration(
        #     request_handler_lambda
        # )
        # api.root.add_method("POST", rest_lambda_integration)

        wafv2.CfnWebACLAssociation(
            self, 'BackendWAFAPIAssociation',
            resource_arn=api.deployment_stage.stage_arn,
            web_acl_arn=web_acl.attr_arn
        )

        cdk.CfnOutput(
            self, 'APIGatewayURL',
            value=api.url,
        )
