import anthropic
import json
from dotenv import load_dotenv
from tools_agents import tools_jarvis
from pathlib import Path

load_dotenv()
prompt_jarvis= Path("prompts/prompt_system.md").read_text()
prompt_coder= Path("prompts/prompt_coder.md").read_text()

client= anthropic.Anthropic()

def send_message_user(mensagem, tools, model, prompt_to_use, max_tokens, tc= "auto"):
    if prompt_to_use == "jarvis":
        prompt= prompt_jarvis
    elif prompt_to_use == "coder":
        prompt= prompt_coder
        
    runner= client.beta.messages.tool_runner(
        model=model,
        max_tokens=max_tokens,
        tools= tools,
        system= prompt,
        tool_choice= {"type": tc},
        messages= mensagem,
    )
    return runner