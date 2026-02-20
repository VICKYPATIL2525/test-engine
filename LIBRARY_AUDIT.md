# 📊 LIBRARY AUDIT & CLEANUP ANALYSIS

**Date:** February 12, 2026  
**Environment:** myenv  
**Total Installed Packages:** 97

---

## 🎯 EXECUTIVE SUMMARY

- **Currently Used:** 7 packages (7.2%)
- **Unused/Bloat:** 90 packages (92.8%)
- **Potential Space Savings:** ~500-800 MB
- **Recommendation:** Create clean environment with minimal dependencies

---

## ✅ ACTUALLY USED LIBRARIES

### **app.py** (Main Application)

| Import | Package | Version | Size | Status |
|--------|---------|---------|------|--------|
| `os` | stdlib | - | - | ✅ Built-in |
| `json` | stdlib | - | - | ✅ Built-in |
| `glob` | stdlib | - | - | ✅ Built-in |
| `re` | stdlib | - | - | ✅ Built-in |
| `pathlib.Path` | stdlib | - | - | ✅ Built-in |
| `datetime` | stdlib | - | - | ✅ Built-in |
| `csv` | stdlib | - | - | ✅ Built-in |
| `python-dotenv` | **python-dotenv** | 1.2.1 | <1MB | ✅ REQUIRED |
| `langchain_openai` | **langchain-openai** | 1.1.9 | <5MB | ✅ REQUIRED |
| `langchain_core.messages` | **langchain-core** | 1.2.11 | <10MB | ✅ REQUIRED (dependency) |

**Dependencies Needed:**
- `openai` (2.20.0) - Required by langchain-openai
- `pydantic` (2.12.5) - Required by langchain-core
- `typing_extensions` - Required by pydantic

---

### **git_extractor.py** (Git Extraction - Optional)

| Import | Package | Version | Size | Status |
|--------|---------|---------|------|--------|
| `os, json, csv, shutil, logging, datetime, pathlib, typing, hashlib` | stdlib | - | - | ✅ Built-in |
| `git` / `git.Repo` | **GitPython** | 3.1.46 | ~5MB | ⚠️ OPTIONAL (only if extracting new repos) |

**Dependencies for GitPython:**
- `gitdb` (4.0.12)
- `smmap` (5.0.2)

---

## ❌ UNUSED LIBRARIES (CAN REMOVE)

### **🗑️ Category 1: Anthropic/Claude (Replaced by Azure OpenAI)**
```
anthropic (0.79.0) - NOT USED
langchain-anthropic (1.3.2) - NOT USED  
```
**Reason:** We switched from Claude to Azure OpenAI  
**Space Saved:** ~50MB

---

### **🗑️ Category 2: Web Frameworks (Not Needed)**
```
Flask (3.1.2) - NOT USED
flask-cors (6.0.2) - NOT USED
Werkzeug (3.1.5) - dependency of Flask
Jinja2 (3.1.6) - dependency of Flask  
click (8.3.1) - dependency of Flask
blinker (1.9.0) - dependency of Flask
itsdangerous (2.2.0) - dependency of Flask
MarkupSafe (3.0.3) - dependency of Jinja2
```
**Reason:** No web server in current app  
**Space Saved:** ~20MB

---

### **🗑️ Category 3: Testing Libraries (Not Needed in Production)**
```
pytest (9.0.2) - NOT USED
pytest-asyncio (1.3.0) - NOT USED
pytest-cov (7.0.0) - NOT USED
coverage (7.13.4) - NOT USED
pluggy (1.6.0) - pytest dependency
iniconfig (2.3.0) - pytest dependency
```
**Reason:** No tests written, production environment  
**Space Saved:** ~15MB

---

### **🗑️ Category 4: Data Processing (Not Used)**
```
pandas (3.0.0) - NOT USED
numpy (2.4.2) - dependency of pandas
```
**Reason:** We use basic CSV/JSON, no pandas operations  
**Space Saved:** ~150MB

---

### **🗑️ Category 5: HTML/PDF Processing (Not Used)**
```
beautifulsoup4 (4.14.3) - NOT USED (we send raw HTML to LLM)
lxml (6.0.2) - NOT USED
soupsieve (2.8.3) - dependency of beautifulsoup4
weasyprint (68.1) - NOT USED (PDF generation)
pillow (12.1.1) - dependency of weasyprint
fonttools (4.61.1) - dependency of weasyprint
cssselect2 (0.8.0) - dependency of weasyprint
pydyf (0.12.1) - dependency of weasyprint
pyphen (0.17.2) - dependency of weasyprint
tinycss2 (1.5.1) - dependency of weasyprint
tinyhtml5 (2.0.0) - dependency of weasyprint
webencodings (0.5.1) - dependency of weasyprint
brotli (1.2.0) - dependency of weasyprint
zopfli (0.4.0) - dependency of weasyprint
zstandard (0.25.0) - dependency of weasyprint
```
**Reason:** Raw HTML sent to LLM, no parsing/PDF generation  
**Space Saved:** ~200MB

---

### **🗑️ Category 6: LangGraph/Advanced Features (Not Used)**
```
langgraph (1.0.8) - NOT USED
langgraph-checkpoint (4.0.0) - NOT USED
langgraph-prebuilt (1.0.7) - NOT USED
langgraph-sdk (0.3.4) - NOT USED
langsmith (0.6.9) - NOT USED (tracing)
orjson (3.11.7) - dependency
ormsgpack (1.12.2) - dependency
uuid_utils (0.14.0) - dependency
```
**Reason:** Simple LLM calls, no workflows/graphs  
**Space Saved:** ~30MB

---

### **🗑️ Category 7: HTTP/Async Libraries (Minimal Use)**
```
aiohttp (3.13.3) - NOT USED directly
aiohappyeyeballs (2.6.1) - dependency
aiosignal (1.4.0) - dependency  
frozenlist (1.8.0) - dependency
multidict (6.7.1) - dependency
propcache (0.4.1) - dependency
yarl (1.22.0) - dependency
```
**Reason:** langchain-openai uses httpx, not aiohttp  
**Space Saved:** ~20MB

---

### **🗑️ Category 8: Markdown/Documentation (Not Used)**
```
Markdown (3.10.2) - NOT USED
markdown-it-py (4.0.0) - NOT USED
mdurl (0.1.2) - dependency
rich (14.3.2) - NOT USED (CLI formatting)
Pygments (2.19.2) - dependency of rich
```
**Reason:** No markdown processing, minimal CLI  
**Space Saved:** ~15MB

---

### **🗑️ Category 9: Miscellaneous Unused**
```
colorama (0.4.6) - NOT USED
requests (2.32.5) - NOT USED (langchain uses httpx)
requests-toolbelt (1.0.0) - NOT USED
tqdm (4.67.3) - NOT USED (progress bars)
regex (2026.1.15) - NOT USED (stdlib re is sufficient)
tiktoken (0.12.0) - NOT USED (token counting, could be useful but unused)
tenacity (9.1.4) - NOT USED directly (retry logic)
cffi (2.0.0) - C Foreign Function Interface (unused)
pycparser (3.0) - dependency
xxhash (3.6.0) - NOT USED (hashing)
```
**Space Saved:** ~30MB

---

## 🎯 MINIMAL REQUIREMENTS.TXT

```txt
# Core Azure OpenAI Integration
openai>=1.12.0
langchain-openai>=0.0.5
langchain-core>=0.1.0

# Environment Configuration
python-dotenv>=1.0.0

# Optional: Git Extraction (only if needed)
# gitpython>=3.1.40
```

**Total Packages:** 4 (down from 97)  
**Total Size:** ~20MB (down from ~700MB)

---

## 📋 CLEANUP STRATEGY

### **Option 1: Clean Install (RECOMMENDED)**

```powershell
# 1. Backup current environment name
Rename-Item myenv myenv_backup

# 2. Create fresh environment
python -m venv myenv

# 3. Activate
.\myenv\Scripts\Activate.ps1

# 4. Install minimal requirements
pip install openai langchain-openai langchain-core python-dotenv

# 5. Test
python app.py

# 6. If successful, delete backup
# Remove-Item -Recurse -Force myenv_backup
```

**Pros:**
- ✅ Clean slate, no conflicts
- ✅ Fastest installation
- ✅ Smallest footprint

**Cons:**
- ⚠️ Need to reinstall if somethingfails

---

### **Option 2: Selective Uninstall (CAUTIOUS)**

```powershell
# Keep environment, remove unused packages
pip uninstall -y anthropic langchain-anthropic flask flask-cors pandas numpy beautifulsoup4 lxml pytest pytest-asyncio pytest-cov weasyprint pillow langgraph langgraph-checkpoint langgraph-prebuilt langgraph-sdk langsmith aiohttp rich markdown tqdm requests

# Verify app still works
python app.py
```

**Pros:**
- ✅ Keep current environment structure
- ✅ Can rollback easily

**Cons:**
- ⚠️ May leave orphaned dependencies
- ⚠️ Not as clean

---

### **Option 3: Keep As Is (if space not a concern)**

**Pros:**
- ✅ Zero risk
- ✅ No downtime
- ✅ Can experiment with other libraries later

**Cons:**
- ❌ ~680MB wasted space
- ❌ Slower environment activation
- ❌ More packages to security-update

---

## 🔍 DEPENDENCY TREE (Minimal Setup)

```
app.py
├── python-dotenv (1.2.1)
└── langchain-openai (1.1.9)
    ├── openai (2.20.0)
    │   ├── httpx (0.28.1)
    │   │   ├── httpcore (1.0.9)
    │   │   │   └── h11 (0.16.0)
    │   │   ├── anyio (4.12.1)
    │   │   │   ├── idna (3.11)
    │   │   │   └── sniffio (1.3.1)
    │   │   └── certifi (2026.1.4)
    │   ├── pydantic (2.12.5)
    │   │   ├── pydantic_core (2.41.5)
    │   │   ├── typing_extensions (4.15.0)
    │   │   └── annotated-types (0.7.0)
    │   ├── distro (1.9.0)
    │   ├── jiter (0.13.0)
    │   └── tqdm (optional, can skip)
    └── langchain-core (1.2.11)
        ├── PyYAML (6.0.3)
        ├── jsonpatch (1.33)
        │   └── jsonpointer (3.0.0)
        ├── packaging (26.0)
        ├── pydantic (shared)
        └── tenacity (9.1.4)
```

**Total Required: ~28 packages** (down from 97)

---

## ✅ VALIDATION CHECKLIST

After cleanup, verify:

```powershell
# 1. Check installed packages
pip list

# 2. Verify app imports
python -c "from langchain_openai import AzureChatOpenAI; from dotenv import load_dotenv; print('✓ All imports successful')"

# 3. Test app
python app.py

# 4. Check output
ls llm_analysis.json
```

---

## 💾 SPACE COMPARISON

| Environment | Packages | Size | Status |
|-------------|----------|------|--------|
| **Current (myenv)** | 97 | ~700MB | ⚠️ Bloated |
| **Minimal (recommended)** | 28 | ~150MB | ✅ Optimal |
| **Savings** | -69 | **-550MB** | ✅ 79% reduction |

---

## 🎯 RECOMMENDATION

**Go with Option 1: Clean Install**

**Why:**
1. ✅ app.py only needs 4 direct dependencies
2. ✅ 79% space savings (~550MB)
3. ✅ Faster pip operations
4. ✅ Easier to maintain/update
5. ✅ No security vulnerabilities in unused packages

**When to do it:**
- ✅ After confirming app.py works correctly (already confirmed)
- ✅ When you have 10 minutes downtime
- ✅ With myenv_backup as safety net

---

## 📞 SUPPORT

If cleanup fails:
1. Restore backup: `Rename-Item myenv_backup myenv`
2. Reactivate: `.\myenv\Scripts\Activate.ps1`
3. Continue working with current environment
