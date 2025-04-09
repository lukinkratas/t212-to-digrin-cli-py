from collections.abc import Callable
from typing import Any

import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')


def handle_client_error(func: Callable[[Any], Any], *args, **kwargs) -> Any | None:
    try:
        response = func(*args, **kwargs)

    except ClientError as e:
        print(e)
        return None

    return response


def s3_put_object(bytes: bytes, bucket: str, key: str) -> dict[str, Any] | None:
    return handle_client_error(s3_client.put_object, Body=bytes, Bucket=bucket, Key=key)


def s3_list_objects(bucket: str, key_prefix: str) -> list[str] | None:
    response = handle_client_error(
        s3_client.list_objects_v2, Bucket=bucket, Prefix=key_prefix
    )
    return [content.get('Key') for content in response.get('Contents')]


def s3_get_object(bucket: str, key: str) -> bytes | None:
    response = handle_client_error(s3_client.get_object, Bucket=bucket, Key=key)
    return response.content
