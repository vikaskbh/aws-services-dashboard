import logging
from typing import Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import BotoCoreError, ClientError, EndpointConnectionError


def scan_lightsail(region: str) -> Tuple[List[Dict[str, str]], Optional[Dict[str, str]]]:
    """
    Collect Lightsail instances using read-only API calls.
    """
    logger = logging.getLogger(__name__)

    try:
        client = boto3.client("lightsail", region_name=region)

        # Manual pagination: still only calls get_instances().
        results: List[Dict[str, str]] = []
        next_token: Optional[str] = None

        while True:
            kwargs = {}
            if next_token:
                kwargs["pageToken"] = next_token

            try:
                response = client.get_instances(**kwargs)
            except ClientError as exc:
                error_code = exc.response.get("Error", {}).get("Code", "")
                error_message = exc.response.get("Error", {}).get("Message", str(exc))

                if "AccessDenied" in error_code or "AccessDenied" in error_message:
                    logger.warning(
                        "Lightsail scan AccessDenied (region=%s): %s",
                        region,
                        error_message,
                    )
                    return (
                        [],
                        {
                            "service": "lightsail",
                            "message": "Access denied to Lightsail resources.",
                        },
                    )

                # Endpoint/region-related failures.
                combined = f"{error_code} {error_message}".lower()
                if (
                    "unknownendpoint" in combined
                    or "endpoint" in combined
                    or "region" in combined
                    or "unsupported" in combined
                ):
                    logger.warning(
                        "Lightsail not available in region (region=%s): %s",
                        region,
                        error_message,
                    )
                    return (
                        [],
                        {
                            "service": "lightsail",
                            "message": "Lightsail not available in this region.",
                        },
                    )

                logger.exception(
                    "Lightsail scan ClientError (region=%s): %s", region, error_message
                )
                return (
                    [],
                    {"service": "lightsail", "message": error_message},
                )

            instances = response.get("instances", [])
            for instance in instances:
                results.append(
                    {
                        "name": instance.get("name", ""),
                        "blueprint": instance.get("blueprintId", ""),
                        "bundle": instance.get("bundleId", ""),
                        "state": instance.get("state", {}).get("name", "unknown"),
                    }
                )

            next_token = response.get("nextPageToken")
            if not next_token:
                break

        return results, None

    except EndpointConnectionError as exc:
        logger.warning(
            "Lightsail endpoint connection error (region=%s): %s", region, str(exc)
        )
        return (
            [],
            {"service": "lightsail", "message": "Lightsail not available in this region."},
        )
    except (BotoCoreError, ClientError, Exception) as exc:
        logger.exception("Lightsail scan failed unexpectedly (region=%s)", region)
        return [], {"service": "lightsail", "message": str(exc)}
