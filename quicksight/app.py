#!/usr/bin/env python3
import os

import subprocess
from pathlib import Path

from aws_cdk import (
    App,
    Stack,
    aws_s3,
)
from constructs import Construct

BUCKET_NAME = "quicksight-bucket-car-demo"


class QuicksightStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Set up a bucket
        bucket = aws_s3.Bucket(
            self,
            BUCKET_NAME,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name=BUCKET_NAME,
        )


if __name__ == "__main__":
    app = App()
    QuicksightStack(app, "QuicksightStack")
    app.synth()
