import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager
)
from constructs import Construct

class DatabaseStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
    
        vpc = ec2.Vpc(
            self, "DatabaseVPC",
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='PublicSubnet',
                    subnet_type=ec2.SubnetType.PUBLIC
                ),
                ec2.SubnetConfiguration(
                    name='PrivateSubnet',
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
                )
            ]
        )


        db_security_group = ec2.SecurityGroup(
            self, "DBSecurityGroup",
            vpc=vpc,
            description="The security group for the PostgreSQL database"
        )

        lambda_security_group = ec2.SecurityGroup(
            self, "LambdaSecurityGroup",
            vpc=vpc,
            description="The security group for lambda functions to connect to the database"
        )



        # db_secret_policy = iam.PolicyStatement(
        #     actions=["secretsmanager:GetSecretValue"],
        #     resources=[db_secret.secret_arn],
        #     principals=[iam.ServicePrincipal("lambda.amazonaws.com")]
        # )

        # allow lambda function to get db secrets
        # db_secret.add_to_resource_policy(db_secret_policy)

        database = rds.DatabaseInstance(
            self, "PostgreSQLInstance",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_13),
            vpc=vpc,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO),
            allocated_storage='20GB',
            max_allocated_storage='100GB',
            storage_type=rds.StorageType.GP2,
            credentials=rds.Credentials.from_secret(db_secret),
            security_groups=[db_security_group],
            publicly_accessible=False, # default
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            backup_retention=cdk.Duration(days=7),
            delete_automated_backups=True,
            removal_policy=cdk.RemovalPolicy.RETAIN
        )

        cdk.CfnOutput(
            self, 'VPCID',
            value=vpc.vpc_id,
            description='The VPC ID where the DB is deployed'
        )

        cdk.CfnOutput(
            self, 'LambdaSecurityGroupID',
            value=lambda_security_group.security_group_id,
            description="The security group ID for lamda functions that need DB access")
        

