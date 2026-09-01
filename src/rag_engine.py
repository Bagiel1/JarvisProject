import chromadb
import os

def inicialization():
    chroma_client= chromadb.PersistentClient(path="./bunker_db")
    collection= chroma_client.get_or_create_collection(name="my_obsidian")

    path_obsidian= "/home/bagiel/Gabriel/obsidian/ia_obsidian"

    documentos= []
    metadados= []
    ids= []

    for nome_arquivo in os.listdir(path_obsidian):
        if nome_arquivo.endswith(".md"):
            full_path= os.path.join(path_obsidian, nome_arquivo)

            with open(full_path, 'r', encoding='utf-8') as f:
                conteudo= f.read()
                documentos.append(conteudo)
                metadados.append({"nome_nota": nome_arquivo})
                ids.append(nome_arquivo)

    if documentos:
        collection.add(
            documents=documentos,
            metadatas=metadados,
            ids=ids
        )
    print(f"✅ {len(documentos)} notas vetorizadas e salvas no banco!")

def busca_contexto(pergunta: str, n_resultados: int= 2):
    chroma_client= chromadb.PersistentClient(path="./bunker_db")
    collection= chroma_client.get_collection(name="my_obsidian")

    resultados= collection.query(
        query_texts=[pergunta],
        n_results= n_resultados
    )
    docs_validos= []
    nomes_validos= []

    for doc, distancia, meta in zip(resultados['documents'][0], resultados['distances'][0],
                                    resultados['metadatas'][0]):
        if distancia < 5:
            docs_validos.append(doc)
            nomes_validos.append(meta['nome_nota'])
            print(distancia)
    
    return docs_validos, nomes_validos

def adicionar_ou_atualizar_nota(full_path: str):
    chroma_client= chromadb.PersistentClient(path="./bunker_db")
    collection= chroma_client.get_collection(name="my_obsidian")

    nome_arquivo= os.path.basename(full_path)

    with open(full_path, 'r', encoding='utf-8') as f:
        conteudo= f.read()

        collection.upsert(
            documents=[conteudo],
            metadatas=[{"nome_nota": nome_arquivo}],
            ids=[nome_arquivo]
        )

    print(f"✅ Nota '{nome_arquivo}' injetada no banco vetorial!")


if __name__ == "__main__":
    inicialization()