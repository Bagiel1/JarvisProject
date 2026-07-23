import anthropic
import json
from dotenv import load_dotenv
import tools
from pathlib import Path

load_dotenv()
prompt_system= Path("prompt_system.md").read_text()

ferramentas= [tools.create_note, tools.list_notes, tools.read_note, tools.search_notes]

client= anthropic.Anthropic()

def send_message_user(mensagem, tools= ferramentas, model="claude-haiku-4-5-20251001", max_tokens= 1000, tc= "auto"):
    runner= client.beta.messages.tool_runner(
        model=model,
        max_tokens=max_tokens,
        tools= tools,
        system= prompt_system,
        tool_choice= {"type": tc},
        messages= mensagem,
    )
    return runner