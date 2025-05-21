"""
GitHub Repository Integration

This module provides functionality for interacting with GitHub repositories,
including cloning, committing changes, and managing version control.
"""

import os
import git
import time
import logging
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubIntegration:
    """Class for interacting with GitHub repositories."""
    
    def __init__(self, repo_url: str, local_path: str, username: str, email: str):
        """
        Initialize GitHub integration.
        
        Args:
            repo_url: URL of the GitHub repository
            local_path: Local path to clone the repository to
            username: GitHub username for commits
            email: GitHub email for commits
        """
        self.repo_url = repo_url
        self.local_path = local_path
        self.username = username
        self.email = email
        
        # Clone repository if it doesn't exist
        if not os.path.exists(os.path.join(local_path, '.git')):
            self.clone_repository()
        
        self.repo = git.Repo(local_path)
        
        # Configure Git identity
        with self.repo.config_writer() as git_config:
            git_config.set_value('user', 'name', username)
            git_config.set_value('user', 'email', email)
        
        logger.info(f"Initialized GitHub integration for repository: {repo_url}")
    
    def clone_repository(self):
        """Clone the repository to the local path."""
        try:
            logger.info(f"Cloning repository {self.repo_url} to {self.local_path}")
            os.makedirs(self.local_path, exist_ok=True)
            git.Repo.clone_from(self.repo_url, self.local_path)
            logger.info("Repository cloned successfully")
        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            raise
    
    def pull_changes(self):
        """Pull the latest changes from the remote repository."""
        try:
            logger.info("Pulling latest changes from remote")
            origin = self.repo.remotes.origin
            origin.pull()
            logger.info("Pull completed successfully")
        except Exception as e:
            logger.error(f"Error pulling changes: {e}")
            raise
    
    def has_changes(self) -> bool:
        """
        Check if there are uncommitted changes in the repository.
        
        Returns:
            True if there are uncommitted changes, False otherwise
        """
        return self.repo.is_dirty()
    
    def get_changed_files(self) -> List[str]:
        """
        Get a list of changed files in the repository.
        
        Returns:
            List of changed file paths
        """
        return [item.a_path for item in self.repo.index.diff(None)]
    
    def stage_file(self, file_path: str):
        """
        Stage a file for commit.
        
        Args:
            file_path: Path to the file to stage
        """
        try:
            logger.info(f"Staging file: {file_path}")
            self.repo.git.add(file_path)
        except Exception as e:
            logger.error(f"Error staging file {file_path}: {e}")
            raise
    
    def stage_all_changes(self):
        """Stage all changes for commit."""
        try:
            logger.info("Staging all changes")
            self.repo.git.add(A=True)
        except Exception as e:
            logger.error(f"Error staging all changes: {e}")
            raise
    
    def commit_changes(self, message: str) -> Optional[git.Commit]:
        """
        Commit staged changes with the given message.
        
        Args:
            message: Commit message
            
        Returns:
            The commit object if successful, None otherwise
        """
        try:
            if not self.repo.is_dirty():
                logger.info("No changes to commit")
                return None
            
            logger.info(f"Committing changes with message: {message}")
            return self.repo.index.commit(message)
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            raise
    
    def push_changes(self):
        """Push commits to the remote repository."""
        try:
            logger.info("Pushing changes to remote")
            origin = self.repo.remotes.origin
            origin.push()
            logger.info("Push completed successfully")
        except Exception as e:
            logger.error(f"Error pushing changes: {e}")
            raise
    
    def auto_commit_and_push(self, message_prefix: str = "Update") -> bool:
        """
        Automatically commit all changes and push to remote.
        
        Args:
            message_prefix: Prefix for the commit message
            
        Returns:
            True if changes were committed and pushed, False otherwise
        """
        try:
            if not self.has_changes():
                logger.info("No changes to commit")
                return False
            
            changed_files = self.get_changed_files()
            if not changed_files:
                logger.info("No changed files detected")
                return False
            
            # Create a descriptive commit message
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            file_list = ", ".join(changed_files[:5])
            if len(changed_files) > 5:
                file_list += f" and {len(changed_files) - 5} more files"
            
            message = f"{message_prefix}: {file_list} ({timestamp})"
            
            # Stage, commit and push
            self.stage_all_changes()
            commit = self.commit_changes(message)
            if commit:
                self.push_changes()
                logger.info(f"Successfully committed and pushed changes: {message}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error in auto_commit_and_push: {e}")
            return False
    
    def get_commit_history(self, max_count: int = 10) -> List[Dict[str, Any]]:
        """
        Get the commit history of the repository.
        
        Args:
            max_count: Maximum number of commits to retrieve
            
        Returns:
            List of commit information dictionaries
        """
        try:
            commits = []
            for commit in self.repo.iter_commits(max_count=max_count):
                commits.append({
                    'hash': commit.hexsha,
                    'author': f"{commit.author.name} <{commit.author.email}>",
                    'date': commit.committed_datetime,
                    'message': commit.message,
                    'files_changed': len(commit.stats.files)
                })
            return commits
        except Exception as e:
            logger.error(f"Error getting commit history: {e}")
            return []
    
    def checkout_branch(self, branch_name: str, create: bool = False) -> bool:
        """
        Checkout a branch.
        
        Args:
            branch_name: Name of the branch to checkout
            create: Whether to create the branch if it doesn't exist
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Checking out branch: {branch_name}")
            if create and branch_name not in self.repo.heads:
                self.repo.git.checkout('-b', branch_name)
            else:
                self.repo.git.checkout(branch_name)
            return True
        except Exception as e:
            logger.error(f"Error checking out branch {branch_name}: {e}")
            return False
    
    def merge_branch(self, branch_name: str) -> bool:
        """
        Merge a branch into the current branch.
        
        Args:
            branch_name: Name of the branch to merge
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Merging branch {branch_name} into current branch")
            self.repo.git.merge(branch_name)
            return True
        except Exception as e:
            logger.error(f"Error merging branch {branch_name}: {e}")
            return False
    
    def handle_merge_conflicts(self, strategy: str = 'ours') -> bool:
        """
        Handle merge conflicts using the specified strategy.
        
        Args:
            strategy: Merge strategy ('ours', 'theirs', or 'manual')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if strategy == 'ours':
                logger.info("Resolving merge conflicts using 'ours' strategy")
                self.repo.git.checkout('--ours', '.')
                self.stage_all_changes()
                return True
            elif strategy == 'theirs':
                logger.info("Resolving merge conflicts using 'theirs' strategy")
                self.repo.git.checkout('--theirs', '.')
                self.stage_all_changes()
                return True
            else:
                logger.warning("Manual conflict resolution required")
                return False
        except Exception as e:
            logger.error(f"Error handling merge conflicts: {e}")
            return False