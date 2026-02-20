import os
import json
import glob
import re
from pathlib import Path
from datetime import datetime
import csv
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()


class LLMTestAnalyzer:
    """Analyzes test reports and commit history using Azure OpenAI"""
    
    def __init__(self):
        self.commits_data = []
        self.test_reports = []
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize Azure OpenAI LLM"""
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
        return llm
    
    def load_commit_data(self, data_folder):
        """Load commit history from JSON file"""
        commits_file = Path(data_folder) / "commits_detailed.json"
        
        if commits_file.exists():
            with open(commits_file, 'r', encoding='utf-8') as f:
                self.commits_data = json.load(f)
            print(f"✓ Commits Loaded: {len(self.commits_data)}")
        else:
            print(f"✗ Commits file not found: {commits_file}")
    
    def load_raw_html_report(self, report_path):
        """Load raw HTML report without parsing"""
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        report_data = {
            'path': str(report_path),
            'name': report_path.name,
            'size_kb': round(len(content) / 1024, 2),
            'content': content
        }
        
        return report_data
    
    def load_test_reports(self, reports_folder):
        """Load all raw HTML test reports"""
        html_reports_path = Path(reports_folder) / "html-reports"
        
        if not html_reports_path.exists():
            print(f"✗ html-reports folder not found: {html_reports_path}")
            return
        
        report_files = glob.glob(str(html_reports_path / "*.html"))
        
        for report_file in report_files:
            report_data = self.load_raw_html_report(Path(report_file))
            self.test_reports.append(report_data)
        
        print(f"✓ Test Reports: {len(self.test_reports)}")
    
    def prepare_analysis_context(self):
        """Prepare context data for LLM analysis"""
        # Prepare commit summary
        commit_summary = []
        for commit in self.commits_data[:30]:  # Last 30 commits
            commit_info = {
                'hash': commit.get('hash', '')[:8],
                'author': commit.get('author', {}).get('name', ''),
                'date': commit.get('date', ''),
                'message': commit.get('message', ''),
                'files_changed': len(commit.get('files_changed', []))
            }
            commit_summary.append(commit_info)
        
        # Prepare raw HTML reports
        test_reports = []
        for report in self.test_reports:
            test_reports.append({
                'name': report['name'],
                'size_kb': report['size_kb'],
                'html_content': report['content']
            })
        
        return {
            'commits': commit_summary,
            'test_reports': test_reports
        }
    
    def analyze_with_llm(self):
        """Send data to Azure OpenAI for analysis"""
        context = self.prepare_analysis_context()
        
        # Create prompt with raw HTML reports
        reports_text = ""
        for idx, report in enumerate(context['test_reports'], 1):
            reports_text += f"\n\n--- TEST REPORT {idx}: {report['name']} ({report['size_kb']} KB) ---\n"
            reports_text += report['html_content']
        
        prompt = f"""You are a QA test analysis expert. Analyze the following commit history and HTML test execution reports to identify root causes of test failures.

COMMIT HISTORY (Last 30 commits):
{json.dumps(context['commits'], indent=2)}

TEST EXECUTION REPORTS (Raw HTML):
{reports_text}

Please analyze the HTML reports and provide:
1. Root cause analysis of any test failures
2. Which commits might have introduced the issues
3. Specific file/line references from error stack traces
4. Exact error messages and their meanings
5. Actionable recommendations to fix the issues
6. Patterns or trends you observe

Be concise, specific, and actionable."""

        messages = [
            SystemMessage(content="You are an expert QA engineer analyzing test failures and commit history."),
            HumanMessage(content=prompt)
        ]
        
        print("\n" + "="*80)
        print("ANALYZING WITH AZURE OPENAI...")
        print("="*80 + "\n")
        
        try:
            response = self.llm.invoke(messages)
            analysis = response.content
            return analysis
        except Exception as e:
            print(f"✗ Error calling Azure OpenAI: {e}")
            return None
    
    def display_summary(self):
        """Display summary statistics"""
        print("\n" + "="*80)
        print("DATA SUMMARY")
        print("="*80)
        
        print(f"\n📊 Commits: {len(self.commits_data)}")
        print(f"📊 Test Reports: {len(self.test_reports)}")
        
        total_size = sum(r['size_kb'] for r in self.test_reports)
        
        print(f"\nTest Report Files:")
        for report in self.test_reports:
            print(f"  • {report['name']} ({report['size_kb']} KB)")
        print(f"\n📊 Total Report Size: {total_size:.2f} KB")
    
    def save_analysis(self, analysis_result, output_file="llm_analysis.json"):
        """Save analysis results to file"""
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'commits_analyzed': len(self.commits_data),
            'reports_analyzed': len(self.test_reports),
            'llm_analysis': analysis_result,
            'raw_data': {
                'commits': self.commits_data[:30],
                'test_reports': self.test_reports
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n✓ Analysis saved to: {output_file}")
    
    def run_analysis(self, data_folder, reports_folder):
        """Main analysis workflow"""
        print("\n" + "="*80)
        print("LLM-POWERED TEST ANALYSIS ENGINE")
        print("="*80 + "\n")
        
        # Load data
        self.load_commit_data(data_folder)
        self.load_test_reports(reports_folder)
        
        # Display summary
        self.display_summary()
        
        # Run LLM analysis
        analysis_result = self.analyze_with_llm()
        
        if analysis_result:
            print("\n" + "="*80)
            print("ANALYSIS RESULTS")
            print("="*80 + "\n")
            print(analysis_result)
            
            # Save results
            self.save_analysis(analysis_result)
            
            print("\n" + "="*80)
            print("✓ ANALYSIS COMPLETE")
            print("="*80 + "\n")
        else:
            print("\n✗ Analysis failed. Please check your Azure OpenAI configuration.")


def main():
    """Main entry point"""
    # Define paths
    current_dir = Path(__file__).parent
    data_folder = current_dir / "pulled_data" / "QA_Playwright_Repo_20260210_163229"
    reports_folder = current_dir
    
    # Verify paths exist
    if not data_folder.exists():
        print(f"✗ Data folder not found: {data_folder}")
        return
    
    # Initialize and run analyzer
    analyzer = LLMTestAnalyzer()
    analyzer.run_analysis(data_folder, reports_folder)


if __name__ == "__main__":
    main()
