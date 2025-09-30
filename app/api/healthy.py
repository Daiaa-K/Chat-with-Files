from fastapi import APIRouter, status
from config.settings import settings

router = APIRouter()

@router.get("/health", status_code = status.HTTP_200_OK, tags=["Health Check"])
async def health_check():
    """
    Health check endpoint to verify if the application is running.
    """
    return{
        "status":"Healthy",
        "app_name":settings.APP_NAME,
        "version":settings.VERSION
    }