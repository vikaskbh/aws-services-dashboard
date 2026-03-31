from typing import Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def scan_rds(region: str) -> Tuple[List[Dict[str, str]], Optional[Dict[str, str]]]:
    try:
        client = boto3.client("rds", region_name=region)
        paginator = client.get_paginator("describe_db_instances")
        results: List[Dict[str, str]] = []

        for page in paginator.paginate():
            for db_instance in page.get("DBInstances", []):
                results.append(
                    {
                        "db_identifier": db_instance.get("DBInstanceIdentifier", ""),
                        "engine": db_instance.get("Engine", ""),
                        "status": db_instance.get("DBInstanceStatus", ""),
                    }
                )

        return results, None
    except (BotoCoreError, ClientError, Exception) as exc:
        return [], {"service": "rds", "message": str(exc)}
