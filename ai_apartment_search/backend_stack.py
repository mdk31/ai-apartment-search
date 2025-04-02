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
    aws_lambda_python_alpha as lambda_python,
    aws_apigateway as apigateway,
    aws_wafv2 as wafd
)
from constructs import Construct

# TODO: write index document
class BackendStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        state_machine = sfn.StateMachine(
            self, 'BackendWorkflow',
            definition=sfn.Pass(self, 'PlaceholderState')
        )

        request_handler_lambda = lambda_python.PythonFunction(
            self, 'RequestHandlerLambda',
            entry='lambda/step_initate_lambda',
            index='handler.py',
            handler='lambda_handler',
            environment={
                "STEP_FUNCTION_ARN": state_machine.state_machine_arn
            }
        )

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
        rest_lambda_integration = apigateway.LambdaIntegration(
            request_handler_lambda
        )
        api.root.add_method("POST", rest_lambda_integration)

        # web_acl = waf.CfnWebACL(
        #     self, 'APIGatewayWAF',
        #     scope='REGIONAL',
        #     default_action=waf.CfnWebACL.DefaultActionProperty(allow={}),
        #     rules=[
        #         waf.CfnWebACL.RuleProperty(
        #             name='BlockedIPs',
        #             priority=1,
        #             action=waf.CfnWebACL.ReulActionProperty(allow={})
        #         )
        #     ]
        # )



        cdk.CfnOutput(
            self, 'APIGatewayURL',
            value=api.url,
        )
