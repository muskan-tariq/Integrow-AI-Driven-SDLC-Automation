from supabase import create_client, Client
from config import settings
import logging

logger = logging.getLogger(__name__)

# Create Supabase client with SERVICE ROLE key to bypass RLS
# This is safe for backend operations as the backend validates requests
supabase_client: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY  # Use service role key instead of anon key
)

class SupabaseService:
    """Service class for Supabase operations"""
    
    def __init__(self):
        self.client = supabase_client
        
    async def get_user_by_github_id(self, github_id: str):
        """Get user by GitHub ID"""
        try:
            response = self.client.table('users').select('*').eq('github_id', github_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by GitHub ID: {e}")
            return None
    
    async def create_user(self, user_data: dict):
        """Create new user"""
        try:
            response = self.client.table('users').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def update_user(self, user_id: str, user_data: dict):
        """Update existing user"""
        try:
            response = self.client.table('users').update(user_data).eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise
    
    async def get_user_projects(self, user_id: str, limit: int = 10, offset: int = 0):
        """Get user's projects with pagination"""
        try:
            response = (
                self.client.table('projects')
                .select('*')
                .eq('user_id', user_id)
                .eq('status', 'active')
                .order('created_at', desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error getting user projects: {e}")
            return []
    
    async def create_project(self, project_data: dict):
        """Create new project"""
        try:
            response = self.client.table('projects').insert(project_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise
    
    async def get_project(self, project_id: str, user_id: str = None):
        """Get project by ID, optionally filtered by user_id"""
        try:
            query = self.client.table('projects').select('*').eq('id', project_id)
            if user_id:
                query = query.eq('user_id', user_id)
            
            response = query.execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting project: {e}")
            return None
    
    async def update_project(self, project_id: str, project_data: dict):
        """Update project"""
        try:
            response = self.client.table('projects').update(project_data).eq('id', project_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            raise
    
    async def log_project_activity(self, activity_data: dict):
        """Log project activity"""
        try:
            response = self.client.table('project_activity').insert(activity_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error logging project activity: {e}")
            # Don't raise exception for logging failures
            return None
    
    def get_requirements_by_project(self, project_id: str):
        """Get all requirements for a project"""
        try:
            response = (
                self.client.table('requirements')
                .select('*')
                .eq('project_id', project_id)
                .order('created_at', desc=True)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error getting requirements by project: {e}")
            return []
    
    # ============================================
    # UML Diagram Methods
    # ============================================
    
    def create_uml_diagram(self, diagram_data: dict):
        """Create new UML diagram"""
        try:
            response = self.client.table('uml_diagrams').insert(diagram_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating UML diagram: {e}")
            raise
    
    def get_uml_diagram(self, diagram_id: str, user_id: str):
        """Get UML diagram by ID"""
        try:
            response = (
                self.client.table('uml_diagrams')
                .select('*')
                .eq('id', diagram_id)
                .eq('user_id', user_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting UML diagram: {e}")
            return None
    
    def get_uml_diagram_by_requirement(self, requirement_id: str, user_id: str):
        """Get latest UML diagram for a requirement"""
        try:
            response = (
                self.client.table('uml_diagrams')
                .select('*')
                .eq('requirement_id', requirement_id)
                .eq('user_id', user_id)
                .order('created_at', desc=True)
                .limit(1)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting UML diagram by requirement: {e}")
            return None
    
    def list_uml_diagrams(self, requirement_id: str, user_id: str, page: int = 1, page_size: int = 10):
        """List UML diagrams for a requirement with pagination"""
        try:
            offset = (page - 1) * page_size
            response = (
                self.client.table('uml_diagrams')
                .select('*')
                .eq('requirement_id', requirement_id)
                .eq('user_id', user_id)
                .order('created_at', desc=True)
                .range(offset, offset + page_size - 1)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error listing UML diagrams: {e}")
            return []
    
    def update_uml_diagram(self, diagram_id: str, user_id: str, update_data: dict):
        """Update UML diagram"""
        try:
            response = (
                self.client.table('uml_diagrams')
                .update(update_data)
                .eq('id', diagram_id)
                .eq('user_id', user_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating UML diagram: {e}")
            raise
    
    def delete_uml_diagram(self, diagram_id: str, user_id: str):
        """Delete UML diagram"""
        try:
            response = (
                self.client.table('uml_diagrams')
                .delete()
                .eq('id', diagram_id)
                .eq('user_id', user_id)
                .execute()
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting UML diagram: {e}")
            return False
    
    def get_user_stories_by_requirement(self, requirement_id: str, user_id: str):
        """
        Get all user stories for a requirement.
        Tries database first, then falls back to reading from GitHub markdown file.
        """
        try:
            # Try database first
            response = (
                self.client.table('user_stories')
                .select('*')
                .eq('requirement_id', requirement_id)
                .order('created_at', desc=False)
                .execute()
            )
            
            if response.data and len(response.data) > 0:
                logger.info(f"Found {len(response.data)} user stories in database for requirement {requirement_id}")
                return response.data
            
            # Fallback to GitHub file if not in database
            logger.info(f"No user stories in database, checking GitHub file for requirement {requirement_id}")
            
            # Get requirement to find project
            requirement = (
                self.client.table('requirements')
                .select('id, project_id')
                .eq('id', requirement_id)
                .eq('user_id', user_id)
                .execute()
            )
            
            if not requirement.data:
                logger.error(f"Requirement {requirement_id} not found")
                return []
            
            project_id = requirement.data[0]['project_id']
            
            # Get project to find local path
            project = (
                self.client.table('projects')
                .select('id, local_path')
                .eq('id', project_id)
                .eq('user_id', user_id)
                .execute()
            )
            
            if not project.data:
                logger.error(f"Project {project_id} not found")
                return []
            
            local_path = project.data[0]['local_path']
            
            # Read user stories from GitHub file
            from pathlib import Path
            
            stories_file = Path(local_path) / ".integrow" / "user-stories" / f"REQ-{requirement_id}.md"
            
            if not stories_file.exists():
                logger.info(f"User stories file not found: {stories_file}")
                return []
            
            # Parse markdown file to extract user stories
            content = stories_file.read_text(encoding='utf-8')
            stories = self._parse_user_stories_from_markdown(content)
            
            logger.info(f"Found {len(stories)} user stories in GitHub file for requirement {requirement_id}")
            return stories
            
            return stories
            
        except Exception as e:
            logger.error(f"Error getting user stories: {e}")
            return []

    def delete_user_stories_by_requirement(self, requirement_id: str):
        """Delete all user stories for a requirement"""
        try:
            self.client.table('user_stories').delete().eq('requirement_id', requirement_id).execute()
            logger.info(f"Deleted user stories for requirement {requirement_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user stories: {e}")
            # Don't throw, just log. Deletion of parent requirement should cleanup or we want best-effort.
            return False
    
    def _parse_user_stories_from_markdown(self, markdown_content: str):
        """Parse user stories from markdown format"""
        import re
        
        stories = []
        
        # Split by story sections (## Story X: Title)
        story_pattern = r'## Story \d+: (.+?)\n\n\*\*Priority\*\*: (.+?)\s+\*\*Story Points\*\*: (.+?)\s+\*\*Tags\*\*: (.+?)\n\n### User Story\n\n(.+?)\n\n### Acceptance Criteria\n\n(.+?)(?=\n---|\n## Story|\Z)'
        
        matches = re.findall(story_pattern, markdown_content, re.DOTALL)
        
        for match in matches:
            title, priority, points, tags, story_text, criteria_text = match
            
            # Parse acceptance criteria (numbered list)
            criteria = re.findall(r'\d+\.\s+(.+?)(?=\n\d+\.|\n---|\Z)', criteria_text, re.DOTALL)
            criteria = [c.strip() for c in criteria]
            
            # Parse story points
            try:
                story_points = int(points.strip()) if points.strip() not in ['Not estimated', 'None'] else None
            except:
                story_points = None
            
            # Parse tags
            tag_list = [t.strip() for t in tags.split(',') if t.strip() and t.strip() != 'None']
            
            story_dict = {
                'id': f"story-{len(stories) + 1}",  # Generate temp ID
                'title': title.strip(),
                'story': story_text.strip(),
                'acceptance_criteria': criteria,
                'priority': priority.strip().lower(),
                'story_points': story_points,
                'tags': tag_list,
                'created_at': None,  # Not available from markdown
            }
            
            stories.append(story_dict)
        
        return stories
    

# Create service instance
supabase_service = SupabaseService()