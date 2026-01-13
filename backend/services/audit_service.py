from services.supabase_service import supabase_client
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AuditService:
    @staticmethod
    async def log_event(user_id: str, action: str, resource_id: str = None, details: dict = None, ip_address: str = None):
        """
        Log a security or business critical event to the audit_logs table.
        """
        try:
            data = {
                "user_id": user_id,
                "action": action,
                "resource_id": resource_id,
                "details": details,
                "ip_address": ip_address,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Fire and forget - don't block the main request
            supabase_client.table('audit_logs').insert(data).execute()
            logger.info(f"Audit log created: {action} by {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")

audit_service = AuditService()
