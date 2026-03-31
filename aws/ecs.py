from typing import Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def scan_ecs(region: str) -> Tuple[List[Dict[str, str]], Optional[Dict[str, str]]]:
    try:
        client = boto3.client("ecs", region_name=region)
        cluster_paginator = client.get_paginator("list_clusters")
        results: List[Dict[str, str]] = []

        for page in cluster_paginator.paginate():
            for cluster_arn in page.get("clusterArns", []):
                cluster_name = cluster_arn.rsplit("/", maxsplit=1)[-1]
                service_paginator = client.get_paginator("list_services")

                for service_page in service_paginator.paginate(cluster=cluster_arn):
                    service_arns = service_page.get("serviceArns", [])
                    if not service_arns:
                        continue

                    described = client.describe_services(
                        cluster=cluster_arn, services=service_arns
                    )
                    for service in described.get("services", []):
                        results.append(
                            {
                                "cluster_name": cluster_name,
                                "service_name": service.get("serviceName", ""),
                                "status": service.get("status", ""),
                            }
                        )

        return results, None
    except (BotoCoreError, ClientError, Exception) as exc:
        return [], {"service": "ecs", "message": str(exc)}
