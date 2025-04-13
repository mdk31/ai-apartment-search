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
    aws_logs as logs
)
from constructs import Construct

# TODO: Chain tasks in state machine correctlyc
class BackendStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        log_group = logs.LogGroup(
            self, 'OpenAIStateMachineLogs',
            retention=logs.RetentionDays.ONE_WEEK
        )

        openai_tasks = sfn_tasks.LambdaInvoke(
            self, 'CallOpenAI',
            lambda_function=openai_lambda,
            output_path="$.Payload"
        )


        request_handler_lambda = lambda_python.PythonFunction(
            self, 'RequestHandlerLambda',
            entry='lambda_files/step_initate_lambda',
            index='handler.py',
            handler='lambda_handler',
            environment={
                "STEP_FUNCTION_ARN": state_machine.state_machine_arn
            }
        )

        openai_secret = secretsmanager.Secret.from_secret_name_v2(
            self, 'OpenAISecret', 'OpenAIKey'
        )

        openai_lambda = lambda_python.PythonFunction(
            self, 'OpenAILambda',
            entry='lambda_files/openai_lambda',
            index='handler.py',
            environment={
                'OPENAI_SECRET_NAME': openai_secret.secret_name
            },
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_11,
            timeout=cdk.Duration.seconds(10)
        )

        db_secret_name = cdk.Fn.import_value('DatabaseSecretName')
        db_secret = secretsmanager.Secret.from_secret_name_v2(
            self, 'ImportedDBSecret', db_secret_name
        )

        query_db_lambda = lambda_python.PythonFunction(
            self, 'QueryDBLambda',
            entry='lambda_files/query_db_lambda',
            index='handler.py',
            environment={
                'DBSECRET': db_secret.secret_name
            }
        )

        query_task = sfn_tasks.LambdaInvoke(
            self, 'QueryDB',
            lambda_function=query_db_lambda,
            output_path="$.Payload"
        )

        definition = openai_tasks.next(query_task)

        state_machine = sfn.StateMachine(
            self, 'BackendWorkflow',
            definition=definition,
            state_machine_type=sfn.StateMachineType.STANDARD,
            logs=sfn.LogOptions(
                destination=log_group,
                level=sfn.LogLevel.ALL
            )
        )



        openai_secret.grant_read(openai_lambda)

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

        web_acl = wafv2.CfnWebACL(
            self, 'APIGatewayWAF',
            scope='REGIONAL',
            default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
            rules=[
                wafv2.CfnWebACL.RuleProperty(
                    name='CRSRule',
                    statement = wafv2.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                            vendor_name='AWS',
                            name='AWSManagedRulesCommonRuleSet'
                        )
                    )
                )
            ]
        )

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
