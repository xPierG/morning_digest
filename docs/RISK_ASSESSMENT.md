# Risk Assessment

This document identifies potential operational risks associated with the **Reader Morning Digest** system and outlines mitigation strategies, as required by DORA for ICT risk management.

## 1. Risk Matrix

| ID | Risk Description | Likelihood | Impact | Severity |
|----|------------------|------------|--------|----------|
| R-01 | **Third-Party API Failure**: Google Gemini API becomes unavailable or changes its interface. | Medium | High | High |
| R-02 | **Cost Overrun**: Excessive API usage or Cloud Run execution time leads to unexpected costs. | Low | Medium | Medium |
| R-03 | **Data Leakage**: Sensitive information is accidentally included in the prompt sent to the LLM. | Low | High | High |
| R-04 | **Delivery Failure**: SMTP server credentials expire or IP is blacklisted. | Low | High | Medium |

## 2. Mitigation Strategies

### R-01: Third-Party API Failure
- **Mitigation**: Implement error handling and retries.
- **Contingency**: Monitor API status. In the long term, abstract the LLM client to support multiple providers (e.g., OpenAI, Anthropic) as backups.

### R-02: Cost Overrun
- **Mitigation**: Set up Google Cloud Budget Alerts.
- **Control**: Configure strict timeouts on the Cloud Run Job.

### R-03: Data Leakage
- **Mitigation**: Review prompts to ensure no PII (Personally Identifiable Information) is included.
- **Control**: The current scope only processes public news/data, minimizing this risk.

### R-04: Delivery Failure
- **Mitigation**: Use a reputable transactional email service (e.g., SendGrid, Mailgun) instead of a generic SMTP if reliability becomes an issue.
- **Monitoring**: Alert on job failure logs.

## 3. Review Cycle

This risk assessment should be reviewed:
- Annually.
- Upon major architectural changes.
- After any significant incident.
