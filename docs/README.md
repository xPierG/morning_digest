# Reader Morning Digest - Project Documentation

Welcome to the documentation for the **Reader Morning Digest** project. This repository contains the source code for an AI-powered agent that generates daily digests from various sources.

## Documentation Map

- **[System Architecture](ARCHITECTURE.md)**: Overview of the system components, data flow, and design decisions.
- **[Deployment Guide](DEPLOYMENT.md)**: Instructions for building, deploying, and configuring the application on Google Cloud Run.
- **[Compliance & DORA](COMPLIANCE.md)**: Information regarding regulatory compliance, change management, and operational resilience.
- **[Requirements](REQUIREMENTS.md)**: Functional and non-functional requirements.
- **[Testing Strategy](TESTING.md)**: Testing approach and resilience scenarios.
- **[Risk Assessment](RISK_ASSESSMENT.md)**: Operational risks and mitigation strategies.

## Quick Start

Refer to the main [README](../README.md) in the root directory for development setup and local execution instructions.

## Project Structure

- \`main.py\`: Main entry point for the application.
- \`agents/\`: Directory containing specialized AI agents (`selector.py`, `enricher.py`).
- \`agent.py\`: Pipeline definition.
- \`client.py\`: Client for interacting with external APIs (e.g., Google Gemini).
- \`notification.py\`: Module for handling email notifications.
- \`deploy_job.sh\`: Script for deploying the application to Cloud Run.
