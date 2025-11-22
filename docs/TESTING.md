# Testing Strategy

This document defines the testing approach for the **Reader Morning Digest** project, with a focus on ensuring reliability and compliance with DORA resilience testing requirements.

## 1. Test Levels

### 1.1. Unit Testing
- **Scope**: Individual functions and classes (e.g., `Agent.generate_digest`, `NotificationManager._convert_to_html`).
- **Tools**: `unittest` or `pytest`.
- **Goal**: Verify logic in isolation. Mocks are used for external dependencies (Gemini API, SMTP).

### 1.2. Integration Testing
- **Scope**: Interaction between modules (e.g., `main.py` calling `agent.py`).
- **Goal**: Verify that components work together correctly.

### 1.3. End-to-End (E2E) Testing
- **Scope**: Full execution of the job.
- **Environment**: Staging (Cloud Run).
- **Goal**: Verify the complete flow from trigger to email delivery.

## 2. Resilience Testing (DORA)

To ensure operational resilience, the following scenarios should be tested periodically:

### 2.1. Dependency Failure
- **Scenario**: The LLM API is unavailable or returns a 500 error.
- **Expected Behavior**: The application should log the error and exit with a non-zero status code (allowing Cloud Run/Scheduler to handle retries or alerting).
- **Test Method**: Mock the API client to raise an exception.

### 2.2. Network Partition
- **Scenario**: SMTP server is unreachable.
- **Expected Behavior**: The application should fail gracefully and log the connection error.

## 3. Execution

### Running Unit Tests
```bash
python -m unittest discover tests
```

### Manual Verification Checklist
- [ ] Deploy to a staging Cloud Run Job.
- [ ] Trigger the job manually.
- [ ] Verify email receipt.
- [ ] Verify logs in Cloud Logging.
