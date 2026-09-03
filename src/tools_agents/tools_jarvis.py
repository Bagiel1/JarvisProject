import os
from anthropic import beta_tool

path_obsidian= "/home/bagiel/Gabriel/obsidian/ia_obsidian"

@beta_tool
def read_note(name_file: str) -> str:
    """Read and return an existing Obsidian note.

    Args:
        name_file: Exact filename including .md.
    """
    print(f"[LOG DO JARVIS] 📖 Lendo o arquivo: {name_file}")
    
    path_note= os.path.join(path_obsidian, name_file)
    with open(path_note, "r", encoding='utf-8') as f:
        note= f.read()
    return note

@beta_tool
def list_notes() -> list:
    """Return the filenames of all Obsidian notes."""

    print("[LOG DO JARVIS] 📂 Listando todos os arquivos do Obsidian...")
    
    notes= os.listdir(path_obsidian)
    notes= " - ".join(notes)
    return notes

@beta_tool
def create_note(name_file: str, written: str) -> str:
    """
    Create a NEW Obsidian note.

    Use this only when a new note is actually needed.
    Do NOT use it to modify an existing note; use update_note instead.
    Write Markdown and only create [[links]] to notes confirmed by previous tool results.

    Args:
        name_file: New filename including .md.
        written: Full Markdown content.
    """
    print(f"[LOG DO JARVIS] ✍️ Criando/Atualizando a nota: {name_file}")
    
    path_file= os.path.join(path_obsidian, name_file)
    with open(path_file, "w", encoding='utf-8') as f:
        f.write(written)

    from rag_engine import adicionar_ou_atualizar_nota

    adicionar_ou_atualizar_nota(path_file)
    
    return "Nota Criada"

@beta_tool
def search_notes(keyword: str) -> list:
    """
    Semantically search Obsidian notes by concept or meaning.
    Use short relevant words or phrases, not necessarily exact text.

    Args:
        keyword: Semantic search query.
    """
    print(f"[LOG DO JARVIS] 🔍 Buscando pela palavra-chave: '{keyword}'")
    
    from rag_engine import busca_contexto

    texto_lista, list_of_search= busca_contexto(keyword)
    list_of_search = " - ".join(list_of_search)
    
    return list_of_search


@beta_tool # Use o mesmo decorador que você já usa nas ferramentas do Obsidian
def transfer_to_coder(tarefa: str) -> str:
    """
    Transfer a programming task to the Coder.

    Use for writing, debugging, analyzing or executing code.
    Do NOT use for creating or editing Obsidian notes, even if the note is about code.

    After calling, respond with "[HANDOFF_CODER]" followed by the task.

    Args:
        tarefa: Programming task to transfer.
    """
    print("\n🔄 [JARVIS] Identificou código. Acionando o Coder por debaixo dos panos...")
    return "Tool executed successfully. Now reply to the user with the [HANDOFF_CODER] tag."

@beta_tool
def delete_note(name_file: str):
    """Delete a note if, and ONLY if, the user especify the name and asks to delete it.
        
        Args:
            name_file: The name of the file. It must be the file asked and MUST include the .md extension.
        """
    try:
        full_path= os.path.join(path_obsidian, name_file)
        os.remove(full_path)

        from rag_engine import remove_note

        remove_note(name_file)

    except FileNotFoundError as e:
        print(f"System error message: {e}\n")
        return f"Nota {name_file} nao existe, use as tools para saber o nome exato da nota."

    return f"Nota {name_file} foi deletada com sucesso."

@beta_tool
def update_note(
    name_file: str,
    operation: str,
    new_text: str,
    old_text: str = "",
    anchor: str = ""
) -> str:
    """
    Make a minimal edit to an EXISTING Obsidian note.
    Always read the target note before calling this tool.
    Prefer this tool over create_note when modifying existing content.

    Operations:
    - "replace": update information that already exists.
    old_text MUST be copied exactly from read_note.
    - "append": add genuinely new information at the end.
    - "insert_after": add information under/after an existing section or passage.
    anchor MUST be copied exactly from read_note.

    Never invent old_text or anchor.

    Args:
        name_file: Exact existing filename including .md.
        operation: "replace", "append", or "insert_after".
        new_text: New Markdown content.
        old_text: Exact existing text to replace. Required for "replace".
        anchor: Exact existing text after which to insert. Required for "insert_after".
    """

    full_path = os.path.join(path_obsidian, name_file)

    if not os.path.exists(full_path):
        return f"Erro: a nota '{name_file}' não existe. Nenhuma alteração foi feita."

    operations_validas = ["append", "replace", "insert_after"]

    if operation not in operations_validas:
        return (
            f"Erro: operação '{operation}' inválida. "
            "Use apenas: append, replace ou insert_after."
        )

    try:

        # ---------------- APPEND ----------------
        if operation == "append":

            if not new_text.strip():
                return "Erro: new_text está vazio. Nenhuma alteração foi feita."

            with open(full_path, "r", encoding="utf-8") as f:
                conteudo = f.read()

            with open(full_path, "a", encoding="utf-8") as f:

                if conteudo and not conteudo.endswith("\n"):
                    f.write("\n")

                f.write(new_text)

                if not new_text.endswith("\n"):
                    f.write("\n")


        # ---------------- REPLACE ----------------
        elif operation == "replace":

            if not old_text:
                return (
                    "Erro: old_text é obrigatório para a operação replace. "
                    "Nenhuma alteração foi feita."
                )

            with open(full_path, "r", encoding="utf-8") as f:
                conteudo = f.read()

            if old_text not in conteudo:
                return (
                    "Erro: old_text não foi encontrado exatamente na nota. "
                    "Leia a nota novamente e use um trecho exato."
                )
            conteudo_novo = conteudo.replace(old_text,new_text,1)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(conteudo_novo)


        # ---------------- INSERT AFTER ----------------
        elif operation == "insert_after":

            if not anchor:
                return (
                    "Erro: anchor é obrigatório para insert_after. "
                    "Nenhuma alteração foi feita."
                )

            with open(full_path, "r", encoding="utf-8") as f:
                conteudo = f.read()

            if anchor not in conteudo:
                return (
                    "Erro: anchor não foi encontrado exatamente na nota. "
                    "Leia a nota novamente e use um trecho exato."
                )

            texto_inserido = anchor + "\n" + new_text

            conteudo_novo = conteudo.replace(anchor,texto_inserido,1)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(conteudo_novo)


    except OSError as e:
        return f"Erro ao atualizar a nota: {e}"

    from rag_engine import adicionar_ou_atualizar_nota
    adicionar_ou_atualizar_nota(full_path)

    return f"Nota '{name_file}' atualizada com sucesso usando '{operation}'."

