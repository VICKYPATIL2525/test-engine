import streamlit as st
import os
import json
import glob
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

# ─── Page Configuration ───
st.set_page_config(
    page_title="Testing Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───
st.markdown("""
<style>
    /* Main title */
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Status badges */
    .badge-pass {
        background-color: #dcfce7;
        color: #166534;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-fail {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Commit table */
    .commit-hash {
        font-family: monospace;
        background: rgba(255, 255, 255, 0.08);
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #818cf8;
    }
    
    /* Analysis box */
    .analysis-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        line-height: 1.7;
    }
    
    /* Sidebar styling - dark theme friendly */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e2e 0%, #181825 100%);
    }
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #cdd6f4 !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] label {
        color: #bac2de !important;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Divider */
    .section-divider {
        border-top: 2px solid rgba(255, 255, 255, 0.1);
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ─── Helper Functions ───
@st.cache_data
def load_commit_data(data_folder):
    """Load commit history from JSON file"""
    commits_file = Path(data_folder) / "commits_detailed.json"
    if commits_file.exists():
        with open(commits_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


@st.cache_data
def load_repo_info(data_folder):
    """Load repository metadata"""
    info_file = Path(data_folder) / "repository_info.json"
    if info_file.exists():
        with open(info_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


@st.cache_data
def load_contributors(data_folder):
    """Load contributor data"""
    contributors_file = Path(data_folder) / "contributors.json"
    if contributors_file.exists():
        with open(contributors_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def load_html_reports(reports_folder):
    """Load all HTML test reports"""
    html_reports_path = Path(reports_folder) / "html-reports"
    reports = []
    if html_reports_path.exists():
        report_files = sorted(glob.glob(str(html_reports_path / "*.html")))
        for report_file in report_files:
            path = Path(report_file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            reports.append({
                'name': path.name,
                'size_kb': round(len(content) / 1024, 2),
                'content': content
            })
    return reports


def get_data_folders():
    """Scan pulled_data directory for available datasets"""
    base_path = Path(__file__).parent / "pulled_data"
    if base_path.exists():
        return [f.name for f in base_path.iterdir() if f.is_dir()]
    return []


def run_llm_analysis(commits_data, test_reports, max_commits=30):
    """Run Azure OpenAI analysis"""
    llm = AzureChatOpenAI(
        deployment_name="gpt-4.1-mini",
        model_name="gpt-4.1-mini",
        temperature=0.1,
        max_tokens=1500,
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_VERSION"),
        api_key=os.getenv("OPENAI_API_KEY"),
        azure_deployment="gpt-4.1-mini"
    )
    
    # Prepare commit context
    commit_summary = []
    for commit in commits_data[:max_commits]:
        commit_summary.append({
            'hash': commit.get('hash', commit.get('sha', ''))[:8],
            'author': commit.get('author', {}).get('name', ''),
            'date': commit.get('date', ''),
            'message': commit.get('message', ''),
            'files_changed': len(commit.get('files_changed', commit.get('changed_files', [])))
        })
    
    # Prepare reports
    reports_text = ""
    for idx, report in enumerate(test_reports, 1):
        reports_text += f"\n\n--- TEST REPORT {idx}: {report['name']} ({report['size_kb']} KB) ---\n"
        reports_text += report['content']
    
    prompt = f"""You are a QA test analysis expert. Analyze the following commit history and HTML test execution reports to identify root causes of test failures.

COMMIT HISTORY (Last {max_commits} commits):
{json.dumps(commit_summary, indent=2)}

TEST EXECUTION REPORTS (Raw HTML):
{reports_text}

Provide your analysis in EXACTLY the following format with these markdown headings. Under each heading, write clear bullet points:

## 🔴 Root Cause Analysis
- (bullet points explaining the root cause of each test failure)

## 🔗 Suspect Commits
- (bullet points listing which commits likely introduced the issues, with hash and reason)

## 📍 Error Details
- (bullet points with specific file/line references, stack traces, and exact error messages)

## 💡 Recommendations
- (bullet points with actionable steps to fix each issue)

## 📊 Patterns & Trends
- (bullet points about patterns or trends observed across the test runs)

## ✅ Summary
- (brief overall summary of the situation)

IMPORTANT: Use the exact heading format above (## emoji Title). Under each heading, use bullet points (- ). Be concise, specific, and actionable."""

    messages = [
        SystemMessage(content="You are an expert QA engineer analyzing test failures and commit history."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    return response.content


def save_analysis(analysis_result, commits_data, test_reports, output_file="llm_analysis.json"):
    """Save analysis results to file"""
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'commits_analyzed': len(commits_data),
        'reports_analyzed': len(test_reports),
        'llm_analysis': analysis_result,
        'raw_data': {
            'commits': commits_data[:30],
            'test_reports': test_reports
        }
    }
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)


def load_previous_analysis(output_file="llm_analysis.json"):
    """Load previously saved analysis"""
    path = Path(__file__).parent / output_file
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def render_formatted_analysis(analysis_text):
    """Render analysis text as styled section cards with headings and bullet points"""
    import re
    
    # Split by ## headings
    sections = re.split(r'(?=^## )', analysis_text.strip(), flags=re.MULTILINE)
    sections = [s.strip() for s in sections if s.strip()]
    
    # Color map for section icons
    section_colors = {
        '🔴': '#ef4444',
        '🔗': '#8b5cf6',
        '📍': '#f59e0b',
        '💡': '#22c55e',
        '📊': '#3b82f6',
        '✅': '#10b981',
    }
    
    for section in sections:
        lines = section.split('\n')
        heading = lines[0].lstrip('#').strip() if lines else ''
        body = '\n'.join(lines[1:]).strip()
        
        # Detect color from emoji in heading
        border_color = '#6366f1'  # default purple
        for emoji, color in section_colors.items():
            if emoji in heading:
                border_color = color
                break
        
        st.markdown(
            f"""
            <div style="
                background: rgba(255,255,255,0.03);
                border-left: 4px solid {border_color};
                border-radius: 8px;
                padding: 1rem 1.5rem;
                margin-bottom: 1rem;
            ">
                <h3 style="margin:0 0 0.6rem 0; color:#e2e8f0; font-size:1.2rem;">{heading}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if body:
            st.markdown(body)


# ─── Sidebar ───
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")
    
    # Data source selection
    data_folders = get_data_folders()
    if data_folders:
        selected_folder = st.selectbox(
            "📁 Select Dataset",
            data_folders,
            index=0,
            help="Choose extracted repository data to analyze"
        )
        data_path = Path(__file__).parent / "pulled_data" / selected_folder
    else:
        st.error("No data found in pulled_data/")
        st.stop()
    
    st.markdown("---")
    
    # LLM Settings
    st.markdown("### 🤖 LLM Settings")
    max_commits = st.slider("Commits to Analyze", min_value=5, max_value=50, value=30, step=5)
    max_tokens = st.slider("Max Tokens", min_value=500, max_value=3000, value=1500, step=100)
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.1, step=0.05)
    
    st.markdown("---")
    
    # Azure OpenAI status
    st.markdown("### 🔑 Azure OpenAI")
    api_key = os.getenv("OPENAI_API_KEY", "")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    
    if api_key and endpoint:
        st.success("✅ Credentials loaded from .env")
        st.caption(f"Endpoint: `{endpoint[:40]}...`")
    else:
        st.error("❌ Missing credentials in .env")
        st.caption("Set OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT")
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#94a3b8; font-size:0.75rem;'>"
        "Testing Engine v0.9<br>Powered by Azure OpenAI"
        "</div>",
        unsafe_allow_html=True
    )


# ─── Main Content ───
st.markdown('<p class="main-title">🔍 Testing Engine</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">AI-Powered Test Failure Analysis — Commits × Reports → Actionable Intelligence</p>', unsafe_allow_html=True)

# Load data
base_dir = Path(__file__).parent
commits_data = load_commit_data(str(data_path))
repo_info = load_repo_info(str(data_path))
contributors = load_contributors(str(data_path))
test_reports = load_html_reports(str(base_dir))

# ─── Top Metrics ───
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(commits_data)}</div>
        <div class="metric-label">Commits</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(test_reports)}</div>
        <div class="metric-label">Test Reports</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_size = sum(r['size_kb'] for r in test_reports)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_size:.1f}</div>
        <div class="metric-label">Report Size (KB)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    unique_authors = set()
    for c in commits_data:
        author = c.get('author', {}).get('name', '')
        if author:
            unique_authors.add(author)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(unique_authors)}</div>
        <div class="metric-label">Contributors</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ─── Tabs ───
tab_analysis, tab_commits, tab_reports, tab_history = st.tabs([
    "🤖 AI Analysis", "📝 Commits", "📊 Test Reports", "📜 History"
])

# ─── Tab 1: AI Analysis ───
with tab_analysis:
    st.markdown("### Run AI Analysis")
    st.markdown("Send commit history and test reports to Azure OpenAI for intelligent root cause analysis.")
    
    col_btn, col_status = st.columns([1, 3])
    
    with col_btn:
        run_analysis = st.button("🚀 Analyze Now", type="primary", use_container_width=True)
    
    with col_status:
        if not (api_key and endpoint):
            st.warning("⚠️ Configure Azure OpenAI credentials in .env first")
        elif len(test_reports) == 0:
            st.info("ℹ️ No test reports found in html-reports/ folder")
        else:
            st.success(f"✅ Ready — {len(commits_data)} commits + {len(test_reports)} reports")
    
    st.markdown("---")
    
    if run_analysis:
        if not (api_key and endpoint):
            st.error("❌ Azure OpenAI credentials not configured. Please set them in .env file.")
        elif len(test_reports) == 0:
            st.error("❌ No test reports found. Place HTML files in html-reports/ folder.")
        else:
            with st.spinner("🔄 Analyzing with Azure OpenAI GPT-4..."):
                try:
                    analysis = run_llm_analysis(commits_data, test_reports, max_commits)
                    save_analysis(analysis, commits_data, test_reports)
                    st.session_state['analysis_result'] = analysis
                    st.session_state['analysis_time'] = datetime.now().isoformat()
                    st.success("✅ Analysis complete! Results saved to llm_analysis.json")
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
    
    # Display analysis results
    analysis_text = st.session_state.get('analysis_result', None)
    
    if analysis_text:
        st.markdown("### 📋 Analysis Results")
        st.markdown(f"*Generated: {st.session_state.get('analysis_time', 'N/A')}*")
        st.markdown("---")
        render_formatted_analysis(analysis_text)
        
        # Download button
        st.download_button(
            label="📥 Download Analysis (JSON)",
            data=json.dumps({
                'timestamp': st.session_state.get('analysis_time', ''),
                'analysis': analysis_text
            }, indent=2),
            file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    else:
        # Show previous analysis if exists
        prev_analysis = load_previous_analysis()
        if prev_analysis:
            st.markdown("### 📋 Previous Analysis")
            st.markdown(f"*Generated: {prev_analysis.get('timestamp', 'N/A')}*")
            st.info("ℹ️ Showing last saved analysis. Click **Analyze Now** to run a fresh one.")
            render_formatted_analysis(prev_analysis.get('llm_analysis', 'No analysis text found.'))
        else:
            st.markdown(
                "<div style='text-align:center; padding:3rem; color:#94a3b8;'>"
                "<p style='font-size:3rem;'>🤖</p>"
                "<p>Click <strong>Analyze Now</strong> to run AI-powered test failure analysis</p>"
                "</div>",
                unsafe_allow_html=True
            )


# ─── Tab 2: Commits ───
with tab_commits:
    st.markdown("### Commit History")
    
    if repo_info:
        st.markdown(f"**Repository:** {repo_info.get('name', 'N/A')} &nbsp;|&nbsp; "
                     f"**Branches:** {repo_info.get('total_branches', 'N/A')} &nbsp;|&nbsp; "
                     f"**Total Commits:** {repo_info.get('total_commits', len(commits_data))}")
    
    st.markdown("---")
    
    # Search
    search_query = st.text_input("🔍 Search commits", placeholder="Search by message, author, or hash...")
    
    # Display commits
    for idx, commit in enumerate(commits_data):
        sha = commit.get('sha', commit.get('hash', ''))[:8]
        author = commit.get('author', {}).get('name', 'Unknown')
        date = commit.get('date', '')
        message = commit.get('message', 'No message')
        changed_files = commit.get('changed_files', commit.get('files_changed', []))
        stats = commit.get('stats', {})
        
        # Apply search filter
        if search_query:
            search_lower = search_query.lower()
            if (search_lower not in message.lower() and 
                search_lower not in author.lower() and 
                search_lower not in sha.lower()):
                continue
        
        with st.expander(f"`{sha}` — {message[:80]}{'...' if len(message) > 80 else ''}", expanded=False):
            col_a, col_b, col_c = st.columns([2, 2, 1])
            with col_a:
                st.markdown(f"**Author:** {author}")
            with col_b:
                st.markdown(f"**Date:** {date[:19] if date else 'N/A'}")
            with col_c:
                st.markdown(f"**Files:** {len(changed_files)}")
            
            # Stats
            if stats:
                ins = stats.get('total_insertions', 0)
                dels = stats.get('total_deletions', 0)
                st.markdown(f"**Lines:** <span style='color:#22c55e;'>+{ins}</span> / "
                           f"<span style='color:#ef4444;'>-{dels}</span>", unsafe_allow_html=True)
            
            # Changed files
            if changed_files:
                st.markdown("**Changed Files:**")
                for f in changed_files:
                    fname = f.get('file', f) if isinstance(f, dict) else str(f)
                    st.markdown(f"- `{fname}`")


# ─── Tab 3: Test Reports ───
with tab_reports:
    st.markdown("### Test Reports")
    
    if not test_reports:
        st.warning("No HTML test reports found in html-reports/ folder.")
        st.info("Place SparkReport HTML files in the `html-reports/` directory.")
    else:
        for idx, report in enumerate(test_reports):
            st.markdown(f"#### 📄 {report['name']}")
            st.markdown(f"**Size:** {report['size_kb']} KB")
            
            col_view, col_raw = st.columns(2)
            
            with col_view:
                if st.button(f"👁️ View Report", key=f"view_{idx}", use_container_width=True):
                    st.session_state[f'show_report_{idx}'] = not st.session_state.get(f'show_report_{idx}', False)
            
            with col_raw:
                if st.button(f"📝 View Source", key=f"raw_{idx}", use_container_width=True):
                    st.session_state[f'show_raw_{idx}'] = not st.session_state.get(f'show_raw_{idx}', False)
            
            # Render HTML report
            if st.session_state.get(f'show_report_{idx}', False):
                st.components.v1.html(report['content'], height=600, scrolling=True)
            
            # Show raw HTML
            if st.session_state.get(f'show_raw_{idx}', False):
                st.code(report['content'][:5000] + ("\n\n... [truncated]" if len(report['content']) > 5000 else ""), language="html")
            
            st.markdown("---")


# ─── Tab 4: History ───
with tab_history:
    st.markdown("### Analysis History")
    
    prev = load_previous_analysis()
    if prev:
        st.markdown(f"**Last Run:** {prev.get('timestamp', 'N/A')}")
        st.markdown(f"**Commits Analyzed:** {prev.get('commits_analyzed', 'N/A')}")
        st.markdown(f"**Reports Analyzed:** {prev.get('reports_analyzed', 'N/A')}")
        
        st.markdown("---")
        st.markdown("#### Full Analysis")
        render_formatted_analysis(prev.get('llm_analysis', 'No analysis text found.'))
        
        st.markdown("---")
        
        # Download
        st.download_button(
            label="📥 Download Full Report (JSON)",
            data=json.dumps(prev, indent=2, default=str),
            file_name=f"full_report_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
    else:
        st.info("No previous analysis found. Run an analysis from the **AI Analysis** tab first.")
