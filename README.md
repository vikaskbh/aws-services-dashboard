# AWS Services Dashboard

A lightweight AWS infrastructure scanner built using FastAPI and boto3 to get real-time visibility into running cloud resources.

This project was built to understand AWS services deeply while preparing for AWS Solutions Architect Associate (SAA) and to create a minimal alternative to heavy monitoring tools.

---

## Preview

<p align="center">
  <img src="assets/aws-service-scan.png" width="800"/>
</p>

## Features

* Scan AWS services in real-time using boto3
* Supports:

  * EC2 Instances
  * RDS Databases
  * Lambda Functions
  * ECS Services
  * S3 Buckets
  * Lightsail Instances
* Region-aware scanning
* Multi-region scan support (optional extension)
* Cost risk indicator (based on active resources)
* Clean UI using Jinja2 templates + charts
* Read-only access (no mutation APIs)

---

## Tech Stack

* FastAPI
* boto3
* Jinja2 (server-side rendering)
* Uvicorn
* Python (venv-based setup)
* AWS IAM (read-only policy)

---

## Project Structure

```
aws-services-dashboard/
├── aws/                # AWS service scanners
├── templates/          # Jinja2 templates
├── static/             # CSS / JS assets
├── main.py             # FastAPI app entry
├── requirements.txt
└── .gitignore
```

---

## Setup (Local)

### 1. Clone repo

```
git clone https://github.com/vikaskbh/aws-services-dashboard.git
cd aws-services-dashboard
```

### 2. Create virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Set environment variables

```
export AWS_ACCESS_KEY_ID=YOUR_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_SECRET
export AWS_DEFAULT_REGION=ap-south-1
```

---

### 5. Run server

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open:

```
http://localhost:8000
```

---

## Deployment (Lightsail / EC2)

* Use systemd to run FastAPI as a service
* Use virtual environment path in ExecStart
* Restrict firewall (port 8000) to your IP
* Store AWS credentials as environment variables
* Prefer IAM roles in production

---

## Security Notes

* Uses read-only AWS APIs (Describe/List only)
* No credentials stored in code
* `.env` files are ignored via `.gitignore`
* Recommended:

  * Rotate IAM keys regularly
  * Use IAM roles instead of access keys for production
  * Sanitize error messages before returning to frontend

---

## API Endpoints

### Dashboard

```
GET /
```

### Scan (single region)

```
GET /api/scan?region=ap-south-1
```

### Scan (all regions)

```
GET /api/scan-all
```

### Health check

```
GET /health
```

---

## Future Improvements

* Multi-region aggregation UI
* Cost estimation (approx AWS billing impact)
* Alerts (email / webhook)
* Authentication (multi-user SaaS version)
* Caching for faster scans
* Pagination support for large accounts

---

## Why this project

Instead of just learning AWS concepts theoretically, this project focuses on:

* Real API usage
* Infrastructure visibility
* Deployment practices (systemd, venv, firewall)
* Security considerations (IAM, least privilege)

---

## License

MIT License

---

## Author

Vikas
https://github.com/vikaskbh
