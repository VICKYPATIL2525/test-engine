# Testing Engine - AI-Powered Test Failure Analysis

An AI-powered tool that analyzes test execution reports and git commit history using **Azure OpenAI GPT-4** to identify root causes of test failures, correlate them with code changes, and provide actionable fix recommendations.

---

## What Is This?

This is a **QA Test Analysis Engine** — a Python-based tool that acts as an intelligent QA assistant. You give it two things:

1. **Your commit history** — extracted from any GitHub repository (who changed what, when, and where)
2. **Your test reports** — HTML reports from test runs (which tests passed, which failed, error logs)

It feeds both into **Azure OpenAI GPT-4** which reads through everything and tells you:
- **What failed** — exact test name, step, and scenario
- **Why it failed** — root cause with error message explanation
- **Which commit caused it** — correlates failures with recent code changes
- **Where in the code** — exact file name and line number from stack traces
- **How to fix it** — specific, actionable recommendations

**In short:** Instead of manually digging through test reports and git logs for hours, this tool does it in **10 seconds** and gives you a structured report you can directly use for bug tickets, stand-ups, or code reviews.

### Example

You run `python app.py` and get:

> **Root Cause:** LoginSteps.java line 182 — XPath locator `//a[contains(.,'Projects')]` matches 5 elements instead of 1. Playwright strict mode requires unique locators.
>
> **Introduced By:** Commit `6135232` — "Create locators.properties" by Neha Verma on Feb 3, 2026.
>
> **Fix:** Use `getByRole(link, {name: "Projects", exact: true})` instead of the ambiguous XPath.

That's it. From raw HTML reports + git history → actionable intelligence, fully automated.

---

- [How It Works](#how-it-works)
- [LLM Configuration](#llm-configuration)
- [Input Data](#input-data)
- [Output](#output)
- [Sample Analysis Output](#sample-analysis-output)
- [Environment Optimization](#environment-optimization)
- [Development History](#development-history)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project takes two inputs:

1. **Git commit history** (extracted from a GitHub repository)
2. **HTML test reports** (SparkReports from Playwright/Cucumber BDD test runs)

It sends both to **Azure OpenAI GPT-4.1-mini** which analyzes the data and returns:

- Root cause analysis of test failures
- Commit correlation (which code change caused the failure)
- Exact file/line references from stack traces
- Error message explanations
- Actionable fix recommendations
- Patterns and trends

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    TESTING ENGINE                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐     ┌──────────────────────┐           │
│  │  pulled_data/    │     │  html-reports/        │           │
│  │  (commits JSON)  │     │  (raw HTML reports)   │           │
│  └────────┬────────┘     └──────────┬───────────┘           │
│           │                         │                        │
│           ▼                         ▼                        │
│  ┌──────────────────────────────────────────────┐           │
│  │              app.py                           │           │
│  │         LLMTestAnalyzer                       │           │
│  │                                               │           │
│  │  1. Load commit data (JSON)                   │           │
│  │  2. Load raw HTML reports                     │           │
│  │  3. Prepare context                           │           │
│  │  4. Send to Azure OpenAI GPT-4               │           │
│  │  5. Display + save results                    │           │
│  └────────────────────┬─────────────────────────┘           │
│                       │                                      │
│                       ▼                                      │
│              ┌─────────────────┐                            │
│              │ Azure OpenAI    │                            │
│              │ GPT-4.1-mini    │                            │
│              └────────┬────────┘                            │
│                       │                                      │
│                       ▼                                      │
│              ┌─────────────────┐                            │
│              │ llm_analysis.json│                            │
│              │ (analysis output)│                            │
│              └─────────────────┘                            │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  Optional: git_extractor.py                                  │
│  (Extract commit data from new GitHub repositories)          │
└──────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
testing-engin/
├── app.py                          # Main application - LLM-powered CLI analysis engine
├── strapp.py                       # Streamlit web UI for interactive analysis
├── git_extractor.py                # Git repository data extractor (optional, run once)
├── requirements.txt                # Full dependencies (original, includes extras)
├── requirements-minimal.txt        # Minimal dependencies (optimized, recommended)
├── .env                            # Azure OpenAI credentials (DO NOT COMMIT)
├── .env.example                    # Template for environment variables
├── .gitignore                      # Git exclusion rules
├── README.md                       # This file
├── LIBRARY_AUDIT.md                # Detailed library audit report
├── ENVIRONMENT_COMPARISON.md       # Environment optimization comparison
│
├── html-reports/                   # Input: HTML test reports
│   ├── run1_TestRunReport.html     # Test Run 1 (PASSED - 11.42 KB)
│   └── run2_TestRunReport.html     # Test Run 2 (FAILED - 32.07 KB)
│
├── pulled_data/                    # Input: Extracted git data
│   └── QA_Playwright_Repo_20260210_163229/
│       ├── commits_detailed.json   # 14 commits with full diffs
│       ├── branches.json           # Branch information
│       ├── contributors.json       # Contributor statistics
│       ├── repository_info.json    # Repo metadata
│       ├── commits_summary.csv     # Commit summary table
│       ├── contributors.csv        # Contributors table
│       ├── file_summary.csv        # File change summary
│       ├── file_history.json       # File change history
│       ├── extraction_stats.json   # Extraction metadata
│       └── preprocessed/           # Preprocessed data files
│
├── llm_analysis.json               # Output: Latest AI analysis results
│
├── venv/                           # Python virtual environment (optimized, 37 packages)
├── myenv/                          # Legacy environment (backup, 97 packages)
│
├── SparkReports 5-Feb-26 11-24-08/ # Original test reports (raw, kept as backup)
│   ├── SparkReports 5-Feb-26 11-24-08/  # Run 1 reports
│   └── SparkReports 5-Feb-26 11-27-41/  # Run 2 reports
│
└── temp_repos/                     # Temporary cloned repositories
```

### File Descriptions

| File | Purpose | Status |
|------|---------|--------|
| `app.py` | Main CLI analysis engine using Azure OpenAI | **Active** |
| `strapp.py` | Streamlit web UI for interactive analysis | **Active** |
| `git_extractor.py` | Extracts commit data from GitHub repos using GitPython | Optional |
| `requirements-minimal.txt` | Minimal pip dependencies for app.py | **Recommended** |
| `requirements.txt` | Full dependency list (includes unused libs) | Legacy |
| `.env` | Azure OpenAI API credentials | Required |
| `.env.example` | Template for .env setup | Reference |
| `llm_analysis.json` | AI-generated analysis output | Output |

---

## Setup Guide

### Prerequisites

- Python 3.10+ installed
- Azure OpenAI API access (API key, endpoint, deployment)
- Git (optional, only for git_extractor.py)

### Step 1: Create Virtual Environment

```powershell
cd C:\Users\vicky\OneDrive\Desktop\testing-engin

# Create environment
python -m venv venv

# Activate environment
.\venv\Scripts\Activate.ps1

# You should see (venv) in your prompt
```

### Step 2: Install Dependencies

```powershell
# Recommended: minimal install (4 packages, ~50 MB)
pip install -r requirements-minimal.txt

# Alternative: full install (includes extras, ~250 MB)
pip install -r requirements.txt
```

**Packages installed (minimal):**

| Package | Version | Purpose |
|---------|---------|---------|
| `openai` | >=1.12.0 | Azure OpenAI Python SDK |
| `langchain-openai` | >=0.0.5 | LangChain Azure integration |
| `langchain-core` | >=0.1.0 | LangChain core messaging |
| `python-dotenv` | >=1.0.0 | Load .env credentials |

### Step 3: Configure Azure OpenAI Credentials

Create a `.env` file (or edit the existing one):

```env
# Azure OpenAI Configuration
OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_VERSION=2024-12-01-preview

# GitHub (optional, only for git_extractor.py)
GITHUB_TOKEN=your_github_token_here
REPO_URL=https://github.com/your-org/your-repo.git
```

### Step 4: Prepare Input Data

**Commit Data** — already extracted in `pulled_data/`:
```
pulled_data/QA_Playwright_Repo_20260210_163229/commits_detailed.json
```

**Test Reports** — place HTML files in `html-reports/`:
```
html-reports/run1_TestRunReport.html
html-reports/run2_TestRunReport.html
```

> **Note:** To extract from a new repository, run `python git_extractor.py`.
> To add new test reports, copy HTML files into `html-reports/` with a clear naming convention (e.g., `run3_Report.html`).

### Step 5: Run the Analysis

```powershell
python app.py
```

### Step 6: View Results

- **Terminal** — analysis prints directly to console
- **File** — full results saved to `llm_analysis.json`

---

## Usage

### Quick Start (5 commands)

```powershell
.\venv\Scripts\Activate.ps1           # Activate environment
pip install -r requirements-minimal.txt # Install dependencies (first time only)
notepad .env                            # Set Azure credentials (first time only)
python app.py                           # Run analysis
code llm_analysis.json                  # View results
```

### Streamlit Web UI

```powershell
.\venv\Scripts\Activate.ps1           # Activate environment
streamlit run strapp.py               # Launch web interface
```

The Streamlit UI provides:
- **Dashboard** — commit metrics, report stats, and contributor counts at a glance
- **AI Analysis tab** — one-click Azure OpenAI analysis with configurable parameters
- **Commits tab** — searchable commit history with expandable diffs and file changes
- **Test Reports tab** — rendered HTML report viewer + raw source toggle
- **History tab** — view and download previous analysis results
- **Sidebar** — dataset selection, LLM settings (temp, tokens, commit count), credential status

Default URL: `http://localhost:8501`

---

### Adding New Test Reports

```powershell
# Copy new HTML report into html-reports/
copy "C:\path\to\new_report.html" html-reports\run3_Report.html

# Re-run analysis
python app.py
```

### Extracting Data from a New Repository

```powershell
# Edit .env with new REPO_URL and GITHUB_TOKEN
notepad .env

# Run extractor
python git_extractor.py

# Then run analysis
python app.py
```

---

## How It Works

### app.py — LLMTestAnalyzer Class

```
1. __init__()
   └── Creates Azure OpenAI connection (GPT-4.1-mini)

2. load_commit_data()
   └── Reads commits_detailed.json (last 30 commits)

3. load_test_reports()
   └── Reads ALL .html files from html-reports/ folder (raw, no parsing)

4. prepare_analysis_context()
   └── Combines commit summaries + raw HTML into structured context

5. analyze_with_llm()
   └── Sends to Azure OpenAI with expert QA prompt
   └── Returns: root causes, commit correlation, fix recommendations

6. save_analysis()
   └── Saves everything to llm_analysis.json
```

### Why Raw HTML?

We send the **raw HTML reports directly** to the LLM instead of pre-parsing them because:

- **Zero data loss** — no crucial info missed by regex parsing
- **Small size** — both reports total ~43 KB (well within GPT-4's 128K token limit)
- **LLM capability** — GPT-4 can read HTML and extract test data, errors, stack traces
- **Simpler code** — no BeautifulSoup, lxml, or regex parsing needed

---

## LLM Configuration

```python
llm = AzureChatOpenAI(
    deployment_name="gpt-4.1-mini",
    model_name="gpt-4.1-mini",
    temperature=0.1,          # Low temperature = deterministic, focused analysis
    max_tokens=1500,           # Sufficient for complete analysis with recommendations
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_VERSION"),
    api_key=os.getenv("OPENAI_API_KEY"),
    azure_deployment="gpt-4.1-mini"
)
```

### Parameters

| Parameter | Value | Reason |
|-----------|-------|--------|
| `model` | gpt-4.1-mini | Fast, cost-effective, handles code/HTML well |
| `temperature` | 0.1 | Deterministic, factual output |
| `max_tokens` | 1500 | Complete analysis + root cause + recommendations |
| `api_version` | 2024-12-01-preview | Latest Azure API |

### Token History

| Version | max_tokens | Result |
|---------|-----------|--------|
| v1 | 500 | Truncated — missing recommendations and patterns sections |
| v2 (current) | 1500 | Complete — all 6 analysis sections fully generated |

---

## Input Data

### Commit History

**Source:** QA_Playwright_Repo (GitHub)  
**Extracted:** February 10, 2026  
**Commits:** 14  
**Contributors:** 2 (Neha Verma, Rohit Singh Shekhawat)  
**Framework:** Java, Playwright, Cucumber BDD, TestNG  

**Key files in repository:**
- `src/test/features/login.feature` — BDD test scenarios (Gherkin)
- `src/test/java/stepDefinitions/LoginSteps.java` — Test implementation
- `src/test/resources/repository/locators.properties` — Element selectors
- `src/test/java/utilities/BaseClass.java` — Locator handling
- `src/test/java/stepDefinitions/CommonSteps.java` — Shared steps

### Test Reports

**Source:** SparkReports (ExtentReports Spark HTML format)  
**Test Framework:** Playwright Java + Cucumber BDD + TestNG  
**Application Under Test:** InsureCRM

| Report | Timestamp | Tests | Status | Size |
|--------|-----------|-------|--------|------|
| run1_TestRunReport.html | Feb 5, 2026 11:24:08 AM | 2 scenarios | ALL PASSED | 11.42 KB |
| run2_TestRunReport.html | Feb 5, 2026 11:27:41 AM | 3 scenarios | 1 FAILED | 32.07 KB |

**Test Scenarios:**
- `@SMOKE` — Validate login with valid credentials → PASSED (both runs)
- `@PROJECT` — Create a new project after login (QA) → PASSED (Run 1), FAILED (Run 2)

---

## Output

### Console Output

```
================================================================================
LLM-POWERED TEST ANALYSIS ENGINE
================================================================================

✓ Commits Loaded: 14
✓ Test Reports: 2

================================================================================
DATA SUMMARY
================================================================================

📊 Commits: 14
📊 Test Reports: 2

Test Report Files:
  • run1_TestRunReport.html (11.42 KB)
  • run2_TestRunReport.html (32.07 KB)

📊 Total Report Size: 43.49 KB

================================================================================
ANALYZING WITH AZURE OPENAI...
================================================================================

[... GPT-4 analysis output ...]

✓ Analysis saved to: llm_analysis.json

================================================================================
✓ ANALYSIS COMPLETE
================================================================================
```

### llm_analysis.json Structure

```json
{
  "timestamp": "2026-02-12T13:45:15.123456",
  "commits_analyzed": 14,
  "reports_analyzed": 2,
  "llm_analysis": "... GPT-4's complete analysis text ...",
  "raw_data": {
    "commits": [ ... last 30 commits with diffs ... ],
    "test_reports": [ ... raw HTML content ... ]
  }
}
```

---

## Sample Analysis Output

The LLM generates a structured analysis with 6 sections:

### 1. Root Cause Analysis
- Run 1: All tests passed
- Run 2: "Create a new project after login (QA)" FAILED
- Failure at step: "When User navigates to the Projects page"
- Error: Playwright strict mode violation — XPath locator matches 5 elements instead of 1

### 2. Commit Correlation
- All commits by Neha Verma on Feb 3, 2026
- "Create locators.properties" commit likely introduced the problematic XPath
- Related commits: CommonPage.java, CommonSteps.java, LoginSteps.java

### 3. File/Line References
- `LoginSteps.java:182` — `user_navigates_to_projects_page()` method
- `LoginSteps.java:177` — Locator definition
- Locator: `//a[contains(.,'Projects') or contains(@href,'projects')]`

### 4. Error Explanation
- **Error:** `strict mode violation: locator resolved to 5 elements`
- **Meaning:** Playwright strict mode requires locators to match exactly 1 element
- **5 matching elements:**
  1. Main "Projects" nav link
  2. "Create Project" link
  3. "View All" link
  4. "Create New Project" card
  5. "Manage Projects" card

### 5. Fix Recommendations
- Refine XPath to target unique element (use exact text or CSS class)
- Use Playwright `getByRole` with exact name matching
- Add locator validation before interactions
- Audit all step definitions for similar ambiguous locators

### 6. Patterns & Trends
- Simple login test passes; complex navigation test fails
- Locator design is the root issue, not application bugs
- Generic commit messages make debugging harder
- Navigation and creation flows need robust locator strategies

---

## Environment Optimization

### Background

During development, multiple libraries were installed for experimentation (Anthropic Claude, Flask, pandas, BeautifulSoup, etc.). An optimization was performed to reduce bloat.

### Results

| Metric | myenv (old) | venv (optimized) | Improvement |
|--------|-------------|-------------------|-------------|
| **Packages** | 97 | 37 | 62% fewer (-60 packages) |
| **Size** | 250.66 MB | 50.37 MB | **79.9% smaller** (-200.29 MB) |
| **Functionality** | Works | Works | 100% preserved |
| **Install time** | ~5 min | ~1 min | 80% faster |

### What Was Removed

| Category | Packages Removed | Space Saved |
|----------|-----------------|-------------|
| pandas + numpy | 2 | ~90 MB |
| HTML/PDF (weasyprint, bs4, lxml, pillow) | 15 | ~50 MB |
| Flask + web frameworks | 8 | ~15 MB |
| Anthropic (wrong provider) | 2 | ~10 MB |
| Testing (pytest, coverage) | 6 | ~15 MB |
| LangGraph ecosystem | 4 | ~15 MB |
| Async HTTP (aiohttp) | 7 | ~10 MB |

### Environments

| Environment | Use | Status |
|-------------|-----|--------|
| `venv/` | **Production** — optimized, minimal, use this | Active |
| `myenv/` | **Backup** — full install, kept temporarily | Legacy |

> **Recommendation:** Use `venv` for all work. Delete `myenv` after confirming stability.

Full audit details: [LIBRARY_AUDIT.md](LIBRARY_AUDIT.md) | [ENVIRONMENT_COMPARISON.md](ENVIRONMENT_COMPARISON.md)

---

## Development History

### Timeline

| Date | Revision | Changes |
|------|----------|---------|
| **Feb 10, 2026** | v0.1 — Initial Setup | Created git_extractor.py, data_preprocessor.py, run_pipeline.py, extract.py, config.json. Extracted commit data from QA_Playwright_Repo (14 commits). |
| **Feb 12, 2026** | v0.2 — Anthropic Attempt | Created app.py with LangChain + Anthropic Claude. Hit installation issues (lxml build failure requiring Visual C++). Created test_llm_connection.py, verify_installation.py. |
| **Feb 12, 2026** | v0.3 — Azure OpenAI Switch | Reverted from Anthropic to Azure OpenAI. Updated app.py to use AzureChatOpenAI with gpt-4.1-mini. Configured .env with Azure credentials. |
| **Feb 12, 2026** | v0.4 — Regex Parsing | Created analyze.py as a standalone tool using built-in Python (regex) to parse HTML reports. No external API needed. Successfully identified test failures. |
| **Feb 12, 2026** | v0.5 — Raw HTML Approach | Decided to send raw HTML reports directly to LLM instead of parsing. Removed regex/BeautifulSoup parsing from app.py. Copied SparkReports HTML files to html-reports/ folder (run1_, run2_ prefix). |
| **Feb 12, 2026** | v0.6 — Token Optimization | Increased max_tokens from 500 to 1500. First run with 500 tokens was truncated (missing recommendations). 1500 tokens produces complete 6-section analysis. |
| **Feb 12, 2026** | v0.7 — Environment Optimization | Audited 97 installed packages. Created venv with only 37 required packages. Saved 200 MB (79.9% reduction). Created requirements-minimal.txt. |
| **Feb 12, 2026** | v0.8 — Cleanup | Removed unused files: analyze.py, analysis_data.json, data_preprocessor.py, run_pipeline.py, extract.py, config.json, __pycache__/, test_llm_connection.py, verify_installation.py. Kept git_extractor.py (optional). |
| **Feb 20, 2026** | v0.9 — Documentation | Comprehensive README update with full project documentation, setup guide, architecture, development history, and optimization details. |

### Key Decisions

| Decision | Why | Result |
|----------|-----|--------|
| **Azure OpenAI over Anthropic** | User already had Azure credentials; lxml/bs4 install failures with Anthropic approach | Smooth integration, no build issues |
| **Raw HTML over parsing** | Regex missed step-by-step execution details, stack traces. Total HTML is only 43 KB | Zero data loss, simpler code, LLM handles extraction perfectly |
| **max_tokens 1500 over 500** | 500 tokens truncated the recommendations and patterns sections | Complete analysis with all 6 sections |
| **Minimal venv over bloated myenv** | 60 packages unused, 200 MB wasted | 79.9% size reduction, same functionality |
| **Last 30 commits over 10** | More context for the LLM to correlate changes | Better commit-to-failure correlation |

### Files Created & Removed During Development

**Created then removed:**
- `analyze.py` — Standalone regex analysis (replaced by LLM approach in app.py)
- `analysis_data.json` — Output from analyze.py (replaced by llm_analysis.json)
- `data_preprocessor.py` — Data preprocessing (not needed, app.py loads raw data)
- `run_pipeline.py` — Pipeline runner (not needed, single script workflow)
- `extract.py` — Data extraction (redundant with git_extractor.py)
- `config.json` — Config file (replaced by .env)
- `extract_reports_helper.py` — Folder extraction script (replaced by simple HTML copy)
- `test_llm_connection.py` — API connection test (one-time use)
- `verify_installation.py` — Package verification (one-time use)
- `requirements-core.txt` — Intermediate requirements (consolidated)
- `INSTALL.md` — Installation guide (merged into README)

---

## Troubleshooting

### "Module not found" Error

```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements-minimal.txt
```

### "Azure OpenAI authentication failed"

```powershell
# Check .env credentials
notepad .env

# Verify these are set correctly:
# OPENAI_API_KEY=your_actual_key
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_VERSION=2024-12-01-preview
```

### "No test reports found"

```powershell
# Verify html-reports folder has HTML files
Get-ChildItem .\html-reports\

# Expected:
# run1_TestRunReport.html
# run2_TestRunReport.html
```

### "Commits file not found"

```powershell
# Verify pulled_data exists
Get-ChildItem .\pulled_data\

# If missing, extract repository data
python git_extractor.py
```

### Truncated Analysis Output

```python
# In app.py, increase max_tokens:
max_tokens=1500    # Current (recommended)
max_tokens=2000    # If analysis still gets cut off
```

### Environment Issues

```powershell
# If venv has issues, fall back to myenv (backup)
.\myenv\Scripts\Activate.ps1
python app.py

# Or recreate venv from scratch
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-minimal.txt
```

---

## Current Test Data Summary

**Repository:** QA_Playwright_Repo  
**Commits:** 14 (by Neha Verma and Rohit Singh Shekhawat, Feb 3, 2026)  
**Test Runs:** 2 (Feb 5, 2026)  
**Application:** InsureCRM (Login + Project Management)  
**Test Framework:** Java, Playwright, Cucumber BDD, TestNG, ExtentReports  

**Known Failure:**
- **Test:** "Create a new project after login (QA)"
- **Root Cause:** Ambiguous XPath locator matches 5 elements
- **File:** LoginSteps.java:182
- **Fix:** Use specific locator (e.g., `getByRole(link, {name: "Projects", exact: true})`)

---

## License

Internal project — not for public distribution.

---

*Last updated: February 20, 2026 — v0.9*
