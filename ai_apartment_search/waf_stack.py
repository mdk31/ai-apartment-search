import aws_cdk as cdk
import os
from aws_cdk import (
    Stack,
    aws_wafv2 as wafv2
)
from constructs import Construct

# TODO: IP rate limiting rules

class BackendStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        bot_rule = wafv2.CfnWebACL.RuleProperty(
            name='BotControlRule',
            priority=1,
            statement=wafv2.CfnWebACL.StatementProperty(
                managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                    vendor_name='AWS',
                    name='AWSManagedRulesBotControlRuleSet'
                )
            ),
            action=wafv2.CfnWebACL.RuleActionProperty(block={}),
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="BotControl",
                sampled_requests_enabled=True
            )
        )


        common_rule = wafv2.CfnWebACL.RuleProperty(
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
        )


        kill_switch_rule = wafv2.CfnWebACL.RuleProperty( # Kill switch rule for lambda
            name='KillSwitch',
            priority=0,
            statement=wafv2.CfnWebACL.StatementProperty(
                byte_match_statement=wafv2.CfnWebACL.ByteMatchStatementProperty(
                    search_string='on',
                    field_to_match=wafv2.CfnWebACL.FieldToMatchProperty(
                        single_header={"Name": "x-kill-switch"} # filler header
                        ),
                        positional_constraint='EXACTLY',
                        text_transformations=[
                            {'priority': 0, "type": "NONE"}
                        ]
                    )
            ),
            action=wafv2.CfnWebACL.RuleActionProperty(count={}),
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name='KillSwitch',
                sampled_requests_enabled=True
            )
        )

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
                bot_rule,
                common_rule,
                kill_switch_rule
            ]
        )
