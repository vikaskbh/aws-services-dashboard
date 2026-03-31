from typing import Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def scan_s3(region: str) -> Tuple[List[Dict[str, str]], Optional[Dict[str, str]]]:
    # S3 bucket listing is global; region is used for client initialization.
    try:
        client = boto3.client("s3", region_name=region)
        response = client.list_buckets()
        results: List[Dict[str, str]] = []

        for bucket in response.get("Buckets", []):
            results.append({"bucket_name": bucket.get("Name", "")})

        return results, None
    except (BotoCoreError, ClientError, Exception) as exc:
        return [], {"service": "s3", "message": str(exc)}
