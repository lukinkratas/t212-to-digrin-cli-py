from typing import Any

import boto3

s3_client = boto3.client('s3')


def s3_put_object(bytes: bytes, bucket: str, key: str) -> dict[str, Any] | None:
    return s3_client.put_object(Body=bytes, Bucket=bucket, Key=key)


def s3_list_objects(bucket: str, key_prefix: str = '') -> list[str] | None:
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=key_prefix)
    return [content.get('Key') for content in response.get('Contents')]


def s3_get_object(bucket: str, key: str) -> bytes | None:
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response.content
