# Microsoft Sentinel Logic Apps (Playbooks)

This folder contains **Logic Apps (Sentinel Playbooks)** that automate incident response and enrich detection workflows in Microsoft Sentinel.  
Each Logic App is published here as a sanitized ARM template that you can customize and deploy in your own environment.

---

## What’s Inside

- **Sanitized Playbook Templates**  
  - Templates are stripped of sensitive values such as subscription IDs, resource group names, connection IDs, and internal site identifiers.  
  - Secret names and connection names are either generic or parameterized.  
  - Example: `BrivoEventsIngest.json` shows how to structure a secure playbook without exposing tenant-specific values.  

- **Examples of Playbook Use Cases**  
  - Enrich incidents with external threat intelligence.  
  - Send alerts to collaboration platforms (Teams, Slack, etc.).  
  - Block IP addresses or accounts through integrations.  
  - Ingest 3rd party security logs into Sentinel.  

---

## Customization

Before deploying any Logic App from this folder, review and update the following:

- **Connections**  
  - `$connections` objects are published empty. You must configure them during or after deployment (e.g., Key Vault, Log Analytics, Microsoft Teams, etc.).

- **Parameters**  
  - Replace placeholders like `<REGION>`, `<RESOURCE-GROUP>`, `<SUBSCRIPTION-ID>`, `<RULE-GUID>`, `<INTERNAL-RANGE>` with values from your environment.  
  - Update default values such as `LogType`, `BrivoSiteID`, or base URLs if provided.  

- **Secrets**  
  - Secret retrieval actions (e.g., `Get_User`, `Get_Password`) assume you’re using **Azure Key Vault**.  
  - You must create corresponding secrets in your own Key Vault instance.  

- **Secure Data**  
  - For HTTP actions handling tokens or credentials, ensure `runtimeConfiguration.secureData` is enabled to prevent token leakage in run history.  

---

## Deployment

You can deploy a Logic App template via the Azure CLI:

```bash
az deployment group create \
  --resource-group <your-resource-group> \
  --template-file <LogicAppTemplate>.json \
  --parameters @parameters.json
