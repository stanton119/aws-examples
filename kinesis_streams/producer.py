#!/usr/bin/env python3
import argparse
import os
import uuid
from random import random
from time import sleep
from typing import Dict

import boto3
import requests

client = boto3.client("kinesis", region_name="us-east-1")
client_firehose = boto3.client("firehose", region_name="us-east-1")
partition_key = str(uuid.uuid4())
DEFAULT_KENESIS_STREAM_NAME = os.getenv("KENESIS_STREAM_NAME")
IS_FIREHOSE = bool(os.getenv("IS_FIREHOSE"))


def get_random_user() -> Dict:
    request_url = "https://randomuser.me/api/"

    result = requests.get(request_url)
    result_json = result.text
    # result_json = result.json()

    return result_json


def submit_to_kenesis(json_data: str, kenesis_stream_name: str = None):
    if kenesis_stream_name is None:
        kenesis_stream_name = DEFAULT_KENESIS_STREAM_NAME

    print(f"logging to {kenesis_stream_name} - {partition_key}: {json_data[:30]}")
    client.put_record(
        StreamName=kenesis_stream_name,
        Data=json_data,
        PartitionKey=partition_key,
    )


def submit_to_firehose(json_data: str, kenesis_stream_name: str = None):
    if kenesis_stream_name is None:
        kenesis_stream_name = DEFAULT_KENESIS_STREAM_NAME

    print(f"logging to {kenesis_stream_name}: {json_data[:30]}")
    json_data = {"Data": json_data}
    client_firehose.put_record(
        DeliveryStreamName=kenesis_stream_name,
        Record=json_data,
    )


def print_to_log(json_data: str):
    print(json_data)


def start_producer(
    request_method: callable = get_random_user,
    submit_method: callable = submit_to_kenesis,
    number_requests: int = 10,
):
    if number_requests is None:
        number_requests = 10

    for _ in range(number_requests):
        result_json = request_method()
        submit_method(result_json)

        # wait <1s
        sleep(random())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--number_requests", type=int)
    parser.add_argument(
        "--kenesis_stream_name", type=str, default=DEFAULT_KENESIS_STREAM_NAME
    )
    parser.add_argument("--firehose", type=bool, default=IS_FIREHOSE)
    args = parser.parse_args()

    if args.firehose:
        submit_method = lambda x: submit_to_firehose(
            x, kenesis_stream_name=args.kenesis_stream_name
        )
    else:
        submit_method = lambda x: submit_to_kenesis(
            x, kenesis_stream_name=args.kenesis_stream_name
        )

    start_producer(submit_method=submit_method, number_requests=args.number_requests)


if __name__ == "__main__":
    main()
    