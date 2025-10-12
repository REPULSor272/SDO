from fastapi import APIRouter
from .auth import router as auth_router
from .files import router as files_router
from .users import router as users_router
from .subjects import router as subjects_router
from .files import router as files_router
from .teachers import router as teachers_router
from .other import router as other_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(files_router)
router.include_router(users_router)
router.include_router(subjects_router)
router.include_router(files_router)
router.include_router(teachers_router)
router.include_router(other_router)