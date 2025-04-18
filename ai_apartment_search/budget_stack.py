import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,
    aws_budgets as budgets
    
)
from constructs import Construct

class BudgetStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        budget_alert_topic = sns.Topic(
            self, 'BudgetAlertTopic',
            display_name='Budget Alert Notifications'
        )

        # Create a budget
        budget = budgets.CfnBudget(
            self, 'MonthlyBudget',
            budget=budgets.CfnBudget.BudgetDataProperty(
                budget_type='COST',
                time_unit='MONTHLY',
                budget_limit=budgets.CfnBudget.SpendProperty(
                    amount=100,
                    unit='USD'
                ),
                budget_name='MonthlyBudget',
            ),
            notifications_with_subscribers=[
                budgets.CfnBudget.NotificationWithSubscribersProperty(
                    notification=budgets.CfnBudget.NotificationProperty(
                        notification_type='ACTUAL',
                        comparison_operator='GREATER_THAN',
                        threshold=100,
                        threshold_type='PERCENTAGE'
                    ),
                    subscribers=[
                        budgets.CfnBudget.SpendProperty(
                            subscription_type='SNS',
                            address=budget_alert_topic.topic_arn
                        )
                    ]
                )
            ]
        )


