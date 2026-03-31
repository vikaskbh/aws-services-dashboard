from typing import Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def scan_ec2(region: str) -> Tuple[List[Dict[str, str]], Optional[Dict[str, str]]]:
    try:
        client = boto3.client("ec2", region_name=region)
        paginator = client.get_paginator("describe_instances")
        results: List[Dict[str, str]] = []

        for page in paginator.paginate():
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    results.append(
                        {
                            "instance_id": instance.get("InstanceId", ""),
                            "instance_type": instance.get("InstanceType", ""),
                            "state": instance.get("State", {}).get("Name", "unknown"),
                            "region": region,
                        }
                    )

        return results, None
    except (BotoCoreError, ClientError, Exception) as exc:
        return [], {"service": "ec2", "message": str(exc)}
