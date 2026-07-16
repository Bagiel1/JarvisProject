from dotenv import load_dotenv
import anthropic
import json
import tools
import utils

question= input()

load_dotenv()
with open ("src/tools.json", "r") as f:
    tools= json.load(f)

client= anthropic.Anthropic()

historico= [{"role": "user", "content": question}]

message= utils.send_message_user(client, historico, tools)
historico.append({"role":"assistant", "content": message.content})

for block in message.content:
    if block.type == "tool_use":
        continue

    if block.type == "text":
        print(block.text)
            
