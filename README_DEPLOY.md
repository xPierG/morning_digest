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
    The agent needs your API keys and email credentials to work. You should set them as environment variables in Cloud Run.
    
    **Email Setup (Gmail Example):**
    - Go to your Google Account > Security.
    - Enable 2-Step Verification.
    - Search for "App Passwords" and create one named "Morning Digest".
    - Use that 16-character password below.

    Run the following command to update the job with your keys (replace placeholders):
    
    ```bash
    gcloud run jobs update morning-digest-agent \
      --region us-central1 \
      --set-env-vars="GOOGLE_API_KEY=your_gemini_key,\
    READWISE_TOKEN=your_readwise_token,\
    EMAIL_SENDER_ADDRESS=your_email@gmail.com,\
    EMAIL_SENDER_APP_PASSWORD=your_app_password,\
    EMAIL_RECIPIENT_ADDRESS=recipient@email.com,\
    SMTP_SERVER=smtp.gmail.com,\
    SMTP_PORT=587"
    ```
    
    *(Note: For better security in production, consider using Google Secret Manager, but environment variables are fine for a personal project).*

3.  **Test the Job**:
    ```bash
    gcloud run jobs execute morning-digest-agent --region us-central1
    ```
    Check the Cloud Run logs to verify execution and email delivery.

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

## Troubleshooting Email

- **Authentication Error**: Ensure you are using an **App Password**, not your main Gmail password.
- **Connection Error**: Verify `SMTP_SERVER` (smtp.gmail.com) and `SMTP_PORT` (587).
- **Spam Folder**: Check your spam folder if the email doesn't appear in your inbox.
