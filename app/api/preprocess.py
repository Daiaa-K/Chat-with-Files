from fastapi import APIRouter, status , HTTPException
from services.preprocessing import Preprocessing
from utils.logger import logger

router = APIRouter()

@router.post("/preprocess", status_code = status.HTTP_200_OK, tags=["Preprocess"])
async def preprocess(file_url: str):
    """
    preprocess endpoint to preprocess the file from the given URL, embed + Pinecone
    """
    
    try:
        logger.info(f"Starting preprocessing for file: {file_url}")
        preprocessor = Preprocessing(file_path=file_url)
        vector_store = preprocessor.preprocess()
        logger.info(f"Preprocessing completed for file: {file_url}")
        index = preprocessor.pc.Index(preprocessor.index_name)
        stats = index.describe_index_stats()
        vector_count = stats["total_vector_count"]
        return {
            "status":"Success",
            "index_name": preprocessor.index_name,
            "message":f"File preprocessed and embeddings stored in Pinecone,{vector_count} vectors created."
        }
    except Exception as e:
        logger.error(f"Error during preprocessing: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during preprocessing.")