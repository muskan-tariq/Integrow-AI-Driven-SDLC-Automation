from github import Github, GithubException
from typing import Optional, Dict, Any, List
import logging

from config import settings
from services.encryption import decrypt_token

logger = logging.getLogger(__name__)

class GitHubAgent:
    """Agent for GitHub operations"""
    
    def __init__(self, access_token: str):
        """Initialize with GitHub access token"""
        self.github = Github(access_token)
        self.user = self.github.get_user()
    
    @classmethod
    def from_encrypted_token(cls, encrypted_token: str):
        """Create agent from encrypted token"""
        access_token = decrypt_token(encrypted_token)
        return cls(access_token)
    
    async def create_repository(
        self, 
        name: str, 
        description: Optional[str] = None,
        private: bool = True,
        auto_init: bool = False
    ) -> Dict[str, Any]:
        """Create a new GitHub repository"""
        try:
            repo = self.user.create_repo(
                name=name,
                description=description or "",
                private=private,
                auto_init=auto_init
            )
            
            return {
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name,
                "html_url": repo.html_url,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url,
                "default_branch": repo.default_branch or "main",
                "private": repo.private,
                "created_at": repo.created_at.isoformat(),
            }
            
        except GithubException as e:
            logger.error(f"GitHub API error creating repository: {e}")
            if e.status == 422:
                # Repository already exists
                raise ValueError(f"Repository '{name}' already exists")
            raise
        except Exception as e:
            logger.error(f"Error creating repository: {e}")
            raise
    
    async def get_repository(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """Get repository information"""
        try:
            repo = self.user.get_repo(repo_name)
            return {
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name,
                "html_url": repo.html_url,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url,
                "default_branch": repo.default_branch or "main",
                "private": repo.private,
                "created_at": repo.created_at.isoformat(),
            }
        except GithubException as e:
            if e.status == 404:
                return None
            logger.error(f"GitHub API error getting repository: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting repository: {e}")
            raise
    
    async def create_branch(self, repo_name: str, branch_name: str, from_branch: str = "main"):
        """Create a new branch in the repository"""
        try:
            repo = self.user.get_repo(repo_name)
            
            # Check if branch already exists
            try:
                repo.get_branch(branch_name)
                logger.info(f"Branch '{branch_name}' already exists in {repo_name}")
                return True  # Branch exists, no need to create
            except GithubException as e:
                if e.status != 404:
                    raise  # Re-raise if it's not a "not found" error
                # Branch doesn't exist, continue to create it
            
            # Get source branch and create new branch
            source_branch = repo.get_branch(from_branch)
            repo.create_git_ref(f"refs/heads/{branch_name}", source_branch.commit.sha)
            logger.info(f"Created branch '{branch_name}' from '{from_branch}' in {repo_name}")
            return True
            
        except GithubException as e:
            logger.error(f"GitHub API error creating branch: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating branch: {e}")
            raise
    
    async def get_user_repos(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get user's repositories"""
        try:
            repos = []
            for repo in self.user.get_repos()[:limit]:
                repos.append({
                    "id": repo.id,
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "html_url": repo.html_url,
                    "private": repo.private,
                    "created_at": repo.created_at.isoformat(),
                })
            return repos
        except GithubException as e:
            logger.error(f"GitHub API error getting repositories: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting repositories: {e}")
            raise
    
    async def create_webhook(
        self, 
        repo_name: str, 
        webhook_url: str, 
        events: List[str] = None
    ):
        """Create a webhook for the repository"""
        try:
            if events is None:
                events = ["push", "pull_request"]
            
            repo = self.user.get_repo(repo_name)
            hook = repo.create_hook(
                "web",
                {
                    "url": webhook_url,
                    "content_type": "json",
                    "insecure_ssl": "0"
                },
                events=events,
                active=True
            )
            
            return {
                "id": hook.id,
                "url": hook.config["url"],
                "events": hook.events,
                "active": hook.active
            }
            
        except GithubException as e:
            logger.error(f"GitHub API error creating webhook: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating webhook: {e}")
            raise

    async def create_or_update_file(
        self,
        repo_name: str,
        path: str,
        content: str,
        message: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """Create or update a file in the repository"""
        try:
            repo = self.user.get_repo(repo_name)
            
            try:
                # Try to get existing file to get its SHA
                contents = repo.get_contents(path, ref=branch)
                result = repo.update_file(
                    path,
                    message,
                    content,
                    contents.sha,
                    branch=branch
                )
                logger.info(f"Updated file '{path}' in {repo_name} (branch: {branch})")
            except GithubException as e:
                if e.status == 404:
                    # File doesn't exist, create it
                    result = repo.create_file(
                        path,
                        message,
                        content,
                        branch=branch
                    )
                    logger.info(f"Created file '{path}' in {repo_name} (branch: {branch})")
                else:
                    raise
            
            return {
                "content": result["content"].name,
                "commit": result["commit"].sha
            }
            
        except GithubException as e:
            logger.error(f"GitHub API error creating/updating file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating/updating file: {e}")
            raise

    async def delete_file(
        self,
        repo_name: str,
        path: str,
        message: str,
        branch: str = "main"
    ) -> bool:
        """Delete a file from the repository"""
        try:
            repo = self.user.get_repo(repo_name)
            
            try:
                # Get file to get SHA
                contents = repo.get_contents(path, ref=branch)
                repo.delete_file(
                    path,
                    message,
                    contents.sha,
                    branch=branch
                )
                logger.info(f"Deleted file '{path}' in {repo_name} (branch: {branch})")
                return True
            except GithubException as e:
                if e.status == 404:
                    logger.warning(f"File '{path}' not found in {repo_name}, skipping delete")
                    return False
                raise
                
        except GithubException as e:
            logger.error(f"GitHub API error deleting file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            raise