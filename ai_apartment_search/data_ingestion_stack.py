import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_lambda_python_alpha as lambda_python,


)
from constructs import Construct

class DataIngestionStack(Stack):
    def __init__(self, scope: Construct, id: str, env_name: str = "prod", **kwargs):
        super().__init__(scope, id, **kwargs)

        db_secret_name = cdk.Fn.import_value("DatabaseSecretName")
        
        max_daily_calls = 30 if env_name == 'dev' else 20

        fetch_active_rentals_lambda = lambda_python.PythonFunction(
            self, 'FetchActiveRentalLambda',
            entry='lambda_files/fetch_active_rentals',
            index='handler.py',
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_11,
            timeout=cdk.Duration.minutes(5),
            environment={
                'MAX_CALLS': max_daily_calls,
                'DBSECRET': db_secret_name
            }
        )
        
        fetch_rental_details_lambda = lambda_python.PythonFunction(
            self, 'FetchRentalDetailsLambda',
            entry='lambda_files/fetch_rental_details',
            index='handler.py'
        )