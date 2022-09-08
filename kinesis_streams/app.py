#!/usr/bin/env python3
import os

import subprocess
from pathlib import Path

from aws_cdk import (
    App,
    Duration,
    Stack,
    aws_dynamodb,
    aws_events,
    aws_events_targets,
    aws_lambda,
    aws_s3,
    aws_kinesis,
    aws_kinesisfirehose,
    aws_kinesisfirehose_destinations_alpha,
    aws_iam,
)
from constructs import Construct


"""
Kenesis stream
Lambda/EC2 to start producer
S3 bucket for results

Kenesis firehose stream to write to s3
S3 bucket for results

based on: https://github.com/ACloudGuru-Resources/Course_AWS_Certified_Machine_Learning/blob/master/Chapter3/setup-data-producer.yml
"""


class RandomUsersStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # s3 bucket for results
        s3_bucket = aws_s3.Bucket(
            self,
            "random_users_s3_bucket",
            versioned=True,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
        )

        # create Role for firehose delivery stream
        firehose_role = aws_iam.Role(
            self,
            "firehose_role",
            assumed_by=aws_iam.ServicePrincipal("firehose.amazonaws.com"),
        )

        # //add s3 permission
        # firehoseRole.addToPolicy(new iam.PolicyStatement({
        #     effect: iam.Effect.ALLOW,
        #     resources: [bucket.bucketArn],
        #     actions: ['s3:AbortMultipartUpload', 's3:GetBucketLocation','s3:GetObject','s3:ListBucket','s3:ListBucketMultipartUploads','s3:PutObject'],
        # }));

        # //add kinesis permission
        # firehoseRole.addToPolicy(new iam.PolicyStatement({
        #     effect: iam.Effect.ALLOW,
        #     resources: [dataStream.streamArn],
        #     actions: ['kinesis:DescribeStream', 'kinesis:GetShardIterator','kinesis:GetRecords'],
        # }));

        # create kenesis stream
        # aws_kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(bucket_arn=)
        # .CfnDeliveryStream.S3DestinationConfigurationProperty(
        firehose = aws_kinesisfirehose.CfnDeliveryStream(
            self,
            "Delivery Stream",
            s3_destination_configuration=aws_kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                bucket_arn=s3_bucket.bucket_arn,
                role_arn=firehose_role.role_arn,
                # the properties below are optional
                # buffering_hints=aws_kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                #     interval_in_seconds=123,
                #     size_in_mBs=123
                # ),
            ),
        )

        # create lambda
        producer_path = Path(__file__).resolve().parent / "producer.py"
        with open(producer_path, encoding="utf8") as fp:
            handler_code = fp.read()
        lambda_api_call = aws_lambda.Function(
            self,
            "Function",
            code=aws_lambda.InlineCode(handler_code),
            handler="handler.main",
            timeout=Duration.seconds(10),
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            memory_size=128,
            description="Call Random users API.",
        )
        # lambda_api_call.add_environment(
        #     "KENESIS_STREAM_NAME", firehose.delivery_stream_name
        # )
        lambda_api_call.add_environment("IS_FIREHOSE", "0")
        # s3_bucket.grant_write(firehose)

        # create eventbridge rule
        daily_rule = aws_events.Rule(
            self,
            "api_call_rule",
            schedule=aws_events.Schedule.cron(minute="2"),
        )
        daily_rule.add_target(aws_events_targets.LambdaFunction(lambda_api_call))


app = App()
RandomUsersStack(app, "RandomUsersStack")
app.synth()
