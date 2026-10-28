# DateWithStranger — MCP & Skill Inventory (Phase 0)

This document audits all Model Context Protocol (MCP) servers, tools, and Antigravity skills required for the development, database management, and maintenance of the **DateWithStranger** system.

---

## 1. MCP Server Inventory

### MCP: `supabase`
* **Purpose**: Native Supabase database operations, SQL execution, migration management, schema inspection, and environment validation.
* **Required**: `Yes`
* **Capabilities**:
  * `execute_sql`: Direct DDL/DML execution for running migrations or querying schema.
  * `list_tables` / `list_migrations`: Inspect current database structure.
  * `apply_migration`: Apply SQL schema files directly to Supabase projects.
  * `get_project` / `list_projects`: Fetch project metadata and reference keys.
  * `search_docs`: Query official Supabase documentation for exact syntax & features.
* **Authentication**: Personal Access Token (PAT) / OAuth bearer token.
* **Permissions**: Database Admin / Project Developer permissions.
* **Phase**: Phase 0 (Discovery & Validation) & Phase 2+ (Database Implementation).
* **Install/setup instructions**:
  1. Configure Supabase credentials in local environment.
  2. Register MCP server in IDE / Antigravity MCP settings.
  3. Authenticate via Supabase Dashboard access token.
* **Security concerns**: `execute_sql` has database owner access. Service role keys and access tokens must remain local and never be logged or committed.

---

### MCP: `playwright` / `chrome-devtools-mcp`
* **Purpose**: Web browser automation, testing public web landing pages (`website/index.html`), validating webhooks, and simulating web admin dashboard interactions.
* **Required**: `Recommended`
* **Capabilities**:
  * `browser_navigate` / `navigate_page`: Load web pages locally or on staging.
  * `browser_take_screenshot`: Capture visual state of website layout.
  * `browser_evaluate`: Inspect DOM, console logs, and JavaScript execution.
* **Authentication**: None required for local pages; session cookies for admin portals.
* **Permissions**: Local headless browser control.
* **Phase**: Phase 0 (Verification) & Phase 4 (Website / Web UI testing).
* **Install/setup instructions**: Automatically available in Antigravity environment.
* **Security concerns**: Ensure browser context does not navigate to untrusted external domains with active auth headers.

---

### MCP: `clickhouse`
* **Purpose**: Big Data analytics queries (if ClickHouse is added for long-term historical log archiving).
* **Required**: `NOT NEEDED`
* **Capabilities**: Select queries on ClickHouse database instances.
* **Authentication**: Service credentials.
* **Permissions**: Read-only.
* **Phase**: N/A (Supabase PostgreSQL handles analytics in current architecture via `daily_statistics` table).
* **Install/setup instructions**: N/A.
* **Security concerns**: N/A.

---

## 2. Antigravity Skill Inventory

### Skill: `agy-customizations`
* **Purpose**: Guide for customizing Antigravity environment rules, skills, plugins, and hooks.
* **Required**: `Yes`
* **Why needed**: Enforces workspace configuration guidelines and ensures all tools adhere to standards.
* **Phase**: Phase 0.
* **Install command/process**: Built-in Antigravity skill (`C:\Users\aman aryal\.gemini\antigravity-ide\builtin\skills\agy-customizations\SKILL.md`).
* **Authentication**: Local filesystem access.

---

### Skill: `antigravity-guide`
* **Purpose**: Comprehensive sitemap and usage guide for Antigravity CLI and IDE features.
* **Required**: `Yes`
* **Why needed**: Reference for executing agentic workflows, background commands, and file operations efficiently.
* **Phase**: Phase 0.
* **Install command/process**: Built-in Antigravity skill (`C:\Users\aman aryal\.gemini\antigravity-ide\builtin\skills\antigravity_guide\SKILL.md`).
* **Authentication**: Local filesystem access.
