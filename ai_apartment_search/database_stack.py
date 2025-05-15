import aws_cdk as cdk
import json
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

        vpc_id = cdk.Fn.import_value('VPCID')
        db_sg_id = cdk.Fn.import_value('DBSecurityGroupID')
        lambda_sg_id = cdk.Fn.import_value('LambdaSecurityGroupID')

        vpc = ec2.Vpc.from_lookup(
            self, 'ImportedVPC',
            vpc_id=vpc_id
        )

        db_security_group = ec2.SecurityGroup.from_security_group_id(
            self, 'ImportedDBSG',
            security_group_id=db_sg_id
        )

        lambda_security_group = ec2.SecurityGroup.from_security_group_id(
            self, 'ImportedLambdasG',
            security_group_id=lambda_sg_id
        )

        db_credentials = rds.Credentials.from_generated_secret('postgres')

        database = rds.DatabaseInstance(
            self, "PostgreSQLInstance",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_13),
            vpc=vpc,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO),
            allocated_storage=20,
            max_allocated_storage=100,
            storage_type=rds.StorageType.GP2,
            credentials=db_credentials,
            security_groups=[db_security_group],
            publicly_accessible=False, # default
            database_name='rentalapp',
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            backup_retention=cdk.Duration(days=7),
            delete_automated_backups=True,
            removal_policy=cdk.RemovalPolicy.RETAIN
        )
        
        cdk.CfnOutput(
            self, 'DatabaseEndpoint',
            value=database.db_instance_endpoint_address,
            description="The PostgreSQL DB endpoint"
        )

        cdk.CfnOutput(
            self, "DatabaseSecretName",
            value=db_credentials.secret_name
        )

