from typing import Any

import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')


def s3_put_object(bytes: bytes, bucket: str, key: str) -> dict[str, Any] | None:
    try:
        response = s3_client.put_object(Body=bytes, Bucket=bucket, Key=key)

    except ClientError as e:
        print(e)
        return None

    return response


def s3_list_objects(bucket: str, key_prefix: str) -> dict[str, Any] | None:
    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=key_prefix)

    except ClientError as e:
        print(e)
        return None

    return [content.get('Key') for content in response.get('Contents')]


def s3_get_object(bucket: str, key: str) -> dict[str, Any] | None:
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)

    except ClientError as e:
        print(e)
        return None

    return response
