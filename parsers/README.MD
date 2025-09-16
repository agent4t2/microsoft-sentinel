# Microsoft Sentinel Parsers

This folder contains reusable **parser functions** for Microsoft Sentinel. Parsers are implemented as **Saved Searches** with the `Parser` category and can be referenced in KQL queries, analytics rules, and workbooks to simplify log normalization.

---

## What’s Inside

- **SyslogSDWAN** – Example parser for normalizing SD-WAN syslog events.  
  - Supports both key/value and delimited message formats.  
  - Extracts fields like `ION_HOST`, `DEVICE_TIME`, `SrcIP`, `DstIP`, `Protocol`, `App`, etc.  
  - Includes logic for excluding specific internal ranges and handling custom host prefixes.  

---

## Customization

Before deploying these parsers, update the following placeholders in the KQL:

- `<SDWAN-PREFIX>`  
  Replace with the hostname prefix your SD-WAN devices use (e.g., `sdwan-` or `edge-`).  

- `<INTERNAL-RANGE-1>` … `<INTERNAL-RANGE-5>`  
  Replace with internal subnets you want to exclude from processing.  
  Example:  
  ```kql
  | where Computer !startswith "10.10."
