import pickle
import numpy as np
from src.embeddings.instructor_embeddings import InstructorEmbeddings
from src.utils.data_loader import load_initiatives_data

def precompute_embeddings():
    """Pre-calcula embeddings para reducir tiempo de carga"""
    
    # Cargar datos
    initiatives = load_initiatives_data("data/raw/iniciativas.xlsx")
    sdg_indicators = load_sdg_indicators("data/raw/sdg_indicators.csv")
    
    # Inicializar modelo
    embedder = InstructorEmbeddings()
    
    # Calcular embeddings
    print("Calculando embeddings de iniciativas...")
    initiatives_embeddings = embedder.encode(
        initiatives['descripcion'].tolist(),
        instruction="Representa la siguiente iniciativa territorial:"
    )
    
    print("Calculando embeddings de ODS...")
    sdg_embeddings = embedder.encode(
        sdg_indicators['indicator_text'].tolist(),
        instruction="Representa el siguiente indicador ODS:"
    )
    
    # Guardar embeddings
    embeddings_data = {
        'initiatives': {
            'texts': initiatives['descripcion'].tolist(),
            'embeddings': initiatives_embeddings,
            'metadata': initiatives[['id', 'nombre', 'municipio']].to_dict('records')
        },
        'sdg': {
            'texts': sdg_indicators['indicator_text'].tolist(),
            'embeddings': sdg_embeddings,
            'metadata': sdg_indicators[['goal', 'target', 'indicator']].to_dict('records')
        }
    }
    
    output_path = Path("data/embeddings/precomputed_embeddings.pkl")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        pickle.dump(embeddings_data, f)
    
    print(f"Embeddings guardados en {output_path}")
    print(f"Tamaño del archivo: {output_path.stat().st_size / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    precompute_embeddings()