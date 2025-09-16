# Microsoft Sentinel Resources

This repository contains reusable content for Microsoft Sentinel, including:

- **KQL queries** for hunting, detections, and troubleshooting.
- **Analytics rules** for automating alerting and incident creation.
- **Workbooks** for visualizing security data and metrics.
- **Logic Apps (Playbooks)** for incident response automation and integrations.

The goal is to share practical, production-tested content that others can quickly deploy and adapt to their environments.

---

## Repository Structure


- **kql_queries/** – Saved queries organized by type or use case.  
- **analytics_rules/** – JSON templates for analytics rule deployment.  
- **workbooks/** – ARM templates or JSON definitions for custom workbooks.  
- **logic_apps/** – Sanitized templates for Sentinel playbooks and automations.  
- **parsers/** – KQL Functions used to parse logs into a more friendly and usable format.


---

## Usage

1. Clone this repository:
   ```bash
   git clone https://github.com/rich-fleming/microsoft-sentinel.git
