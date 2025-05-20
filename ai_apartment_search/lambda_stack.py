import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_lambda_python_alpha as lambda_python,
    aws_wafv2 as wafv2,
    aws_events as events,
    aws_stepfunctions as sfn,
    aws_events_targets as targets,
    aws_secretsmanager as secretsmanager,
    aws_logs as logs,
    aws_stepfunctions_tasks as sfn_tasks,
    aws_ec2 as ec2
)
from constructs import Construct

# TODO: Move rest or lambdas, check where state machine should go
class LambdaStack(Stack):
    def __init__(self, scope: Construct, id: str, *, web_acl: wafv2.CfnWebACL, env_name: str = "prod", **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc_id = cdk.Fn.import_value('VPCID')
        db_sg_id = cdk.Fn.import_value('DBSecurityGroupID')
        db_lambda_sg_id = cdk.Fn.import_value('LambdaSecurityGroupID')

        vpc = ec2.Vpc.from_lookup(self, "ImportedVPC", vpc_id=vpc_id)
        lambda_sg = ec2.SecurityGroup.from_security_group_id(self, "LambdaSG", security_group_id=db_lambda_sg_id)
        db_sg = ec2.SecurityGroup.from_security_group_id(self, 'DBSG', security_group_id=db_sg_id)

        # Ensure lambda can connect to the DB security group
        db_sg.add_ingress_rule(
            peer=lambda_sg
        )

        db_secret_name = cdk.Fn.import_value('DatabaseSecretName')
        if not db_secret_name:
            raise ValueError("Database credentials secret name not found")
        
        # Make calls to OpenAI models
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

        openai_secret.grant_read(openai_lambda)

        # Lambda to query database from OpenAI results
        db_environment={
            'DBSECRET': db_secret_name
        }       
        query_db_lambda = lambda_python.PythonFunction(
            self, 'QueryDBLambda',
            entry='lambda_files/query_db_lambda',
            index='handler.py',
            security_groups=[lambda_sg],
            environment=db_environment,
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_11,
            timeout=cdk.Duration.seconds(10)
        )

        secretsmanager.Secret.from_secret_name_v2(
            self, 'DBSecret', db_secret_name
        ).grant_read(query_db_lambda)

        openai_tasks = sfn_tasks.LambdaInvoke(
            self, 'CallOpenAI',
            lambda_function=openai_lambda # type: ignore
        )

        query_db_tasks = sfn_tasks.LambdaInvoke(
             self, 'QueryDB',
             lambda_function=query_db_lambda # type: ignore
        )

        definition = openai_tasks.next(query_db_tasks)
        
        log_group = logs.LogGroup(
            self, 'StateMachineLogs',
            retention=logs.RetentionDays.ONE_WEEK
        )

        state_machine = sfn.StateMachine(
            self, 'BackendWorkflow',
            definition_body=sfn.DefinitionBody.from_chainable(definition),
            state_machine_type=sfn.StateMachineType.STANDARD,
            logs=sfn.LogOptions(
                destination=log_group,
                level=sfn.LogLevel.ALL
            )
        )

        # Function to invoke the state machine
        request_handler_lambda = lambda_python.PythonFunction(
            self, 'RequestHandlerLambda',
            entry='lambda_files/step_initate_lambda',
            index='handler.py',
            handler='lambda_handler',
            environment={
                "STEP_FUNCTION_ARN": state_machine.state_machine_arn,
            },
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_11
        )

        state_machine.grant_start_execution(request_handler_lambda)

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















        
