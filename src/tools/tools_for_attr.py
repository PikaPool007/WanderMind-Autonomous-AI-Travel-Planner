import os
import pandas as pd
from langchain_chroma import Chroma

from src.LLMs.openaillm import OpenAiLLM
from src.tools.logger import logger


class AttractionTools:
    def __init__(self):
        try:
            df = pd.read_csv("src\\Data\\combined.csv")
            self.attractions_df = df[["name", "main_category", "categories", "city", "country", "state", "broader_category"]]
            logger.info("✅ Successfully loaded attractions dataset from combined.csv")
        except Exception as e:
            logger.exception(f"❌ Failed to load attractions dataset: {e}")

    def create_chunks(self):
        try:
            grouped = self.attractions_df.groupby('city')
            chunks, metadata = [], []

            for city, city_df in grouped:
                state = city_df["state"].iloc[0]
                country = city_df["country"].iloc[0]

                text = (
                    f"Tourist attractions in {city}, {state}, {country} include: " +
                    " ".join(
                        f"{row['name']} ({row['main_category']}, {row['broader_category']}) — "
                        f"{row['categories']}."
                        for _, row in city_df.iterrows()
                    )
                )

                chunks.append(text)
                metadata.append({
                    "city": city,
                    "state": state,
                    "country": country,
                    "num_attractions": len(city_df),
                    "unique_categories": ", ".join(city_df["broader_category"].unique())
                })

            logger.info(f"🧩 Created text chunks and metadata for {len(chunks)} cities.")
            return chunks, metadata

        except Exception as e:
            logger.exception(f"❌ Error while creating attraction chunks: {e}")
            return [], []

    def create_vector_db(self):
        try:
            embedding = OpenAiLLM.get_llm_embedding()
            vector_db_path = "./vector_db/"

            if os.path.exists(vector_db_path):
                logger.info("📁 Existing vector database found, loading from disk.")
                db = Chroma(
                    embedding_function=embedding,
                    persist_directory=vector_db_path
                )
            else:
                logger.info("🚀 No vector database found. Creating a new one.")
                chunks, metadata = self.create_chunks()
                db = Chroma.from_texts(
                    texts=chunks,
                    embedding=embedding,
                    metadatas=metadata,
                    persist_directory=vector_db_path
                )
                logger.info(f"✅ Vector DB created with {len(chunks)} city chunks.")

            return db

        except Exception as e:
            logger.exception(f"❌ Error while creating or loading vector DB: {e}")
            return None

    def create_retriever(self):
        try:
            retriever = self.create_vector_db().as_retriever()
            logger.info("🔍 Successfully created Chroma retriever.")
            return retriever
        except Exception as e:
            logger.exception(f"❌ Error creating retriever: {e}")
            return None
