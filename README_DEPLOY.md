# Deployment Guide for Morning Digest Agent

This guide explains how to deploy your Morning Digest Agent to **Google Cloud Run Jobs**.
This approach is cost-effective (pay-per-use) and fits the periodic nature of the task.

## Prerequisites

1.  **Google Cloud Project**: Ensure you have a GCP project and `gcloud` CLI installed.
2.  **APIs Enabled**: You need to enable Cloud Run, Cloud Build, and Artifact Registry APIs.
    ```bash
    gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
    ```

## Deployment Steps

1.  **Run the deployment script**:
    ```bash
    ./deploy_job.sh
    ```
    This will build your Docker container and deploy the Job definition to Cloud Run.

2.  **Configure Secrets (Crucial!)**:
    The agent needs your API keys to work. You should set them as environment variables in Cloud Run.
    
    Run the following command to update the job with your keys:
    
    ```bash
    gcloud run jobs update morning-digest-agent \
      --region us-central1 \
      --set-env-vars GOOGLE_API_KEY=your_gemini_api_key,READWISE_TOKEN=your_readwise_token
    ```
    
    *(Note: For better security in production, consider using Google Secret Manager, but environment variables are fine for a personal project).*

3.  **Test the Job**:
    ```bash
    gcloud run jobs execute morning-digest-agent --region us-central1
    ```

## Scheduling (Optional)

To have the digest generated automatically every morning (e.g., 7:00 AM Rome time), use Cloud Scheduler:

1.  Create a Service Account for the scheduler:
    ```bash
    gcloud iam service-accounts create scheduler-sa
    ```
    
2.  Grant permission to invoke Cloud Run:
    ```bash
    gcloud run jobs add-iam-policy-binding morning-digest-agent \
        --region us-central1 \
        --member="serviceAccount:scheduler-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/run.invoker"
    ```

3.  Create the Schedule:
    ```bash
    gcloud scheduler jobs create http morning-digest-scheduler \
        --location us-central1 \
        --schedule="0 7 * * *" \
        --time-zone="Europe/Rome" \
        --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/YOUR_PROJECT_ID/jobs/morning-digest-agent:run" \
        --http-method POST \
        --oauth-service-account-email "scheduler-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com"
    ```
