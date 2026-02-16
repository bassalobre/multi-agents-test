import os

from dotenv import load_dotenv

from src.logger import logger

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    logger.warning("WARNING: OPENAI_API_KEY not found. API might fail.")

if not os.getenv("QDRANT_URL"):
    logger.warning("WARNING: QDRANT_URL not found. API might fail.")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
QDRANT_URL=os.getenv("QDRANT_URL")
QDRANT_API_KEY=os.getenv("QDRANT_API_KEY", "")
