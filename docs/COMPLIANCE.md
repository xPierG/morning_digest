# Compliance & DORA Documentation

This document outlines the compliance measures and operational resilience strategies for the **Reader Morning Digest** project, in alignment with the Digital Operational Resilience Act (DORA).

## Change Management

All changes to the codebase are tracked via Git.

- **Version Control**: GitHub (or equivalent) is used as the single source of truth.
- **Code Review**: All changes must be reviewed before merging to the `main` branch.
- **Traceability**: Each deployment is linked to a specific commit hash.

### Change Log

| Date | Version | Author | Description |
|------|---------|--------|-------------|
| 2025-11-22 | 0.1.0 | AI Agent | Initial release and documentation setup |

## Incident Management

In the event of a service disruption:

1. **Detection**: Monitoring alerts (Cloud Monitoring) or user reports.
2. **Classification**: Assess severity (Low, Medium, High, Critical).
3. **Response**:
   - Check Cloud Run logs.
   - Rollback to the previous stable revision if necessary.
4. **Post-Mortem**: Analyze the root cause and update this documentation.

## Security Controls

- **Authentication**: Service-to-service authentication via IAM.
- **Secrets Management**: Sensitive data (API keys, passwords) are stored in Secret Manager or environment variables, never in code.
- **Least Privilege**: The Cloud Run service account has only the necessary permissions.

## Business Continuity

- **Redundancy**: Cloud Run automatically handles replication within the region.
- **Backup**: Source code is replicated in the remote repository.
- **Recovery Time Objective (RTO)**: < 1 hour (Redeploy previous version).
- **Recovery Point Objective (RPO)**: N/A (Stateless service).
