from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import os
from typing import Any, Dict, List, Optional

import boto3
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from aws.ec2 import scan_ec2
from aws.ecs import scan_ecs
from aws.lambda_service import scan_lambda
from aws.lightsail import scan_lightsail
from aws.rds import scan_rds
from aws.s3 import scan_s3


app = FastAPI(title="AWS Services Dashboard")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_default_region() -> str:
    session_region = boto3.session.Session().region_name
    return (
        session_region
        or os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or "us-east-1"
    )


def build_scan_payload(region: Optional[str] = None) -> Dict[str, Any]:
    selected_region = region or get_default_region()
    errors = []

    ec2_data, ec2_error = scan_ec2(selected_region)
    if ec2_error:
        errors.append(ec2_error)

    rds_data, rds_error = scan_rds(selected_region)
    if rds_error:
        errors.append(rds_error)

    lambda_data, lambda_error = scan_lambda(selected_region)
    if lambda_error:
        errors.append(lambda_error)

    ecs_data, ecs_error = scan_ecs(selected_region)
    if ecs_error:
        errors.append(ecs_error)

    s3_data, s3_error = scan_s3(selected_region)
    if s3_error:
        errors.append(s3_error)

    lightsail_data, lightsail_error = scan_lightsail(selected_region)
    if lightsail_error:
        errors.append(lightsail_error)

    ec2_states: Dict[str, int] = {}
    running_ec2 = 0
    for instance in ec2_data:
        state = instance.get("state", "unknown")
        ec2_states[state] = ec2_states.get(state, 0) + 1
        if state == "running":
            running_ec2 += 1

    summary = {
        "total_ec2_running": running_ec2,
        "total_rds": len(rds_data),
        "total_lambda": len(lambda_data),
        "total_ecs_services": len(ecs_data),
        "total_s3_buckets": len(s3_data),
        "total_lightsail_instances": len(lightsail_data),
    }
    if summary["total_rds"] > 0:
        cost_risk = "high"
    elif summary["total_ec2_running"] > 0:
        cost_risk = "medium"
    else:
        cost_risk = "low"

    return {
        "region": selected_region,
        "last_scan": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "cost_risk": cost_risk,
        "ec2_state_counts": ec2_states,
        "ec2": ec2_data,
        "rds": rds_data,
        "lambda": lambda_data,
        "ecs": ecs_data,
        "s3": s3_data,
        "lightsail": lightsail_data,
        "errors": errors,
    }


def get_all_regions() -> List[str]:
    try:
        ec2 = boto3.client("ec2", region_name="us-east-1")
        regions = ec2.describe_regions()["Regions"]
        return [r["RegionName"] for r in regions]
    except Exception:
        return [get_default_region()]


def scan_all_regions() -> List[Dict[str, Any]]:
    regions = get_all_regions()

    def scan(region: str) -> Dict[str, Any]:
        try:
            return build_scan_payload(region)
        except Exception as exc:
            return {"region": region, "error": str(exc)}

    with ThreadPoolExecutor(max_workers=5) as executor:
        return list(executor.map(scan, regions))


@app.get("/")
def dashboard(request: Request, region: Optional[str] = None):
    payload = build_scan_payload(region)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "data": payload},
    )


@app.get("/api/scan")
def api_scan(region: Optional[str] = None):
    payload = build_scan_payload(region)
    return JSONResponse(content=payload)


@app.get("/api/scan-all")
def api_scan_all():
    return JSONResponse(content=scan_all_regions())


@app.get("/health")
def health():
    return {"status": "ok"}