from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from api import preprocess, chat, healthy
from utils.logger import logger
import uvicorn



app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="An application to chat with your files using LLMs and Vector Databases.",   
)
# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/", status_code=status.HTTP_200_OK, tags=["Root"])
async def root():
    """
    Root endpoint to verify if the application is running.
    """
    return {
        "message": "Welcome to the Chat with Files API!",
        "documentation":"/docs"
        }
    
# Include API routers
app.include_router(healthy.router)
app.include_router(preprocess.router)
app.include_router(chat.router)

if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME} version {settings.VERSION} on port {settings.WS_PORT} ...")
    uvicorn.run(
        app,
        host=settings.WS_HOST,
        port=int(settings.WS_PORT),
        )