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

class BackendStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.web_acl = wafv2.CfnWebACL(
            self, 'APIGatewayWAF',
            scope='REGIONAL',
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name='APIGatewayWAF',
                sampled_requests_enabled=True
            ),
            default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
            rules=[
                wafv2.CfnWebACL.RuleProperty(
                    name='CRSRule',
                    statement = wafv2.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                            vendor_name='AWS',
                            name='AWSManagedRulesCommonRuleSet'
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=True,
                        metric_name='CommonRuleSet',
                        sampled_requests_enabled=True
                    )
                ),
                wafv2.CfnWebACL.RuleProperty( # Kill switch rule for lambda
                    name='KillSwitch',
                    priority=0,
                    statement=wafv2.CfnWebACL.StatementProperty(
                        byte_match_statement=wafv2.CfnWebACL.ByteMatchStatementProperty(
                            search_string='on',
                            field_to_match=wafv2.CfnWebACL.FieldToMatchProperty(
                                single_header={"Name": "x-kill-switch"}
                            ),
                            positional_constraint='EXACTLY',
                            text_transformations=[
                                {'priority': 0, "type": "NONE"}
                            ]
                        )
                    ),
                    action=wafv2.CfnWebACL.RuleActionProperty(block={}),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=True,
                        metric_name='KillSwitch',
                        sampled_requests_enabled=True
                    )
                )
            ]
        )
