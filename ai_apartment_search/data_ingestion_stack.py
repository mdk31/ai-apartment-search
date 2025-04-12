from aws_cdk import (
    Stack

)
from constructs import Construct

class DataIngestionStack(Stack):
    def __init__(self, scope: Construct, id: str, env_name: str = "prod", **kwargs):
        super().__init__(scope, id, **kwargs)
        
        max_daily_calls = 30 if env_name == 'dev' else 20
        