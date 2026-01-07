# src/embeddings/instructor_embeddings.py
from sentence_transformers import SentenceTransformer #
import os
from pathlib import Path

class InstructorEmbeddings:
    def __init__(self, model_name="hkunlp/instructor-large", cache_dir="./data/embeddings/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # HF Spaces descargará automáticamente el modelo
        self.model = SentenceTransformer(
            model_name,
            cache_folder=str(self.cache_dir)
        )
    
    def encode(self, texts, instruction="", **kwargs):
        if instruction:
            texts_with_instruction = [[instruction, text] for text in texts]
            return self.model.encode(texts_with_instruction, **kwargs)
        return self.model.encode(texts, **kwargs)