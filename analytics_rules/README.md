# Microsoft Sentinel KQL Queries & Analytics Rules

This folder contains **KQL queries** and **Analytics Rules** for Microsoft Sentinel.  
They are designed to accelerate threat detection, hunting, and incident response.

---

## What’s Inside

- **KQL Queries**  
  - Useful for hunting, threat investigations, and validation.  
  - Typically stored as `.kql` or `.txt` files.  
  - Can be run directly in the Sentinel Logs blade or reused in analytics rules.  

- **Analytics Rules (ARM Templates)**  
  - JSON templates for scheduled detection rules.  
  - Each rule includes metadata such as severity, description, tactics/techniques, and entity mappings.  
  - Rules are built to be **parameterized** so they can be deployed in different environments.  

---

## Customization

Before deploying rules from this folder, check for:

- **Rule IDs (GUIDs)**  
  - Some templates include generated GUIDs for `alertRules/<GUID>`.  
  - Replace with your own GUID or let Sentinel generate one at deployment.

- **Display Names / Descriptions**  
  - Update names to align with your organization’s naming standards.  
  - Ensure descriptions match your environment and intended use.

- **Query Logic**  
  - Many rules contain KQL that references vendor names (e.g., “Palo Alto Networks”).  
  - These are safe to share publicly, but adapt them if you use different log sources.  
  - Some queries include **placeholders** (e.g., `<primary-indicator>` or `<HA-naming>`) that must be updated to reflect your environment.

- **CustomDetails / EntityMappings**  
  - Check the `customDetails` and `entityMappings` sections to make sure fields map correctly in your data.  

---

## Deployment

### Deploy an Analytics Rule

Use Azure CLI or ARM deployment:

```bash
az deployment group create \
  --resource-group <your-resource-group> \
  --template-file <RuleFile>.json \
  --parameters workspace=<your-workspace-name>
