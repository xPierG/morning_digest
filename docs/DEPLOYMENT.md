# Deployment Guide

This document details the deployment process for the **Reader Morning Digest** application on Google Cloud Run.

## Prerequisites

- Google Cloud Platform (GCP) Project
- `gcloud` CLI installed and authenticated
- Docker (for local building/testing)

## Configuration

The application relies on the following environment variables, which must be set in the `.env` file or configured in the Cloud Run Job:

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | API key for Google Gemini |
| `SMTP_SERVER` | Hostname of the SMTP server |
| `SMTP_PORT` | Port for the SMTP server (e.g., 587) |
| `SMTP_USERNAME` | Username for SMTP authentication |
| `SMTP_PASSWORD` | Password for SMTP authentication |
| `EMAIL_FROM` | Sender email address |
| `EMAIL_TO` | Recipient email address |

## Deployment Script

The project includes a helper script `deploy_job.sh` to automate the deployment process.

### Usage

```bash
./deploy_job.sh
```

### What the script does

1. **Builds the Docker Image**: Uses `gcloud builds submit` to build the container image from the `Dockerfile`.
2. **Deploys to Cloud Run**: Creates or updates a Cloud Run Job named `reader-morning-digest-job`.
   - Sets the region (default: `us-central1`).
   - Configures environment variables from the local `.env` file.

## Manual Deployment Steps

If you prefer to deploy manually or need to customize the process:

1. **Build Image**:
   ```bash
   gcloud builds submit --tag gcr.io/[PROJECT_ID]/reader-morning-digest
   ```

2. **Create Job**:
   ```bash
   gcloud run jobs create reader-morning-digest-job \
     --image gcr.io/[PROJECT_ID]/reader-morning-digest \
     --region us-central1
   ```

3. **Execute Job**:
   ```bash
   gcloud run jobs execute reader-morning-digest-job --region us-central1
   ```

## Scheduling

To run the job automatically (e.g., every morning), use Cloud Scheduler:

```bash
gcloud scheduler jobs create http morning-digest-trigger \
  --location us-central1 \
  --schedule "0 8 * * *" \
  --uri "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/[PROJECT_ID]/jobs/reader-morning-digest-job:run" \
  --http-method POST \
  --oauth-service-account-email [SERVICE_ACCOUNT_EMAIL]
```
