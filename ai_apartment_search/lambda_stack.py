import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_lambda_python_alpha as lambda_python,
    aws_wafv2 as wafv2,
    aws_events as events,
    aws_stepfunctions as sfn,
    aws_events_targets as targets,
    aws_secretsmanager as secretsmanager

)
from constructs import Construct

# TODO: Move rest or lambdas, check where state machine should go
class LambdaStack(Stack):
    def __init__(self, scope: Construct, id: str, *, web_acl: wafv2.CfnWebACL, env_name: str = "prod", **kwargs):
        super().__init__(scope, id, **kwargs)

        db_secret_name = cdk.Fn.import_value('DatabaseSecretName')
        if not db_secret_name:
            raise ValueError("Database credentials secret name not found")


        if not all([web_acl.name, web_acl.attr_id, web_acl.scope]):
            raise ValueError("Missing one or more required WebACL environment variables")

        environment={
            "WEB_ACL_NAME": web_acl.name,
            "WEB_ACL_ID": web_acl.attr_id,
            "WEB_ACL_SCOPE": web_acl.scope
        }

        kill_lambda = lambda_python.PythonFunction(
            self, 'ShutOffLambda',
            entry='lambda_files/shutoff_lambda.py',
            index='handler.py',
            handler='lambda_handler',
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_11,
            environment=environment,
            timeout=cdk.Duration.seconds(10),
            memory_size=1024
        )

        monthly_reset_rule = events.Rule(
            self, 'ResetKillSwitchRule',
            schedule=events.Schedule.cron(minute='0', hour='0', day='1', month='*', year='*'),
        )
        monthly_reset_rule.add_target(
            targets.LambdaFunction(
                handler=kill_lambda, # type: ignore
                event=events.RuleTargetInput.from_object({"mode": "activate"})
            )
        )


        request_handler_lambda = lambda_python.PythonFunction(
            self, 'RequestHandlerLambda',
            entry='lambda_files/step_initate_lambda',
            index='handler.py',
            handler='lambda_handler',
            environment={
                "STEP_FUNCTION_ARN": state_machine.state_machine_arn,
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



        environment={
            'DBSECRET': db_secret_name
        }       

        query_db_lambda = lambda_python.PythonFunction(
            self, 'QueryDBLambda',
            entry='lambda_files/query_db_lambda',
            index='handler.py',
            environment=environment
        )

        state_machine = sfn.StateMachine(
            self, 'BackendWorkflow',
            definition=definition,
            state_machine_type=sfn.StateMachineType.STANDARD,
            logs=sfn.LogOptions(
                destination=log_group,
                level=sfn.LogLevel.ALL
            )
        )






        
