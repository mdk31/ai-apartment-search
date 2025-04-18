import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_lambda_python_alpha as lambda_python,


)
from constructs import Construct

class LambdaStack(Stack):
    def __init__(self, scope: Construct, id: str, env_name: str = "prod", **kwargs):
        super().__init__(scope, id, **kwargs)
