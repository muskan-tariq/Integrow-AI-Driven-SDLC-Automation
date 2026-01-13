# API Routes Package

from . import auth_router
from . import user_router
from . import project_router
from . import requirements_router
from . import user_stories_router
from . import uml_router
from . import code_generation_router
from . import dashboard_router
from . import review_router
from . import debt_router

__all__ = [
    "auth_router",
    "user_router",
    "project_router",
    "requirements_router",
    "user_stories_router",
    "uml_router",
    "code_generation_router",
    "dashboard_router",
    "review_router",
    "debt_router",
]
