import os
from anthropic import beta_tool

path_codes= "/home/bagiel/Gabriel/obsidian"

@beta_tool 
def transfer_to_jarvis(motivo: str) -> str:
    """
    TRANSFER control back to the Jarvis (Orchestrator) agent. Use this tool IMMEDIATELY when you have successfully finished the requested programming task, or if the user asks about personal notes, Obsidian, training, or non-programming topics.
    
    CRITICAL RULE: After using this tool, your text response to the user MUST start exactly with:
    [HANDOFF_JARVIS] followed by the 'motivo'. Do not add any other text or greetings.
    
    Args:
        motivo: A clear and detailed summary explaining exactly what you coded, the current state of the project, and why you are transferring control back. This gives Jarvis the full context of what was done so he can update the user.
    """
    print("\n🔄 [CODER] Tarefa concluída ou assunto fora de escopo. Transferindo o controle de volta para o Jarvis...")
    return "Tool executed successfully. Now reply to the user with the [HANDOFF_JARVIS] tag."


@beta_tool
def create_code(file_path: str, code: str) -> str:
    """
    Create a new file and write the provided code or text into it. Overwrites the file if it already exists.
    
    Args:
        file_path: The name or relative/absolute path of the file to be created (e.g., 'main.py', 'src/utils.c', 'script.sh').
        code: The complete, raw code or text content to be written into the file. Do NOT truncate or omit parts of the code and dont use comments.
    """
    print(f"\n[LOG DO CODER] ✍️ Criando/Atualizando o arquivo: {file_path}")
    
    full_path = os.path.join(path_codes, file_path)
    
    with open(full_path, "w") as f:
        f.write(code)
    
    return f"File '{file_path}' created/updated successfully."

@beta_tool
def read_file(file_path: str) -> str:
    """
    Read and return the exact content of an existing file in the system.
    
    Args:
        file_path: The name or relative/absolute path of the file to read (e.g., 'main.py', 'config.json').
    """
    print(f"\n[LOG DO CODER] 📖 Lendo o arquivo: {file_path}")
    
    full_path = os.path.join(path_codes, file_path)
    
    try:
        with open(full_path, "r") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: The file '{file_path}' was not found. Please verify the path."