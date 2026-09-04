import chromadb
import re
import os
import shutil
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from config import CHROMA_PATH, OBSIDIAN_PATH

path_chroma= CHROMA_PATH
path_obsidian= OBSIDIAN_PATH

EMBEDDING_FUNCTION= SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")

def chunk_note(nome_arquivo: str):
    documentos= []
    metadados= []
    ids= []
    
    chunk_size= 70
    overlap= 20
    
    full_path= path_obsidian / nome_arquivo

    with open(full_path, 'r', encoding='utf-8') as f:
        conteudo= f.read()
        palavras= list(re.finditer(r"\S+", conteudo))

        if not palavras:
            return [], [], []

        for index, inicio in enumerate(range(0, len(palavras), chunk_size-overlap)):
            fim= min(inicio + chunk_size, len(palavras))
            inicio_char= palavras[inicio].start()
            fim_char= palavras[fim-1].end()
            
            chunk_text= conteudo[inicio_char:fim_char].strip()
        
            documentos.append(chunk_text)
            metadados.append({"nome_nota": nome_arquivo, "chunk": index})
            ids.append(f"{nome_arquivo}::{index}")

    return documentos, metadados, ids

def inicialization():
    chroma_client= chromadb.PersistentClient(path=str(path_chroma))
    collection= chroma_client.get_or_create_collection(name="my_obsidian",
                                                       embedding_function=EMBEDDING_FUNCTION)

    documentos = []
    metadados = []
    ids = []

    for nome_arquivo in os.listdir(path_obsidian):
        if nome_arquivo.endswith(".md"):
            docs_notes, meta_notes, ids_notes= chunk_note(nome_arquivo)

            documentos.extend(docs_notes)
            metadados.extend(meta_notes)
            ids.extend(ids_notes)

    if documentos:
        collection.add(
            documents=documentos,
            metadatas=metadados,
            ids=ids
        )
    print(f"✅ {len(documentos)} chunks vetorizadas e salvos no banco!")

def busca_contexto(pergunta: str, n_notas: int= 2, trechos_por_nota: int= 2, threshold: float= 0.7):
    chroma_client= chromadb.PersistentClient(path=str(path_chroma))
    collection= chroma_client.get_collection(name="my_obsidian",
                                             embedding_function=EMBEDDING_FUNCTION)

    notas_selecionadas= []

    for _ in range(n_notas):
        if notas_selecionadas:
            resultados= collection.query(
                query_texts=[pergunta],
                n_results=1,
                where={
                    "nome_nota": {
                        "$nin": notas_selecionadas
                    }
                }
            )
        else:
            resultados= collection.query(
                query_texts=[pergunta],
                n_results=1
            )

        if not resultados["documents"][0]:
            break

        distancia= resultados["distances"][0][0]
        meta= resultados["metadatas"][0][0]

        if distancia >= threshold:
            break

        notas_selecionadas.append(meta["nome_nota"])

    resposta= []

    for nome_nota in notas_selecionadas:
        resultados= collection.query(
            query_texts=[pergunta],
            n_results=trechos_por_nota,
            where={"nome_nota": nome_nota}
        )

        trechos= []

        for doc, distancia in zip(resultados["documents"][0], resultados["distances"][0]):
            if distancia < threshold:
                trechos.append(doc)
        
        resposta.append({
            "nome_nota": nome_nota,
            "trechos": trechos
        })
    
    return resposta

def adicionar_ou_atualizar_nota(full_path: str):
    chroma_client= chromadb.PersistentClient(path=str(path_chroma))
    collection= chroma_client.get_collection(name="my_obsidian",
                                             embedding_function=EMBEDDING_FUNCTION)

    nome_arquivo= os.path.basename(full_path)
    collection.delete(where={"nome_nota": nome_arquivo})

    documentos, metadados, ids= chunk_note(nome_arquivo)

    if documentos:
        collection.upsert(
            documents=documentos,
            metadatas=metadados,
            ids=ids
        )

    print(f"✅ Nota '{nome_arquivo}' injetada no banco vetorial!")

def remove_note(name_file: str):
    chroma_client= chromadb.PersistentClient(path=str(path_chroma))
    collection= chroma_client.get_collection(name="my_obsidian",
                                             embedding_function=EMBEDDING_FUNCTION)

    collection.delete(where={"nome_nota": name_file})

def reset_bunker():
    if CHROMA_PATH.exists():
        shutil.rmtree(CHROMA_PATH)
        print("🗑️ Bunker apagado.")
    else:
        print("Bunker não existe.")

def rebuild_bunker():
    reset_bunker()
    inicialization()

if __name__ == "__main__":
    rebuild_bunker()