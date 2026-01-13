import git
from git import Repo, InvalidGitRepositoryError
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
import os
import yaml
from datetime import datetime

logger = logging.getLogger(__name__)

class GitAgent:
    """Agent for local Git operations"""
    
    AGENT_NAME = "InteGrow Agent"
    AGENT_EMAIL = "agent@integrow.ai"
    
    def __init__(self, repo_path: str):
        """Initialize with repository path"""
        self.repo_path = Path(repo_path)
        self.repo: Optional[Repo] = None
        
        if self.repo_path.exists() and (self.repo_path / ".git").exists():
            try:
                self.repo = Repo(str(self.repo_path))
            except InvalidGitRepositoryError:
                logger.warning(f"Invalid Git repository at {repo_path}")
    
    async def init_repository(self, remote_url: str) -> bool:
        """Initialize Git repository with remote"""
        try:
            # Create directory if it doesn't exist
            self.repo_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize Git repository
            self.repo = Repo.init(str(self.repo_path))
            
            # Configure Git identity
            config_writer = self.repo.config_writer()
            config_writer.set_value("user", "name", self.AGENT_NAME)
            config_writer.set_value("user", "email", self.AGENT_EMAIL)
            # Set default branch to main
            config_writer.set_value("init", "defaultBranch", "main")
            config_writer.release()
            
            # Add remote origin
            self.repo.create_remote("origin", remote_url)
            
            logger.info(f"Initialized Git repository at {self.repo_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Git repository: {e}")
            raise
    
    async def create_commit(self, message: str, files: List[str] = None) -> str:
        """Create a commit with specified files or all changes"""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            # Add files to staging
            if files:
                for file_path in files:
                    self.repo.index.add([file_path])
            else:
                # Add all files
                self.repo.git.add(".")
            
            # Rename current branch to 'main' if it's not already
            # This handles both new repos and repos with 'master' branch
            try:
                current_branch = self.repo.active_branch.name
                if current_branch != "main":
                    self.repo.git.branch("-M", "main")
            except:
                # No active branch yet (first commit), will be created as main
                pass
            
            # Create commit
            commit = self.repo.index.commit(
                message,
                author=git.Actor(self.AGENT_NAME, self.AGENT_EMAIL),
                committer=git.Actor(self.AGENT_NAME, self.AGENT_EMAIL)
            )
            
            logger.info(f"Created commit: {commit.hexsha[:8]} - {message}")
            return commit.hexsha
            
        except Exception as e:
            logger.error(f"Error creating commit: {e}")
            raise
    
    async def push_to_remote(self, branch: str = "main", remote: str = "origin") -> bool:
        """Push changes to remote repository"""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            # Ensure we're on the correct branch
            try:
                current_branch = self.repo.active_branch.name
                if current_branch != branch:
                    logger.warning(f"Current branch '{current_branch}' != target branch '{branch}'")
            except:
                pass
            
            # Push to remote with set-upstream
            origin = self.repo.remote(remote)
            origin.push(refspec=f"{branch}:{branch}", set_upstream=True)
            
            logger.info(f"Pushed branch '{branch}' to remote '{remote}'")
            return True
            
        except Exception as e:
            logger.error(f"Error pushing to remote: {e}")
            raise
    
    async def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """Create a new branch"""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            # Create new branch
            new_branch = self.repo.create_head(branch_name)
            
            if checkout:
                new_branch.checkout()
            
            logger.info(f"Created branch '{branch_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error creating branch: {e}")
            raise
    
    async def switch_branch(self, branch_name: str) -> bool:
        """Switch to specified branch"""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            self.repo.heads[branch_name].checkout()
            logger.info(f"Switched to branch '{branch_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error switching branch: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current Git status"""
        try:
            if not self.repo:
                return {"error": "Repository not initialized"}
            
            # Get current branch
            current_branch = str(self.repo.active_branch)
            
            # Get status
            untracked_files = self.repo.untracked_files
            changed_files = [item.a_path for item in self.repo.index.diff(None)]
            staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
            
            # Get last commit
            last_commit = None
            if self.repo.heads:
                try:
                    commit = self.repo.head.commit
                    last_commit = {
                        "sha": commit.hexsha[:8],
                        "message": commit.message.strip(),
                        "author": str(commit.author),
                        "date": commit.committed_datetime.isoformat()
                    }
                except Exception:
                    pass
            
            return {
                "current_branch": current_branch,
                "untracked_files": untracked_files,
                "changed_files": changed_files,
                "staged_files": staged_files,
                "last_commit": last_commit,
                "total_commits": len(list(self.repo.iter_commits())) if self.repo.heads else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting Git status: {e}")
            return {"error": str(e)}
    
    async def pull_from_remote(self, branch: str = "main", remote: str = "origin") -> bool:
        """Pull changes from remote repository"""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            origin = self.repo.remote(remote)
            origin.pull(branch)
            
            logger.info(f"Pulled changes from remote '{remote}' branch '{branch}'")
            return True
            
        except Exception as e:
            logger.error(f"Error pulling from remote: {e}")
            raise
    
    async def commit_requirement(
        self, 
        requirement_data: Dict[str, Any], 
        commit_message: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Commit a requirement to .integrow/requirements/ directory
        
        Args:
            requirement_data: Dictionary containing requirement data
            commit_message: Git commit message
            branch: Target branch (default: main)
            
        Returns:
            Dictionary with commit_sha, file_path, and version
        """
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            # Create .integrow/requirements directory if it doesn't exist
            integrow_dir = self.repo_path / ".integrow" / "requirements"
            integrow_dir.mkdir(parents=True, exist_ok=True)
            
            # Get next version number
            version = self._get_next_requirement_version(integrow_dir)
            
            # Create YAML file
            file_name = f"requirements_v{version}.yaml"
            file_path = integrow_dir / file_name
            relative_path = f".integrow/requirements/{file_name}"
            
            # Prepare YAML content
            yaml_content = self._format_requirement_yaml(requirement_data, version)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            logger.info(f"Created requirement file: {relative_path}")
            
            # Commit the file
            commit_sha = await self.create_commit(
                message=commit_message,
                files=[relative_path]
            )
            
            return {
                "commit_sha": commit_sha,
                "file_path": relative_path,
                "version": version,
                "full_path": str(file_path)
            }
            
        except Exception as e:
            logger.error(f"Error committing requirement: {e}")
            raise
    
    
    async def commit_file(
        self,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Commit any file with content to repository
        
        Args:
            file_path: Relative path from repo root (e.g., '.integrow/user-stories/REQ-123.md')
            content: File content as string
            commit_message: Git commit message
            branch: Target branch (default: main)
            
        Returns:
            Dictionary with sha, file_path
        """
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            # Construct full path
            full_path = self.repo_path / file_path
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created file: {file_path}")
            
            # Commit the file
            commit_sha = await self.create_commit(
                message=commit_message,
                files=[file_path]
            )
            
            return {
                "sha": commit_sha,
                "file_path": file_path,
                "full_path": str(full_path)
            }
            
        except Exception as e:
            logger.error(f"Error committing file: {e}")
            raise

    async def commit_multiple_files(
        self,
        files: List[Dict[str, str]],
        commit_message: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Write and commit multiple files in a single commit.
        
        Args:
            files: List of dicts with 'path' and 'content' keys
            commit_message: Git commit message
            branch: Target branch (default: main)
            
        Returns:
            Dictionary with sha, files_committed count
        """
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            file_paths = []
            
            for file_data in files:
                file_path = file_data.get("path")
                content = file_data.get("content", "")
                
                if not file_path:
                    continue
                
                # Construct full path
                full_path = self.repo_path / file_path
                
                # Create parent directories
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write content to file
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                file_paths.append(file_path)
                logger.info(f"Created file: {file_path}")
            
            if not file_paths:
                return {"sha": None, "files_committed": 0}
            
            # Commit all files in one commit
            commit_sha = await self.create_commit(
                message=commit_message,
                files=file_paths
            )
            
            return {
                "sha": commit_sha,
                "files_committed": len(file_paths),
                "file_paths": file_paths
            }
            
        except Exception as e:
            logger.error(f"Error committing multiple files: {e}")
            raise

    def _get_next_requirement_version(self, integrow_dir: Path) -> int:
        """Get the next version number for requirements"""
        try:
            # List existing requirement files
            existing_files = list(integrow_dir.glob("requirements_v*.yaml"))
            
            if not existing_files:
                return 1
            
            # Extract version numbers
            versions = []
            for file in existing_files:
                # Parse version from filename: requirements_v{X}.yaml
                try:
                    version_str = file.stem.split('_v')[1]
                    versions.append(int(version_str))
                except (IndexError, ValueError):
                    logger.warning(f"Could not parse version from file: {file.name}")
                    continue
            
            if not versions:
                return 1
            
            return max(versions) + 1
            
        except Exception as e:
            logger.error(f"Error getting next version: {e}")
            return 1
    
    def _format_requirement_yaml(self, requirement_data: Dict[str, Any], version: int) -> Dict[str, Any]:
        """Format requirement data for YAML export"""
        yaml_data = {
            "version": version,
            "metadata": {
                "created_at": requirement_data.get("created_at", datetime.utcnow().isoformat()),
                "approved_at": requirement_data.get("approved_at", datetime.utcnow().isoformat()),
                "approved_by": requirement_data.get("approved_by"),
                "requirement_id": str(requirement_data.get("id", "")),
                "project_id": str(requirement_data.get("project_id", ""))
            },
            "requirement": {
                "raw_text": requirement_data.get("raw_text", ""),
                "status": requirement_data.get("status", "approved")
            },
            "analysis": {}
        }
        
        # Add parsed entities if available
        if "parsed_entities" in requirement_data and requirement_data["parsed_entities"]:
            entities = requirement_data["parsed_entities"]
            yaml_data["analysis"]["parsed_entities"] = {
                "actors": entities.get("actors", []),
                "actions": entities.get("actions", []),
                "entities": entities.get("entities", []),
                "constraints": entities.get("constraints", []),
                "dependencies": entities.get("dependencies", [])
            }
        
        # Add ambiguity analysis
        if "ambiguity_analysis" in requirement_data and requirement_data["ambiguity_analysis"]:
            ambiguity = requirement_data["ambiguity_analysis"]
            yaml_data["analysis"]["ambiguity"] = {
                "score": ambiguity.get("score", 0.0),
                "total_issues": ambiguity.get("total_issues", 0),
                "issues": [
                    {
                        "term": issue.get("term", ""),
                        "severity": issue.get("severity", "low"),
                        "explanation": issue.get("explanation", ""),
                        "suggestions": issue.get("suggestions", [])
                    }
                    for issue in ambiguity.get("issues", [])
                ]
            }
        
        # Add completeness analysis
        if "completeness_analysis" in requirement_data and requirement_data["completeness_analysis"]:
            completeness = requirement_data["completeness_analysis"]
            yaml_data["analysis"]["completeness"] = {
                "score": completeness.get("score", 0.0),
                "total_missing": completeness.get("total_missing", 0),
                "missing_items": [
                    {
                        "category": item.get("category", ""),
                        "severity": item.get("severity", "low"),
                        "description": item.get("description", ""),
                        "suggestion": item.get("suggestion", "")
                    }
                    for item in completeness.get("missing_items", [])
                ]
            }
        
        # Add ethics analysis
        if "ethics_analysis" in requirement_data and requirement_data["ethics_analysis"]:
            ethics = requirement_data["ethics_analysis"]
            yaml_data["analysis"]["ethics"] = {
                "score": ethics.get("score", 0.0),
                "total_issues": ethics.get("total_issues", 0),
                "ethical_issues": [
                    {
                        "issue_type": issue.get("issue_type", ""),
                        "category": issue.get("category", ""),
                        "severity": issue.get("severity", "low"),
                        "description": issue.get("description", ""),
                        "recommendation": issue.get("recommendation", "")
                    }
                    for issue in ethics.get("ethical_issues", [])
                ]
            }
        
        # Add overall quality score
        yaml_data["analysis"]["overall_quality_score"] = requirement_data.get("overall_quality_score", 0.0)
        
        return yaml_data
    
    async def get_requirement_history(self, requirement_id: str) -> List[Dict[str, Any]]:
        """
        Get commit history for all versions of a requirement
        
        Args:
            requirement_id: UUID of the requirement
            
        Returns:
            List of commit information dictionaries
        """
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            integrow_dir = self.repo_path / ".integrow" / "requirements"
            if not integrow_dir.exists():
                return []
            
            # Get all requirement version files
            requirement_files = list(integrow_dir.glob("requirements_v*.yaml"))
            history = []
            
            for file in sorted(requirement_files):
                relative_path = f".integrow/requirements/{file.name}"
                
                # Get commits for this file
                try:
                    commits = list(self.repo.iter_commits(paths=relative_path, max_count=1))
                    if commits:
                        commit = commits[0]
                        
                        # Read YAML to check if it matches requirement_id
                        with open(file, 'r', encoding='utf-8') as f:
                            content = yaml.safe_load(f)
                            
                        if content.get("metadata", {}).get("requirement_id") == requirement_id:
                            history.append({
                                "version": content.get("version", 0),
                                "commit_sha": commit.hexsha[:8],
                                "commit_message": commit.message.strip(),
                                "author": str(commit.author),
                                "date": commit.committed_datetime.isoformat(),
                                "file_path": relative_path
                            })
                except Exception as e:
                    logger.warning(f"Error reading file {file.name}: {e}")
                    continue
            
            return sorted(history, key=lambda x: x["version"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting requirement history: {e}")
            return []
    
    def create_project_structure(self, template: str = "blank"):
        """Create initial project structure based on template"""
        try:
            if template == "blank":
                self._create_blank_structure()
            elif template == "web-app":
                self._create_web_app_structure()
            elif template == "mobile-app":
                self._create_mobile_app_structure()
            elif template == "api":
                self._create_api_structure()
            else:
                self._create_blank_structure()
                
        except Exception as e:
            logger.error(f"Error creating project structure: {e}")
            raise
    
    def _create_blank_structure(self):
        """Create basic project structure"""
        files_to_create = {
            "README.md": self._get_readme_content(),
            ".gitignore": self._get_gitignore_content(),
            "docs/README.md": "# Documentation\n\nProject documentation goes here.\n",
            "src/.gitkeep": "",
        }
        
        for file_path, content in files_to_create.items():
            full_path = self.repo_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
    
    def _create_web_app_structure(self):
        """Create web app project structure"""
        self._create_blank_structure()
        
        additional_files = {
            "src/index.html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>InteGrow Project</title>\n</head>\n<body>\n    <h1>Hello InteGrow!</h1>\n</body>\n</html>\n",
            "src/styles/main.css": "/* Main styles */\nbody {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n}\n",
            "src/scripts/main.js": "// Main JavaScript\nconsole.log('InteGrow project loaded!');\n",
            "package.json": '{\n  "name": "integrow-project",\n  "version": "1.0.0",\n  "description": "InteGrow generated project",\n  "main": "src/index.html",\n  "scripts": {\n    "start": "echo \\"Open src/index.html in your browser\\""\n  }\n}\n'
        }
        
        for file_path, content in additional_files.items():
            full_path = self.repo_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
    
    def _create_mobile_app_structure(self):
        """Create mobile app project structure"""
        self._create_blank_structure()
        
        additional_files = {
            "src/App.js": "// Main App Component\nconst App = () => {\n  return (\n    <div>\n      <h1>InteGrow Mobile App</h1>\n    </div>\n  );\n};\n\nexport default App;\n",
            "src/components/README.md": "# Components\n\nReact components go here.\n",
            "src/screens/README.md": "# Screens\n\nMobile app screens go here.\n",
            "src/utils/README.md": "# Utilities\n\nUtility functions go here.\n"
        }
        
        for file_path, content in additional_files.items():
            full_path = self.repo_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
    
    def _create_api_structure(self):
        """Create API project structure"""
        self._create_blank_structure()
        
        additional_files = {
            "src/main.py": "# Main API entry point\nfrom fastapi import FastAPI\n\napp = FastAPI(title='InteGrow API')\n\n@app.get('/')\nasync def root():\n    return {'message': 'InteGrow API is running!'}\n",
            "src/routers/README.md": "# API Routers\n\nAPI route handlers go here.\n",
            "src/models/README.md": "# Data Models\n\nPydantic models go here.\n",
            "src/services/README.md": "# Services\n\nBusiness logic services go here.\n",
            "requirements.txt": "fastapi\nuvicorn[standard]\n",
        }
        
        for file_path, content in additional_files.items():
            full_path = self.repo_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
    
    def _get_readme_content(self) -> str:
        """Generate README content"""
        return f"""# InteGrow Project

This project was created with InteGrow AI-SES Suite.

## Getting Started

1. Clone this repository
2. Follow the setup instructions below
3. Start developing!

## Generated by InteGrow

- **Created**: {Path.cwd().name}
- **Agent**: {self.AGENT_NAME}
- **Email**: {self.AGENT_EMAIL}

## Documentation

See the `docs/` directory for detailed documentation.

## Contributing

This project follows the InteGrow development workflow.
"""
    
    def _get_gitignore_content(self) -> str:
        """Generate .gitignore content"""
        return """# Dependencies
node_modules/
__pycache__/
*.pyc
.env
.env.local
.env.production

# Build outputs
dist/
build/
out/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# InteGrow
.integrow/
"""

    async def delete_file(
        self,
        file_path: str,
        commit_message: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Delete a file and commit the change
        
        Args:
            file_path: Relative path from repo root
            commit_message: Git commit message
            branch: Target branch (default: main)
            
        Returns:
            Dictionary with sha, file_path
        """
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            # Construct full path
            full_path = self.repo_path / file_path
            
            if not full_path.exists():
                logger.warning(f"File to delete does not exist: {full_path}")
                return {"sha": None, "file_path": file_path, "status": "not_found"}
            
            # Delete file
            os.remove(full_path)
            
            logger.info(f"Deleted file: {file_path}")
            
            # Commit the deletion
            self.repo.index.remove([file_path])
            
            commit_sha = await self.create_commit(
                message=commit_message,
                files=None 
            )
            
            return {
                "sha": commit_sha,
                "file_path": file_path,
                "status": "deleted"
            }
            
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            raise