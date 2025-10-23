from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
import os
from dotenv import load_dotenv

from src.tools.logger import logger

load_dotenv()

env_vars = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_DEPLOYMENT_NAME",
    "AZURE_EMBD_OPENAI_API_VERSION",
    "AZURE_EMBD_DEPLMENT_NAME"
]

# ✅ Log missing environment variables
for var in env_vars:
    if not os.getenv(var):
        logger.warning(f"Environment Variable Missing: {var}")
    os.environ[var] = os.getenv(var)  # retain your existing approach


class OpenAiLLM:

    @staticmethod
    def get_llm_model():
        logger.info("Initializing AzureChatOpenAI LLM model...")
        try:
            llm = AzureChatOpenAI(
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                azure_deployment=os.environ["AZURE_DEPLOYMENT_NAME"],
                api_version=os.environ["AZURE_OPENAI_API_VERSION"],
                temperature=0,
                max_tokens=1000,
                timeout=None,
                max_retries=2
            )
            logger.info("✅ AzureChatOpenAI model initialized successfully")
            return llm

        except Exception as e:
            logger.error("❌ Failed to initialize AzureChatOpenAI model", exc_info=True)
            raise

    @staticmethod
    def get_llm_embedding():
        logger.info("Initializing Azure embeddings model...")
        try:
            embeddings = AzureOpenAIEmbeddings(
                api_version=os.environ["AZURE_EMBD_OPENAI_API_VERSION"],
                model=os.environ["AZURE_EMBD_DEPLMENT_NAME"]
            )
            logger.info("✅ Embeddings model initialized successfully")
            return embeddings

        except Exception as e:
            logger.error("❌ Failed to initialize AzureOpenAIEmbeddings", exc_info=True)
            raise
