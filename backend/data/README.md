# Parameters Database

This directory expects a file named `parameters.xlsx` used by the document generator to map scraped portal parameters to human-readable instructions.

## Schema
The `parameters.xlsx` file must contain the following columns:

- **parameter_key** (Column A)
- **display_name** (Column B)
- **definition** (Column C): Supports text and bullet points. You can use `{value}` or `{interval}` placeholders.
- **how_it_works** (Column D): Supports text and bullet points.
- **faq** (Column E): Supports Q&A pairs. Start exact questions with "Q1:" to auto-bold them.

If a parameter is scraped from the portal but missing from this Excel file, the document will fallback to portal-scraped descriptions or display "Documentation coming soon".
