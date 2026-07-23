import os
from anthropic import beta_tool

path_obsidian= "/home/bagiel/Gabriel/obsidian/ia_obsidian"

@beta_tool
def read_note(name_file: str) -> str:
    """Show the content of a note

    Args:
        name_file: The exact name of the file to read, including the .md extension
    """
    print(f"[LOG DO JARVIS] 📖 Lendo o arquivo: {name_file}")
    
    path_note= os.path.join(path_obsidian, name_file)
    with open(path_note, "r") as f:
        note= f.read()
    return note

@beta_tool
def list_notes() -> list:
    """Show all the names of the notes in the Obsidian graph written

    """
    print("[LOG DO JARVIS] 📂 Listando todos os arquivos do Obsidian...")
    
    notes= os.listdir(path_obsidian)
    notes= " - ".join(notes)
    return notes

@beta_tool
def create_note(name_file: str, written: str) -> str:
    """Create a new note and add it as a node in the Obsidian graph.

    CRITICAL INSTRUCTION BEFORE CALLING: If you do not currently have the exact list of existing notes in your context memory, you MUST call list_notes() first.

    Args:
        name_file: The name of the file. It must reflect the main topic of the note and MUST include the .md extension and no accents (e.g., 'machine_learning.md').
        written: The content of the note. IMPORTANT: As you write the content, if you mention a concept or entity that exactly matches one of the existing notes in the Obsidian vault, you MUST connect them by wrapping the existing note's name in double brackets (e.g., [[existing_note_name]]). NEVER invent, hallucinate, or guess note names. ONLY create links to notes that were explicitly returned by list_notes().
    """
    print(f"[LOG DO JARVIS] ✍️ Criando/Atualizando a nota: {name_file}")
    
    path_file= os.path.join(path_obsidian, name_file)
    with open(path_file, "w") as f:
        f.write(written)
    
    return "Nota Criada"

@beta_tool
def search_notes(keyword: str) -> list:
    """Search for a specific keyword inside all markdown notes in the Obsidian vault.

    Use this tool when you need to find which notes mention a specific concept, entity, or word before trying to read them or create links.

    Args:
        keyword: The specific word, phrase, or concept to search for across the notes.
    """
    print(f"[LOG DO JARVIS] 🔍 Buscando pela palavra-chave: '{keyword}'")
    
    lista_of_notes= os.listdir(path_obsidian)
    list_of_search= []

    for name_file in lista_of_notes:
        path_file= os.path.join(path_obsidian, name_file)
        if path_file.endswith(".md"):
            with open(path_file, "r") as f:
                if keyword in f.read():
                    list_of_search.append(name_file)

    list_of_search= " - ".join(list_of_search)
    
    return list_of_search