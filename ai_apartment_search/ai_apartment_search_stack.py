import aws_cdk as cdk

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_lambda_python_alpha as python,
    aws_secretsmanager as secretsmanager
    # core
)

from constructs import Construct

class AiApartmentSearchStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        db_secret_arn = cdk.Fn.import_value("DatabaseSecretARN")
        db_endpoint = cdk.Fn.import_value("DatabaseEndpoint")
        lambda_sg_id = cdk.Fn.import_value("LambdaSecurityGroupID")
        vpc_id = cdk.Fn.import_value('VPCID')

        db_secret = secretsmanager.Secret.from_secret_name_v2(
            self, "DBSecret", "PostgreSQLCredentials"
        )

        vpc = ec2.Vpc.from_lookup(self, "ImportedVPC", vpc_id=vpc_id)
        lambda_security_group = ec2.SecurityGroup.from_security_group_id(
            self, 'ImportedLambdaSecurityGroup',
            lambda_sg_id
        )

        lambda_role = iam.Role(
            self, 'LambdaExecutionRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')
            ]
        )

        api_lambda_role = iam.Role(
            self, 'ApiLambdaExecutionRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')
            ]

        )

        db_secret.grant_read(lambda_role)

        # lambda funcitons
        db_query_lambda = _lambda.Function(
            self, 'DatabaseQueryLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='db_lambda_handler',
            code=_lambda.Code.from_asset('lambda/'),
            vpc=vpc,
            security_groups=[lambda_security_group],
            role=lambda_role
        )

        openai_lambda = python.PythonFunction(
            self, 'OpenAIHandlerLambda',
            entry='lambda',  # Folder containing handler.py
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='openai_lambda_handler'
        )


        api_gateway = apigw.LambdaRestApi(
            self, "APIGateway",
            handler=openai_lambda,
            proxy=True,
            deploy_options=apigw.StageOptions(
                logging_level=apigw.MethodLoggingLevel.ERROR,
                data_trace_enabled=False
            )
        )






        # domain_name = "yourcustomdomain.com"
        # hosted_zone = route53.HostedZone.from_lookup(self, "HostedZone", domain_name=domain_name)

        # certificate = acm.Certificate(
        #     self, "SiteCertificate",
        #     domain_name=domain_name,
        #     validation=acm.CertificateValidation.from_dns(hosted_zone)
        # )

        # db_secret = secretsmanager.Secret.from_secret_name_v2(self, "DBSecret", "PostgresDB")
        # db_host = ssm.StringParameter.from_string_parameter_name(self, "DBHost", "/rental-app/db-host").string_value

        # log_group = logs.LogGroup(self, "APIGatewayLogGroup")

        # frontend_bucket = s3.Bucket(
        #     self, "FrontendBucket",
        #     website_index_document="index.html",
        #     public_read_access=True,
        #     removal_policy=core.RemovalPolicy.DESTROY
        # )

        # frontend_distribution = cloudfront.Distribution(
        #     self, "FrontendDistribution",
        #     default_behavior=cloudfront.BehaviorOptions(
        #         origin=origins.S3Origin(frontend_bucket),
        #         viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
        #     ),
        #     domain_names=[domain_name],
        #     certificate=certificate
        # )

        # route53.ARecord(
        #     self, "FrontendAlias",
        #     zone=hosted_zone,
        #     target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(frontend_distribution))
        # )

        # openai_secret = secretsmanager.Secret.from_secret_name_v2(self, "OpenAISecret", "OpenAISecret")

        # openai_lambda = _lambda.Function(
        #     self, "OpenAIFunc",
        #     runtime=_lambda.Runtime.PYTHON_3_9,
        #     handler="openai_handler.lambda_handler",
        #     code=_lambda.Code.from_asset("lambda"),
        #     environment={
        #         "OPENAI_SECRET_ARN": openai_secret.secret_arn
        #     }
        # )
        # openai_secret.grant_read(openai_lambda)


        # ssm.StringParameter(
        #     self, "OpenAIAPIURLParameter",
        #     parameter_name="/rental-app/openai-api-url",
        #     string_value=api_gateway.url
        # )

        # cluster = ecs.Cluster(self, "FargateCluster")

        # fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
        #     self, "FlaskAPI",
        #     cluster=cluster,
        #     task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
        #         image=ecs.ContainerImage.from_registry(f"{core.Stack.of(self).account}.dkr.ecr.us-east-1.amazonaws.com/rental-flask-api:latest"),
        #         environment={
        #             "DB_SECRET_ARN": db_secret.secret_arn,
        #             "DB_HOST_PARAM": "/rental-app/db-host",
        #             "OPENAI_API_PARAM": "/rental-app/openai-api-url"
        #         }
        #     ),
        #     certificate=certificate,
        #     domain_name=f"api.{domain_name}",
        #     domain_zone=hosted_zone,
        #     desired_count=1
        # )

        # route53.ARecord(
        #     self, "ApiAlias",
        #     zone=hosted_zone,
        #     target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(fargate_service.load_balancer))
        # )

        # core.CfnOutput(self, "FrontendURL", value=f"https://{domain_name}")
        # core.CfnOutput(self, "FlaskAPIEndpoint", value=f"https://api.{domain_name}")
        # core.CfnOutput(self, "OpenAIAPIURL", value=api_gateway.url)
        # core.CfnOutput(self, "DBHost", value=db_host)
