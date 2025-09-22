# Microsoft Sentinel Workbooks

This folder contains **workbook templates** for Microsoft Sentinel.  
Workbooks provide rich, interactive dashboards for visualizing and analyzing security data in your workspace.

---

## Customization

Before deploying a workbook, replace the following placeholders in the JSON:

- `<SUBSCRIPTION-ID>` → Your Azure subscription ID.  
- `<RESOURCE-GROUP>` → Resource group that contains your Log Analytics workspace.  
- `<WORKSPACE-NAME>` → Name of your Sentinel workspace.  
- `<WORKBOOK-GUID>` → A new GUID for the workbook. You can generate one with PowerShell:  
  ```powershell
  New-Guid
