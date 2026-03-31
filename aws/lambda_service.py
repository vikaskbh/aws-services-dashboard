from typing import Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def scan_lambda(region: str) -> Tuple[List[Dict[str, str]], Optional[Dict[str, str]]]:
    try:
        client = boto3.client("lambda", region_name=region)
        paginator = client.get_paginator("list_functions")
        results: List[Dict[str, str]] = []

        for page in paginator.paginate():
            for function in page.get("Functions", []):
                results.append(
                    {
                        "function_name": function.get("FunctionName", ""),
                        "runtime": function.get("Runtime", "n/a"),
                    }
                )

        return results, None
    except (BotoCoreError, ClientError, Exception) as exc:
        return [], {"service": "lambda", "message": str(exc)}
