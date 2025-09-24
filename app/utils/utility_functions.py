import os
import glob
from logger import logger
from config.settings import settings

def clean_up_sessions(folder:str,max_sessions: int = settings.MAX_SESSIONS):
    """Clean up old session files in the specified folder.

    Args:
        folder (str): _description_
        max_sessions (int, optional): _description_. Defaults to 10.
    """
    
    files = glob.glob(os.path.join(folder,"chat_history_*.json"))
    
    if len(files) > max_sessions:
        # sort files by time
        files.sort(key=os.path.getmtime)
        
        for f in files[:-max_sessions]:
            os.remove(f)
    logger.info(f"Cleaned up old session files in {folder}, kept the latest {max_sessions} sessions.")

            