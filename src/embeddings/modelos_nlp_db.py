
# ============================================================================
# Funciones generales PLN
# ============================================================================

import argparse, os, json, hashlib, pandas as pd, numpy as np
from pathlib import Path
import re

def md5_text(s: str) -> str:
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def build_ods_fingerprint(model_name: str, instruction: str, ods_texts: list) -> str:
    concat = model_name + "\n" + instruction + "\n" + "\n".join(ods_texts)
    return md5_text(concat)

def ensure_out_dir(p: str):
    Path(p).mkdir(parents=True, exist_ok=True)

def load_data(patr_tblinput: str, ods_tblinput: str):
    # patr = pd.read_tblinput(patr_tblinput)
    # ods = pd.read_tblinput(ods_tblinput)
    patr = pd.read_excel(patr_tblinput)#, encoding='cp1252')


    ods = pd.read_excel(ods_tblinput)#.iloc[:32,:]
    # Basic validations
    assert {"ID",       "INICIATIVAS", "MUNICIPIO"}.issubset(patr.columns), "PATR CSV must include columns: ID,      INICIATIVAS"
    assert {'OBJETIVO', 'OBJETIVO_META', 'INDICADORES', 'CODIGO_UNSD',
       'ID_OBJETIVO', 'ID_META', 'ID_INDICADORES'}.issubset(ods.columns), "ODS CSV must include columns: OBJETIVO, OBJETIVO_META, INDICADORES, CODIGO_UNSD,ID_OBJETIVO, ID_META, ID_INDICADORES"
    return patr, ods

def make_text_pairs(instruction: str, texts: list):
    return [[instruction, t if isinstance(t,str) else ""] for t in texts]

def compute_embeddings(model, pairs, batch_size: int, normalize: bool):
    # SentenceTransformer.encode has normalize_embeddings parameter
    return model.encode(
        pairs,
        batch_size=batch_size,
        convert_to_tensor=True,
        show_progress_bar=True,
        normalize_embeddings=normalize
    )

def cosine_sim_matrix(a, b):
    # a: (N,d) tensor, b: (M,d) tensor
    from sentence_transformers import util
    sims = util.cos_sim(a, b).cpu().numpy()
    return sims

# def save_cache(cache_path: str, meta: dict, emb_np: np.ndarray):
#     np.savez(cache_path, embeddings=emb_np, meta=json.dumps(meta, ensure_ascii=False))

# def load_cache(cache_path: str):
#     data = np.load(cache_path, allow_pickle=True)
#     emb = data["embeddings"]
#     meta = json.loads(str(data["meta"]))
#     return emb, meta

def save_cache(cache_path: str, meta: dict, emb_np: np.ndarray):
    np.savez(cache_path, embeddings=emb_np)      # solo arrays
    with open(cache_path + ".json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)   # meta en JSON sidecar

def load_cache(cache_path: str):
    emb = np.load(cache_path)["embeddings"]
    with open(cache_path + ".json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    return emb, meta

<<<<<<< HEAD
# import spacy
=======
import spacy
>>>>>>> 9ab216112fea523257810c2947af1aabc35b409c

def limpiar_texto(texto, nlp):
    """
    Limpia nombres propios, entidades y caracteres especiales del texto.
    Conserva la primera palabra de cada oración (aunque esté en mayúscula).
    """
    if not texto or not isinstance(texto, str):
        return ""

    # 1️⃣ Remover caracteres especiales innecesarios (antes del análisis)
    #    Mantiene letras, números, espacios y signos básicos de puntuación.
    texto = re.sub(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9\s.,;:!?()\-]", " ", texto)

    # 2️⃣ Procesamiento lingüístico
    doc = nlp(texto)
    resultado = []

    for sent in doc.sents:
        tokens = []
        for i, token in enumerate(sent):
            # eliminar puntuación y símbolos
            if token.is_punct or token.is_space or token.is_digit:
                continue
            # Mantiene primera palabra de cada oración
            if i == 0:
                tokens.append(token.text)
            # Elimina nombres propios o entidades nombradas
            elif token.pos_ == "PROPN" or token.ent_type_ in ["PER", "ORG", "LOC", "GPE"]:
                continue
            else:
                tokens.append(token.text)
        resultado.append(" ".join(tokens))

    # 3️⃣ Limpiar puntuación repetida y espacios múltiples
    texto_limpio = " ".join(resultado)
    texto_limpio = re.sub(r"\s{2,}", " ", texto_limpio).strip()

    # 4️⃣ Opcional: eliminar espacios antes de comas o puntos
    texto_limpio = re.sub(r"\s+([,.!?;:])", r"\1", texto_limpio)

    return texto_limpio


# ============================================================================
# Generador de cache para generar embeddings nuevas tablas
# ============================================================================

def genCache(cache_name:str, tbl_input_dir:str, out_dir:str, instruction:str, batch_size = 32, normalize = True, cache_path = None, force_recompute = False):
  
  model_name = "hkunlp/instructor-large" #help="HF model name for embeddings.")
  # instruction = "Representa el tema central del siguiente objetivo de desarrollo sostenible" #"Instruction for ODS texts.")
  ensure_out_dir(out_dir)

  # Load data
  input_df = pd.read_excel(tbl_input_dir)
  input_texts  = (input_df["ods"].fillna("") + ". " + input_df["descripcion"].fillna("")).tolist()

  # Compute fingerprint and cache path
  fingerprint = build_ods_fingerprint(model_name, instruction, input_texts)
  cache_path = cache_path or os.path.join(out_dir, f"{cache_name}_{fingerprint}.npz")

  # Lazy import model to allow quick --help
  from sentence_transformers import SentenceTransformer

  model = SentenceTransformer(model_name)
  input_pairs = make_text_pairs(instruction, input_texts)
  emb_input = compute_embeddings(model, input_pairs, batch_size=batch_size, normalize=normalize)
  emb_input_np = emb_input.cpu().numpy()
  save_cache(cache_path, {"model": model_name, "instr": instruction, "count": len(input_texts)}, emb_input_np)

# ============================================================================
# Función generadora tablas
# ============================================================================

import torch
import pandas as pd
import numpy as np


def search(query):
#   patr_tblinput = ' //Copy of Iniciativas priorizadas PATR 385.xlsx' #"CSV with PATR projects (columns: id, descripcion, ...).")
  ods_tblinput = Path('data/raw/v1_tabla_odsDescripcion.xlsx')
  meta_tblinput = Path('data/raw/v1_tabla_lvlMetaOds.xlsx')
  indicador_tblinput = Path('data/raw/marco_ods_ids.xlsx')
  genero_tblinput = Path('data/raw/genero.xlsx')
  poblacional_tblinput = Path('data/raw/poblacional.xlsx')
  etnico_tblinput = Path('data/raw/etnico.xlsx')
  pilares_tblinput = Path('data/raw/pilares.xlsx') #"CSV with ODS list (columns: ods_id, titulo, descripcion).")
  categorias_tblinput = Path('data/raw/categorias.xlsx')
  estrategias_tblinput = Path('data/raw/estrategias.xlsx')
  out_dir = Path('data/embeddings') #"Output directory.")
  model_name = "hkunlp/instructor-large" #help="HF model name for embeddings.")
  instr_proj = "Representa el propósito de desarrollo sostenible del siguiente proyecto territorial" #"Instruction for PATR projects.")
  instr_ods = "Representa el tema central del siguiente ODS" #"Instruction for ODS texts.")
  batch_size = 32 #"Batch size for encoding.")
  top_k = 5 #"Top-K ODS to retrieve.")
  normalize = True #"L2-normalize embeddings during encoding.") # Changed from "store_true" to boolean
  cache_path = None #"Path to cache npz for ODS embeddings (auto if not set).")
  force_recompute = False #"Ignore cache and recompute ODS embeddings.") # Changed from "store_true" to boolean


  ensure_out_dir(out_dir)

  #"OBJETIVO","OBJETIVO_META","INDICADORES","CODIGO_UNSD"

  # Load data
  # patr_df, ods_df = load_data(patr_tblinput, ods_tblinput)
  # patr_df = patr_df[['ID', 'INICIATIVAS']].drop_duplicates().reset_index(drop=True) # Reset index
  # patr_texts = patr_df["INICIATIVAS"].fillna("").tolist()
  # patr_df = pd.read_excel(patr_tblinput)
  ods_df = pd.read_excel(ods_tblinput)
  meta_df = pd.read_excel(meta_tblinput)  
  inidicador_df = pd.read_excel(indicador_tblinput)
  genero_df = pd.read_excel(genero_tblinput)
  poblacional_df = pd.read_excel(poblacional_tblinput)
  etnico_df = pd.read_excel(etnico_tblinput)
  pilares_df = pd.read_excel(pilares_tblinput)
  estrategias_df = pd.read_excel(estrategias_tblinput)
  categorias_df = pd.read_excel(categorias_tblinput)

#   nlp = spacy.load("es_core_news_md")
#   query = limpiar_texto(query, nlp)
  patr_texts = list([query])
  # print(len(patr_texts))
  ods_texts  = (ods_df["ods"].fillna("") + ". " + ods_df["descripcion"].fillna("")).tolist()
  meta_texts = (meta_df["OBJETIVO"].fillna("") + ". " + meta_df["META"].fillna("")).tolist()
  indicadores_texts  = (inidicador_df["OBJETIVO"].fillna("") + ". " + inidicador_df["INDICADORES"].fillna("")).tolist()
  genero_texts = (genero_df["DESCRIPCION"].fillna("")).tolist()
  poblacional_texts = (poblacional_df["DESCRIPCION"].fillna("")).tolist()
  etnico_texts = (etnico_df["DESCRIPCION"].fillna("")).tolist()
  # ods_texts  = (ods_df["OBJETIVO"].fillna("") + ". " + ods_df["INDICADORES"].fillna("")).tolist()
  pilares_texts  = (pilares_df["PILAR"].fillna("") + ". " + pilares_df["DESCRIPCION"].fillna("") + ". " + pilares_df["SUSTENTO"].fillna("")).tolist()
  estrategias_texts  = (estrategias_df["ESTRATEGIA"].fillna("") + ". " + estrategias_df["DESCRIPCION"].fillna("")).tolist()
  categorias_texts  = (categorias_df["CATEGORIA"].fillna("") + ". " + categorias_df["DESCRIPCION"].fillna("")).tolist()
  # print(len(ods_texts))

  texts = [ods_texts, meta_texts, indicadores_texts, genero_texts, poblacional_texts, etnico_texts, pilares_texts, estrategias_texts, categorias_texts]

  # print('texts')
  # print([len(x) for x in texts])

  instruc_bases = [
                  "Representa la definición global de los Objetivo de Desarrollo Sostenible (ODS) para su uso como categoría de referencia en la clasificación de iniciativas ciudadanas.",
                  "Representa la definición global de las metas de los Objetivos de Desarrollo Sostenible (ODS) para su uso como categoría de referencia en la clasificación de iniciativas ciudadanas", 
                  "Representa el tema central del siguiente ODS", 
                  "Representa el tema central del siguiente de enfoque", 
                  "Representa el tema central del siguiente de enfoque poblacional",
                  "Representa el tema central del siguiente de enfoque etnico",
                  "Representa el tema de los siguiente ejes temáticos y estratégicos", 
                  "Representa el tema de las siguiente estrategias",
                  "Representa el tema de las siguientes categorias"
                  ]

  instruc_iniciativas = [
                        "Representa la iniciativa de planificación territorial y construcción de paz en Colombia para clasificarla según su alineación semántica con los Objetivos de Desarrollo Sostenible (ODS)", 
                        "Representa la iniciativa de planificación territorial y construcción de paz en Colombia para clasificarla según su alineación semántica con las metas globales de los Objetivos de Desarrollo Sostenible (ODS)",
                        "Representa la iniciativa de planificación territorial y construcción de paz en Colombia para clasificarla según su alineación semántica con los indicadores globales de los Objetivos de Desarrollo Sostenible (ODS)",
                        "Representa la iniciativa de proyecto de construcción de paz para clasificar si aplica el Enfoque de Género, detectando acciones afirmativas dirigidas a mujeres rurales, madres cabeza de familia, liderazgo femenino o cierre de brechas de desigualdad entre hombres y mujeres.grupos poblacionales según sexo, identidad de género, orientación sexual o roles de género.mujeres, equidad de género, igualdad de oportunidades, discriminación, violencia basada en género", 
                        "Representa la iniciativa de proyecto de construcción de paz para clasificar si aplica el enfoque poblacional, reconoce explícitamente la diversidad poblacional y plantea acciones diferenciadas según edad, condición o situación social. juventudes, niñez, adultos mayores, personas con discapacidad, víctimas del conflicto, migrantes, refugiados",
                        "Representa la iniciativa de proyecto de construcción de paz para clasificar si aplica el enfoque etnico, reconoce diversidad étnica y cultural,  plantea acciones diferenciadas para estos grupos. Indígenas, negros, afrodescendientes, raizales, palenqueros, rom, resguardos, palenques, consejos comunitarios", 
                        "Representa el siguiente proyecto territorial en terminos de ejes temáticos y estratégicos", 
                        "Representa el siguiente proyecto territorial en terminos de la estrategia", 
                        "Representa el siguiente proyecto territorial en terminos de la categoria"
                        ]



  # Compute fingerprint and cache path
  # fingerprint = build_ods_fingerprint(model_name, instr_ods, ods_texts)
  # fingerprint = [build_ods_fingerprint(model_name, instr, texts[idx]) for idx, instr in enumerate(instruc_bases)]
  fingerprint = ['e109a32969828923f9ddf6f4ad59328d','e0d3b674182b1e8ab9280544bd9e8532','07948e6beafe34049ca8a7309363eee2','9a4c52cf18e95c52566c0b657a25c44f','5a8b0dd04b865e8f1c356a64795b3b67',
                  'c0973f650cac27181b3751aa9666819b','0a475def7da8551abdd502e1d042dc00','42e4e8bfb28dc47602e662a27d8b4e76','e0338741fd4e7b08ab7f92a32e08919b']


  ods_cache_path = cache_path or os.path.join(out_dir, f"v1_tabla_odsDescripcion_{fingerprint[0]}.npz")
  meta_cache_path = cache_path or os.path.join(out_dir, f"v1_tabla_lvlMetaOds_{fingerprint[1]}.npz")
  indicadores_cache_path = cache_path or os.path.join(out_dir, f"ods_embeddings_{fingerprint[2]}.npz")
  genero_cache_path = cache_path or os.path.join(out_dir, f"tabla_genero_{fingerprint[3]}.npz")
  poblacional_cache_path = cache_path or os.path.join(out_dir, f"tabla_poblacional_{fingerprint[4]}.npz")
  etnico_cache_path = cache_path or os.path.join(out_dir, f"tabla_etnico_{fingerprint[5]}.npz")  
  pilaresPdet_cache_path = cache_path or os.path.join(out_dir, f"pilaresPdet_embeddings_{fingerprint[6]}.npz")
  estrategiasPdet_cache_path = cache_path or os.path.join(out_dir, f"estrategiasPdet_embeddings_{fingerprint[7]}.npz")
  categoriasPdet_cache_path = cache_path or os.path.join(out_dir, f"categoriasPdet_embeddings_{fingerprint[8]}.npz")

  cache_paths = [ods_cache_path, meta_cache_path, indicadores_cache_path, genero_cache_path, poblacional_cache_path, etnico_cache_path, pilaresPdet_cache_path, estrategiasPdet_cache_path, categoriasPdet_cache_path]

  print('cache_paths')
  print([x for x in cache_paths])

  # Lazy import model to allow quick --help
  from sentence_transformers import SentenceTransformer

  # Load / compute ODS embeddings with cache
  ods_use_cache = (not force_recompute) and os.path.exists(ods_cache_path)
  meta_use_cache = (not force_recompute) and os.path.exists(meta_cache_path)
  indicadores_use_cache = (not force_recompute) and os.path.exists(indicadores_cache_path)
  genero_use_cache = (not force_recompute) and os.path.exists(genero_cache_path)
  poblacional_use_cache = (not force_recompute) and os.path.exists(poblacional_cache_path)
  etnico_use_cache = (not force_recompute) and os.path.exists(etnico_cache_path)  
  pilaresPdet_use_cache = (not force_recompute) and os.path.exists(pilaresPdet_cache_path)
  estrategiasPdet_use_cache = (not force_recompute) and os.path.exists(estrategiasPdet_cache_path)
  categoriasPdet_use_cache = (not force_recompute) and os.path.exists(categoriasPdet_cache_path)

  matrix_unfpa = []
  caches = [ods_use_cache, meta_use_cache, indicadores_use_cache, genero_use_cache, poblacional_use_cache, etnico_use_cache,
            pilaresPdet_use_cache, estrategiasPdet_use_cache, categoriasPdet_use_cache]

  for idx, i_cache in enumerate(caches):
    # print(cache_paths[idx])

    if i_cache:
        emb_unfpa_np, meta = load_cache(cache_paths[idx])
        # Minimal safety check: same model/instruction length
        if meta.get("model_name") != model_name or meta.get("instr") != instruc_bases[idx] or meta.get("count") != len(texts[idx]):
          print(f'Diferencias en carga de metadata nlp cache {cache_paths[idx]}:')
          print(meta.get("model_name"), model_name)
          print(meta.get("instr"), instruc_bases[idx])
          print(meta.get("count"),len(texts[idx]))
            # i_cache = False

    if not i_cache:
      print(f'no se encontro cache de id : {idx}')
        # model = SentenceTransformer(model_name)
        # ods_pairs = make_text_pairs(instruc_bases[idx], texts[idx])
        # emb_ods = compute_embeddings(model, ods_pairs, batch_size=batch_size, normalize=normalize)
        # emb_unfpa_np = emb_ods.cpu().numpy()
        # save_cache(cache_paths[idx], {"model_name": model_name, "instr": instruc_bases[idx], "count": len(texts[idx])}, emb_unfpa_np)
    else:
        model = SentenceTransformer(model_name)  # still needed for project embeddings

    # Compute PATR embeddings
    patr_pairs = make_text_pairs(instruc_iniciativas[idx], patr_texts)
    emb_patr = compute_embeddings(model, patr_pairs, batch_size=batch_size, normalize=normalize)

    # Convert ODS (np.ndarray) to torch.Tensor and move it to the same device as emb_patr
    emb_unfpa_t = torch.from_numpy(emb_unfpa_np).to(emb_patr.device)

    # Similarity
    from sentence_transformers import util
    sim_matrix_ = util.cos_sim(emb_patr, emb_unfpa_t).cpu().numpy()

    matrix_unfpa.append(sim_matrix_)

  print([len(x) for x in matrix_unfpa])

  # tops_k = [5,1,1,1] # ods_use_cache, pilaresPdet_use_cache, estrategiasPdet_use_cache, categoriasPdet_use_cache
  tops_k = [len(ods_texts),len(meta_texts),len(indicadores_texts),1,1,1,1,1,1]
  res_dfs = []

  for idx, top in enumerate(tops_k):
    sim_matrix = matrix_unfpa[idx]
    # Top-K per project
    # K = min(top_k, sim_matrix.shape[1])
    K = min(top, sim_matrix.shape[1])
    top_rows = []
    for i in range(sim_matrix.shape[0]):
        sims = sim_matrix[i]
        # rt descending and take first K
        top_idx = np.argsort(-sims)[:K]
        # ods_df
        # meta_df
        # inidicador_df
        # genero_df
        # poblacional_df
        # etnico_df
        # pilares_df
        # estrategias_df
        # categorias_df

        #### RESULTADOS PARA DESCRIPCION ODS
        if idx == 0:
          for rank, j in enumerate(top_idx, start=1):
              row = {
                  # "project_id": patr_df.iloc[i, patr_df.columns.get_loc("ID")], # Use iloc with positional index
                  # "project_text": patr_df.iloc[i, patr_df.columns.get_loc("INICIATIVAS")], # Use iloc with positional index
                  "ODS_ID": ods_df.iloc[j, ods_df.columns.get_loc("id_ods")], # Use iloc with positional index
                  "OBJETIVO": ods_df.iloc[j, ods_df.columns.get_loc("ods")], # Use iloc with positional index

                  # "ods_texto": ods_texts[j],
                  "ods_rank": rank,
                  "ods_similaridad_cos": float(sims[j]),
                  # "ods_titulo": ods_df.iloc[j, ods_df.columns.get_loc("INDICADORES")], # Use iloc with positional index
                  # "ods_texto": ods_texts[j]
              }
              top_rows.append(row)

        #### RESULTADOS PARA METAS ODS
        if idx == 1:
          for rank, j in enumerate(top_idx, start=1):
              row = {
                  # "project_id": patr_df.iloc[i, patr_df.columns.get_loc("ID")], # Use iloc with positional index
                  # "project_text": patr_df.iloc[i, patr_df.columns.get_loc("INICIATIVAS")], # Use iloc with positional index
                  "META_ID": meta_df.iloc[j, meta_df.columns.get_loc("ID_META")], # Use iloc with positional index
                  "META": meta_df.iloc[j, meta_df.columns.get_loc("META")], # Use iloc with positional index
                  "ODS_ID": meta_df.iloc[j, meta_df.columns.get_loc("ID_OBJETIVO")],

                  # "ods_texto": ods_texts[j],
                  "meta_rank": rank,
                  "meta_similaridad_cos": float(sims[j]),
                  # "ods_titulo": ods_df.iloc[j, ods_df.columns.get_loc("INDICADORES")], # Use iloc with positional index
                  # "ods_texto": ods_texts[j]
              }
              top_rows.append(row)

        #### RESULTADOS PARA INDICADORES ODS
        if idx == 2:
          for rank, j in enumerate(top_idx, start=1):
              row = {
                  # "project_id": patr_df.iloc[i, patr_df.columns.get_loc("ID")], # Use iloc with positional index
                  # "project_text": patr_df.iloc[i, patr_df.columns.get_loc("INICIATIVAS")], # Use iloc with positional index
                  "INDICADOR_ID": inidicador_df.iloc[j, inidicador_df.columns.get_loc("ID_INDICADORES")], # Use iloc with positional index
                  "INDICADOR": inidicador_df.iloc[j, inidicador_df.columns.get_loc("INDICADORES")], # Use iloc with positional index
                  "ODS_ID": inidicador_df.iloc[j, inidicador_df.columns.get_loc("ID_ODS")],
                  "META_ID": inidicador_df.iloc[j, inidicador_df.columns.get_loc("ID_META")],

                  # "ods_texto": ods_texts[j],
                  "indicador_rank": rank,
                  "indicador_similaridad_cos": float(sims[j]),
                  # "ods_titulo": ods_df.iloc[j, ods_df.columns.get_loc("INDICADORES")], # Use iloc with positional index
                  # "ods_texto": ods_texts[j]
              }
              top_rows.append(row)

        #### RESULTADOS PARA ENFOQUE GENERO
        if idx == 3:
          for rank, j in enumerate(top_idx, start=1):
              row = {
                  # "project_id": patr_df.iloc[i, patr_df.columns.get_loc("ID")], # Use iloc with positional index
                  # "project_text": patr_df.iloc[i, patr_df.columns.get_loc("INICIATIVAS")], # Use iloc with positional index
                  "ENFOQUE_GENERO": genero_df.iloc[j, genero_df.columns.get_loc("CATEGORIA")], # Use iloc with positional index
                  # "INDICADOR": genero_df.iloc[j, genero_df.columns.get_loc("INDICADORES")], # Use iloc with positional index

                  # "ods_texto": ods_texts[j],
                  "rank": rank,
                  "similaridad_cos": float(sims[j]),
                  # "ods_titulo": ods_df.iloc[j, ods_df.columns.get_loc("INDICADORES")], # Use iloc with positional index
                  # "ods_texto": ods_texts[j]
              }
              top_rows.append(row)

        #### RESULTADOS PARA ENFOQUE POBLACIONAL
        if idx == 4:
          for rank, j in enumerate(top_idx, start=1):
              row = {
                  # "project_id": patr_df.iloc[i, patr_df.columns.get_loc("ID")], # Use iloc with positional index
                  # "project_text": patr_df.iloc[i, patr_df.columns.get_loc("INICIATIVAS")], # Use iloc with positional index
                  "ENFOQUE_POBLACIONAL": poblacional_df.iloc[j, poblacional_df.columns.get_loc("CATEGORIA")], # Use iloc with positional index
                  # "INDICADOR": poblacional_df.iloc[j, poblacional_df.columns.get_loc("INDICADORES")], # Use iloc with positional index

                  # "ods_texto": ods_texts[j],
                  "rank": rank,
                  "similaridad_cos": float(sims[j]),
                  # "ods_titulo": ods_df.iloc[j, ods_df.columns.get_loc("INDICADORES")], # Use iloc with positional index
                  # "ods_texto": ods_texts[j]
              }
              top_rows.append(row)

        #### RESULTADOS PARA ENFOQUE ETNICO
        if idx == 5:
          for rank, j in enumerate(top_idx, start=1):
              row = {
                  # "project_id": patr_df.iloc[i, patr_df.columns.get_loc("ID")], # Use iloc with positional index
                  # "project_text": patr_df.iloc[i, patr_df.columns.get_loc("INICIATIVAS")], # Use iloc with positional index
                  "ENFOQUE_POBLACIONAL": etnico_df.iloc[j, etnico_df.columns.get_loc("CATEGORIA")], # Use iloc with positional index
                  # "INDICADOR": etnico_df.iloc[j, etnico_df.columns.get_loc("INDICADORES")], # Use iloc with positional index

                  # "ods_texto": ods_texts[j],
                  "rank": rank,
                  "similaridad_cos": float(sims[j]),
                  # "ods_titulo": ods_df.iloc[j, ods_df.columns.get_loc("INDICADORES")], # Use iloc with positional index
                  # "ods_texto": ods_texts[j]
              }
              top_rows.append(row)

        #### RESULTADOS PARA PILARES
        if idx == 6:
          for rank, j in enumerate(top_idx, start=1):
              row = {
                  "rank": rank,
                  "similaridad_cos": float(sims[j]),
                  "pilar_texto": pilares_texts[j]
              }
              top_rows.append(row)

        #### RESULTADOS PARA ESTRATEGIAS
        if idx == 7:
          for rank, j in enumerate(top_idx, start=1):
              row = {
                  "rank": rank,
                  "similaridad_cos": float(sims[j]),
                  "estrategia_texto": estrategias_texts[j]
              }
              top_rows.append(row)

        #### RESULTADOS PARA CATEGORIAS
        if idx == 8:
          for rank, j in enumerate(top_idx, start=1):
              row = {
                  "rank": rank,
                  "similaridad_cos": float(sims[j]),
                  "categoria_texto": categorias_texts[j]
              }
              top_rows.append(row)


    res_df = pd.DataFrame(top_rows).drop_duplicates()
    res_dfs.append(res_df)

  # Additionally, export a simple edges file (Top-1) for graph visualizations
  # edges = []
  # df_edges = pd.DataFrame()
  # df_edges['source'] = res_dfs[0]['ods_id']
  # df_edges['target'] = res_dfs[0]['indicador_id']
  # df_edges['weight'] = res_dfs[0]['similaridad_cos']

  # for pid, group in res_df.groupby("project_id"):
  #     best = group.sort_values("rank").iloc[0]
  #     edges.append({"source": group["project_id"], "target": group["ods_id"], "weight": group["similaridad_cos"]})
  # df_edges = pd.DataFrame(edges)#.to_tblinput(out_edges, index=False, encoding="utf-8

  # html = build_graph(df_edges)
  from sklearn.preprocessing import MinMaxScaler


  # dfs_norm = []
  # Initialize the MinMaxScaler
  scaler = MinMaxScaler()

  for i in range(0,3):    

    if i == 0:
      # Reshape the 'similaridad_cos' column as it needs to be 2D for the scaler
      similarity_scores = res_dfs[i]['ods_similaridad_cos'].values.reshape(-1, 1)
      # Fit and transform the data
      res_dfs[i]['ods_similaridad_cos_normalized'] = scaler.fit_transform(similarity_scores)
      # df_sim = res_dfs[i][['ODS_ID',	'OBJETIVO',	'rank',	'similaridad_cos']]
      # df_simnorm = res_dfs[i][['ODS_ID',	'OBJETIVO',	'ods_rank', 'ods_similaridad_cos_normalized']]
      # df_simnorm.columns = ['ODS_ID',	'OBJETIVO',	'rank',	'similaridad_cos']
      # dfs_norm.append(df_simnorm)
    if i == 1:
      # Reshape the 'similaridad_cos' column as it needs to be 2D for the scaler
      similarity_scores = res_dfs[i]['meta_similaridad_cos'].values.reshape(-1, 1)
      # Fit and transform the data
      res_dfs[i]['meta_similaridad_cos_normalized'] = scaler.fit_transform(similarity_scores)
      # df_sim = res_dfs[i][['META_ID',	'META',	'rank',	'similaridad_cos']]
      # df_simnorm = res_dfs[i][['META_ID',	'META',	'rank', 'similaridad_cos_normalized']]
      # df_simnorm.columns = ['META_ID',	'META',	'rank',	'similaridad_cos']
      # dfs_norm.append(df_simnorm)
    if i == 2:
      # Reshape the 'similaridad_cos' column as it needs to be 2D for the scaler
      similarity_scores = res_dfs[i]['indicador_similaridad_cos'].values.reshape(-1, 1)
      # Fit and transform the data
      res_dfs[i]['indicador_similaridad_cos_normalized'] = scaler.fit_transform(similarity_scores)
      # # df_sim = res_dfs[i][['INDICADOR_ID',	'INDICADOR',	'rank',	'similaridad_cos']]
      # df_simnorm = res_dfs[i][['INDICADOR_ID',	'INDICADOR',	'rank', 'similaridad_cos_normalized']]
      # df_simnorm.columns = ['INDICADOR_ID',	'INDICADOR',	'rank',	'similaridad_cos']
      # dfs_norm.append(df_simnorm)
    
    bdl_ods = res_dfs[0].merge(res_dfs[1], 'inner', left_on='ODS_ID', right_on='ODS_ID')
    bdl_ods = bdl_ods.merge(res_dfs[2],'inner', left_on=['ODS_ID','META_ID'], right_on=['ODS_ID','META_ID'])
    print(f'Tamaño BDL: {len(bdl_ods)}')

    

  return (query, res_dfs[0], res_dfs[1], res_dfs[2], res_dfs[3], res_dfs[4], res_dfs[5], res_dfs[6], res_dfs[7], res_dfs[8], bdl_ods)



# ============================================================================
# Función para normalizar
# ============================================================================



