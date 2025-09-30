# Microsoft Sentinel Workbooks (Sanitized)

This repository contains a collection of Microsoft Sentinel workbooks in JSON gallery format.  
All workbooks have been sanitized to remove environment-specific identifiers such as:

- Subscription IDs → `PLACEHOLDER_SUBSCRIPTION_ID`
- Tenant IDs → `PLACEHOLDER_TENANT_ID`
- Hostnames → `PLACEHOLDER_HOSTNAME`
- API keys, secrets, tokens → `PLACEHOLDER_KEY_OR_SECRET`

Table names and workbook logic remain intact so the templates can be reused in other environments.

## Usage

- Import any of the JSON files into your Sentinel workbook gallery.  
- Replace the placeholder values with environment-specific details.  
- Modify visualizations or queries as needed for your environment.

## Notes

These workbooks are provided as templates. You must configure data connectors and ensure the required tables exist in your environment for the visualizations to work.
