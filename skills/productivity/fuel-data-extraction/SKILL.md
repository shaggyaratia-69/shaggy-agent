---
name: fuel-data-extraction
description: "Extract, normalize, and audit fuel-station data from portals, Firecrawl/web pages, PDFs, invoices, CSV/XLSX files, emails, and screenshots."
version: 1.0.0
license: Customer-safe
metadata:
  shaggy:
    tags: [fuel, data-extraction, firecrawl, web-scraping, invoices, pdf, csv]
---

# Fuel Data Extraction and Firecrawl/Web Workflow

Use this skill when the user needs fuel data scraped, downloaded, OCR'd, normalized, or turned into a report.

## Sources Shaggy can handle

- Vendor portals such as fuel pricing, invoices, delivery history, drafts/payments, orders, and statements.
- Public web pages and competitor price pages.
- Firecrawl/API extraction when configured by the customer.
- PDFs and scanned documents.
- CSV/XLSX exports.
- Emails and attachments, after the user authorizes the mailbox/account.
- Screenshots/images using vision/OCR tools.

## Extraction rules

1. Save raw source files first for audit.
2. Normalize into CSV/JSON/XLSX second.
3. Keep one folder per customer/location/year/task.
4. Record source URL/file, extraction time, row counts, totals, and failures.
5. Never treat a failed/empty export as proof of no data until verified.
6. For PDFs, verify file signature and page count when possible.
7. Do not print secrets/tokens/session cookies in logs or reports.

## Firecrawl/web extraction

Use Firecrawl or another configured web extraction tool when:
- the page is public or the customer authorizes authenticated scraping,
- browser snapshots are insufficient,
- many pages must be crawled consistently,
- structured markdown/HTML extraction is helpful.

Do not bypass paywalls, terms, or access controls. For authenticated portals, use the customer's active session or approved export/API path.

## Local folder template

```text
fuel_work/
  [location]/
    [year]/
      raw_exports/
      normalized/
      reports/
      logs/
      manifests/
```

## Output

For each extraction run, produce:
- raw files saved,
- normalized files saved,
- row counts/totals,
- exceptions/failures,
- what is safe to use for decisions.
