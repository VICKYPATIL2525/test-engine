"""
Git Repository Data Extractor
Extracts comprehensive information from GitHub repositories using GitPython
"""

import os
import json
import csv
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import git
from git import Repo
import hashlib


class GitExtractor:
    """
    Production-grade Git repository data extractor
    
    Extracts:
    - Complete commit history with diffs
    - File change tracking
    - Branch and tag information  
    - Contributor statistics
    - Repository metadata
    """
    
    def __init__(
        self,
        repo_url: str,
        github_token: Optional[str] = None,
        output_dir: str = "pulled_data",
        max_commits: Optional[int] = None,
        shallow_clone: bool = True
    ):
        """
        Initialize Git Extractor
        
        Args:
            repo_url: GitHub repository URL (https or ssh)
            github_token: GitHub token for private repos
            output_dir: Base output directory (default: pulled_data)
            max_commits: Limit number of commits (None = all)
            shallow_clone: Use shallow clone for speed
        """
        self.repo_url = repo_url
        self.github_token = github_token
        self.max_commits = max_commits
        self.shallow_clone = shallow_clone
        
        # Extract repo name
        self.repo_name = self._extract_repo_name(repo_url)
        
        # Setup paths
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.session_id = hashlib.md5(f"{repo_url}{self.timestamp}".encode()).hexdigest()[:8]
        
        # Create base output directory if it doesn't exist
        base_output = Path(output_dir)
        base_output.mkdir(parents=True, exist_ok=True)
        
        self.clone_dir = Path("temp_repos") / f"{self.repo_name}_{self.timestamp}"
        self.output_dir = base_output / f"{self.repo_name}_{self.timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Inject token for private repos
        if github_token and 'github.com' in repo_url and repo_url.startswith('https://'):
            self.clone_url = repo_url.replace('https://', f'https://{github_token}@')
        else:
            self.clone_url = repo_url
        
        # Setup logging
        self.logger = self._setup_logger()
        self.repo = None
        
        # Statistics
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'commits_processed': 0,
            'files_tracked': 0,
            'errors': []
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger"""
        logger = logging.Logger(f"GitExtractor-{self.repo_name}")
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(self.output_dir / "extraction.log", encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _extract_repo_name(self, url: str) -> str:
        """Extract repository name from URL"""
        name = url.rstrip('/').split('/')[-1].replace('.git', '')
        return "".join(c for c in name if c.isalnum() or c in ('-', '_')) or 'repo'
    
    def _save_json(self, data: Any, filename: str) -> bool:
        """Save data as JSON"""
        try:
            filepath = self.output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            size = filepath.stat().st_size
            self.logger.info(f"✓ Saved {filename} ({size:,} bytes)")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save {filename}: {e}")
            return False
    
    def _save_csv(self, data: List[Dict], filename: str) -> bool:
        """Save data as CSV"""
        if not data:
            return False
        
        try:
            filepath = self.output_dir / filename
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            self.logger.info(f"✓ Saved {filename} ({len(data)} rows)")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save {filename}: {e}")
            return False
    
    def clone_repository(self) -> bool:
        """Clone repository"""
        self.logger.info(f"Cloning {self.repo_url}...")
        
        try:
            if self.clone_dir.exists():
                shutil.rmtree(self.clone_dir)
            
            clone_kwargs = {}
            # Note: We need full history to extract commits with diffs
            # Shallow clone only gets latest snapshot without history
            if self.shallow_clone and self.max_commits:
                # Use depth slightly more than max_commits to ensure we get enough history
                clone_kwargs['depth'] = self.max_commits + 10
                self.logger.info(f"Using shallow clone (depth={self.max_commits + 10})")
            
            self.repo = Repo.clone_from(self.clone_url, self.clone_dir, **clone_kwargs)
            self.logger.info(f"✓ Cloned to {self.clone_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Clone failed: {e}")
            self.stats['errors'].append(f"Clone failed: {str(e)}")
            return False
    
    def extract_repository_info(self) -> Dict:
        """Extract basic repository information"""
        self.logger.info("Extracting repository info...")
        
        try:
            info = {
                'name': self.repo_name,
                'url': self.repo_url,
                'clone_path': str(self.clone_dir),
                'extracted_at': datetime.now().isoformat(),
                'session_id': self.session_id,
                'remotes': [{'name': r.name, 'url': r.url} for r in self.repo.remotes],
                'total_commits': sum(1 for _ in self.repo.iter_commits()),
                'total_branches': len(list(self.repo.branches)),
                'total_tags': len(list(self.repo.tags))
            }
            
            # Get HEAD info
            try:
                head = self.repo.head.commit
                info['head'] = {
                    'sha': head.hexsha,
                    'message': head.message.strip(),
                    'author': head.author.name,
                    'date': head.committed_datetime.isoformat()
                }
            except:
                info['head'] = None
            
            self._save_json(info, "repository_info.json")
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to extract repo info: {e}")
            return {}
    
    def extract_commits(self) -> List[Dict]:
        """Extract commits with diffs"""
        self.logger.info("Extracting commits with diffs...")
        
        commits_data = []
        commits_summary = []
        
        try:
            count = 0
            for commit in self.repo.iter_commits():
                if self.max_commits and count >= self.max_commits:
                    break
                
                try:
                    # Get diffs
                    diffs = []
                    if commit.parents:
                        parent = commit.parents[0]
                        for diff in parent.diff(commit, create_patch=True):
                            diff_data = {
                                'change_type': diff.change_type,
                                'old_path': diff.a_path,
                                'new_path': diff.b_path,
                                'renamed': diff.renamed,
                                'deleted': diff.deleted_file,
                                'new_file': diff.new_file
                            }
                            
                            # Add diff content (limit size)
                            if diff.diff:
                                diff_text = diff.diff.decode('utf-8', errors='ignore')
                                if len(diff_text) > 10000:
                                    diff_data['diff'] = diff_text[:10000] + "\n... [truncated]"
                                    diff_data['truncated'] = True
                                else:
                                    diff_data['diff'] = diff_text
                                    diff_data['truncated'] = False
                            
                            diffs.append(diff_data)
                    
                    # Get changed files
                    changed_files = []
                    for file, stats in commit.stats.files.items():
                        changed_files.append({
                            'file': file,
                            'insertions': stats['insertions'],
                            'deletions': stats['deletions'],
                            'lines': stats['lines']
                        })
                    
                    # Build commit data
                    commit_data = {
                        'sha': commit.hexsha,
                        'sha_short': commit.hexsha[:7],
                        'author': {
                            'name': commit.author.name,
                            'email': commit.author.email
                        },
                        'committer': {
                            'name': commit.committer.name,
                            'email': commit.committer.email
                        },
                        'date': commit.committed_datetime.isoformat(),
                        'message': commit.message.strip(),
                        'parents': [p.hexsha for p in commit.parents],
                        'changed_files': changed_files,
                        'diffs': diffs,
                        'stats': {
                            'total_files': len(changed_files),
                            'total_insertions': commit.stats.total['insertions'],
                            'total_deletions': commit.stats.total['deletions'],
                            'total_lines': commit.stats.total['lines']
                        }
                    }
                    
                    commits_data.append(commit_data)
                    
                    # Summary for CSV
                    commits_summary.append({
                        'sha': commit.hexsha[:7],
                        'author': commit.author.name,
                        'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        'message': commit.message.strip().split('\n')[0][:100],
                        'files_changed': len(changed_files),
                        'insertions': commit.stats.total['insertions'],
                        'deletions': commit.stats.total['deletions']
                    })
                    
                    count += 1
                    if count % 50 == 0:
                        self.logger.info(f"Processed {count} commits...")
                
                except Exception as e:
                    self.logger.warning(f"Error processing commit: {e}")
                    continue
            
            self._save_json(commits_data, "commits_detailed.json")
            self._save_csv(commits_summary, "commits_summary.csv")
            
            self.stats['commits_processed'] = len(commits_data)
            self.logger.info(f"✓ Extracted {len(commits_data)} commits")
            return commits_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract commits: {e}")
            return []
    
    def extract_branches(self) -> List[Dict]:
        """Extract branch information"""
        self.logger.info("Extracting branches...")
        
        branches = []
        
        try:
            for branch in self.repo.branches:
                branches.append({
                    'name': branch.name,
                    'type': 'local',
                    'commit_sha': branch.commit.hexsha[:7],
                    'commit_message': branch.commit.message.strip().split('\n')[0],
                    'commit_date': branch.commit.committed_datetime.isoformat()
                })
            
            # Remote branches
            for remote in self.repo.remotes:
                for ref in remote.refs:
                    branches.append({
                        'name': ref.name,
                        'type': 'remote',
                        'commit_sha': ref.commit.hexsha[:7],
                        'commit_message': ref.commit.message.strip().split('\n')[0],
                        'commit_date': ref.commit.committed_datetime.isoformat()
                    })
            
            self._save_json(branches, "branches.json")
            self._save_csv(branches, "branches.csv")
            self.logger.info(f"✓ Extracted {len(branches)} branches")
            return branches
            
        except Exception as e:
            self.logger.error(f"Failed to extract branches: {e}")
            return []
    
    def extract_tags(self) -> List[Dict]:
        """Extract tag information"""
        self.logger.info("Extracting tags...")
        
        tags = []
        
        try:
            for tag in self.repo.tags:
                tags.append({
                    'name': tag.name,
                    'commit_sha': tag.commit.hexsha[:7],
                    'commit_date': tag.commit.committed_datetime.isoformat()
                })
            
            if tags:
                self._save_json(tags, "tags.json")
                self._save_csv(tags, "tags.csv")
                self.logger.info(f"✓ Extracted {len(tags)} tags")
            else:
                self.logger.info("No tags found")
            
            return tags
            
        except Exception as e:
            self.logger.error(f"Failed to extract tags: {e}")
            return []
    
    def extract_contributors(self, commits_data: List[Dict]) -> List[Dict]:
        """Extract contributor statistics"""
        self.logger.info("Extracting contributors...")
        
        contributors_map = {}
        
        try:
            for commit_info in commits_data:
                email = commit_info['author']['email']
                
                if email not in contributors_map:
                    contributors_map[email] = {
                        'name': commit_info['author']['name'],
                        'email': email,
                        'commits': 0,
                        'total_insertions': 0,
                        'total_deletions': 0,
                        'files_modified': set(),
                        'first_commit': commit_info['date'],
                        'last_commit': commit_info['date']
                    }
                
                contrib = contributors_map[email]
                contrib['commits'] += 1
                contrib['total_insertions'] += commit_info['stats']['total_insertions']
                contrib['total_deletions'] += commit_info['stats']['total_deletions']
                
                for file in commit_info['changed_files']:
                    contrib['files_modified'].add(file['file'])
                
                # Update dates
                if commit_info['date'] < contrib['first_commit']:
                    contrib['first_commit'] = commit_info['date']
                if commit_info['date'] > contrib['last_commit']:
                    contrib['last_commit'] = commit_info['date']
            
            # Convert to list
            contributors = []
            for contrib in contributors_map.values():
                contrib['files_modified'] = len(contrib['files_modified'])
                contributors.append(contrib)
            
            contributors.sort(key=lambda x: x['commits'], reverse=True)
            
            self._save_json(contributors, "contributors.json")
            self._save_csv(contributors, "contributors.csv")
            self.logger.info(f"✓ Extracted {len(contributors)} contributors")
            return contributors
            
        except Exception as e:
            self.logger.error(f"Failed to extract contributors: {e}")
            return []
    
    def extract_file_history(self, commits_data: List[Dict]) -> Dict:
        """Extract file change history"""
        self.logger.info("Extracting file history...")
        
        file_history = {}
        
        try:
            for commit in commits_data:
                for file_info in commit['changed_files']:
                    file_path = file_info['file']
                    
                    if file_path not in file_history:
                        file_history[file_path] = []
                    
                    file_history[file_path].append({
                        'commit': commit['sha_short'],
                        'author': commit['author']['name'],
                        'date': commit['date'],
                        'message': commit['message'].split('\n')[0][:100],
                        'insertions': file_info['insertions'],
                        'deletions': file_info['deletions']
                    })
            
            # Create summary
            file_summary = []
            for file_path, changes in file_history.items():
                file_summary.append({
                    'file': file_path,
                    'total_changes': len(changes),
                    'total_insertions': sum(c['insertions'] for c in changes),
                    'total_deletions': sum(c['deletions'] for c in changes),
                    'contributors': len(set(c['author'] for c in changes))
                })
            
            file_summary.sort(key=lambda x: x['total_changes'], reverse=True)
            
            self._save_json(file_history, "file_history.json")
            self._save_csv(file_summary, "file_summary.csv")
            
            self.stats['files_tracked'] = len(file_history)
            self.logger.info(f"✓ Tracked {len(file_history)} files")
            return file_history
            
        except Exception as e:
            self.logger.error(f"Failed to extract file history: {e}")
            return {}
    
    def extract_all(self) -> bool:
        """Extract all data"""
        self.logger.info("="*80)
        self.logger.info(f"Starting extraction: {self.repo_name}")
        self.logger.info("="*80)
        
        start = datetime.now()
        
        # Clone
        if not self.clone_repository():
            return False
        
        # Extract data
        self.extract_repository_info()
        commits = self.extract_commits()
        self.extract_branches()
        self.extract_tags()
        self.extract_contributors(commits)
        self.extract_file_history(commits)
        
        # Calculate duration
        duration = (datetime.now() - start).total_seconds()
        self.stats['end_time'] = datetime.now().isoformat()
        self.stats['duration_seconds'] = duration
        
        # Save stats
        self._save_json(self.stats, "extraction_stats.json")
        
        # Cleanup
        if self.clone_dir.exists():
            try:
                # Windows fix: handle permission errors
                def handle_remove_readonly(func, path, exc):
                    import stat
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                
                shutil.rmtree(self.clone_dir, onerror=handle_remove_readonly)
                self.logger.info("✓ Cleaned up clone directory")
            except Exception as e:
                self.logger.warning(f"Could not cleanup clone directory: {e}")
        
        self.logger.info("="*80)
        self.logger.info(f"✓ Extraction completed in {duration:.1f}s")
        self.logger.info(f"✓ Data saved to: {self.output_dir}")
        self.logger.info("="*80)
        
        return True


def main():
    """CLI interface"""
    import sys
    
    print("="*80)
    print("Git Repository Data Extractor")
    print("="*80)
    
    # Get inputs
    repo_url = input("\nRepository URL: ").strip()
    token = input("GitHub token (optional, press Enter to skip): ").strip() or None
    
    max_commits_input = input("Max commits to extract (press Enter for all): ").strip()
    max_commits = int(max_commits_input) if max_commits_input.isdigit() else None
    
    # Extract
    extractor = GitExtractor(
        repo_url=repo_url,
        github_token=token,
        max_commits=max_commits
    )
    
    success = extractor.extract_all()
    
    if success:
        print("\n✅ Extraction successful!")
        print(f"Output: {extractor.output_dir}")
    else:
        print("\n❌ Extraction failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
