import utils
from tools_agents import tools_jarvis, tools_coder
import time
from config import (
    JARVIS_MODEL, CODER_MODEL, JARVIS_MAX_TOKENS,
    CODER_MAX_TOKENS, MODEL_PRICES  
)

def new_stats():
    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "tool_calls": 0,
        "tools": [],
        "agents": set(),
        "handoffs": 0,
        "cost": 0.0,
    }

def mostrar_stats(stats, tempo):
    tools_usadas = ", ".join(stats["tools"]) if stats["tools"] else "nenhuma"

    print("\n╭────────── JARVIS RUN ──────────╮")
    print(f"│ Input tokens : {stats['input_tokens']:>10}")
    print(f"│ Output tokens: {stats['output_tokens']:>10}")
    print(f"│ Tool calls   : {stats['tool_calls']:>10}")
    print(f"│ Agents       : {len(stats['agents']):>10}")
    print(f"│ Handoffs     : {stats['handoffs']:>10}")
    print(f"│ Time         : {tempo:>8.2f} s")
    print(f"│ Cost         : ${stats['cost']:>9.5f}")
    print("╰────────────────────────────────╯")
    print(f"Tools: {tools_usadas}\n")

question = input("Você: ")
stats= new_stats()
inicio_tarefa= time.perf_counter()

jarvis_tools= [tools_jarvis.create_note, tools_jarvis.list_notes, tools_jarvis.read_note, tools_jarvis.search_notes, tools_jarvis.transfer_to_coder, tools_jarvis.delete_note, tools_jarvis.update_note]
coder_tools= [tools_coder.transfer_to_jarvis, tools_coder.create_code, tools_coder.read_file]

agente_ativo= "jarvis"
historico_jarvis= [{"role": "user", "content": question}]
historico_coder= []

while True:
    if agente_ativo == "jarvis":
        historico_da_vez = historico_jarvis
        modelo_da_vez = JARVIS_MODEL 
        limite_tokens = JARVIS_MAX_TOKENS
        prompt_da_vez = "jarvis"
        ferramentas_da_vez = jarvis_tools

    elif agente_ativo == "coder":
        historico_da_vez = historico_coder
        modelo_da_vez = CODER_MODEL 
        limite_tokens = CODER_MAX_TOKENS
        prompt_da_vez = "coder"
        ferramentas_da_vez = coder_tools 

    stats["agents"].add(agente_ativo)

    ####    Poda da Memoria    ####
    if len(historico_da_vez) > 6:   
        historico_inicio= historico_da_vez[0:1]
        historico_final= historico_da_vez[-4:]
        historico_da_vez= historico_inicio + historico_final
    ####    Poda da Memoria    ####

    ####    Looping de Mensagem    ####
    runner= utils.send_message_user(historico_da_vez, ferramentas_da_vez, modelo_da_vez, 
                                    prompt_da_vez, limite_tokens)

    final_message= None

    for message in runner:
        final_message= message

        stats["input_tokens"]+= message.usage.input_tokens
        stats["output_tokens"]+= message.usage.output_tokens

        preco= MODEL_PRICES[modelo_da_vez]

        stats["cost"]+= (message.usage.input_tokens/1_000_000) * preco["input"]
        stats["cost"]+= (message.usage.output_tokens/1_000_000) * preco["output"]

        for block in message.content:
            if(block.type == "tool_use"):
                stats["tool_calls"]+= 1
                stats["tools"].append(block.name)

    handoff_acionado= False
    tarefa_para_coder= ""
    motivo= ""

    for block in final_message.content:
        if block.type == "text":
            if "[HANDOFF_CODER]" in block.text:
                tarefa_para_coder= block.text.replace("[HANDOFF_CODER]", "").strip()
                handoff_acionado= True
                handoff_destino= "coder"
            elif "[HANDOFF_JARVIS]" in block.text:
                motivo= block.text.replace("[HANDOFF_JARVIS]", "").strip()
                handoff_acionado= True
                handoff_destino= "jarvis"
            else:
                print(f"[{agente_ativo.upper()}]: {block.text}")
                historico_da_vez.append({"role": "assistant", "content": block.text})

    if agente_ativo == "jarvis":
        historico_jarvis = historico_da_vez
    elif agente_ativo == "coder":
        historico_coder = historico_da_vez

    if handoff_acionado:
        stats["handoffs"]+= 1
        if handoff_destino == "coder":
            print(f"🔄 Terminal redirecionado para o Coder. Tarefa: '{tarefa_para_coder}'")
            agente_ativo = "coder"
            msg_coder = f"[SISTEMA - ORDEM DE ORQUESTRAÇÃO]\nO usuário pediu a seguinte tarefa de programação: '{tarefa_para_coder}'"
            historico_coder.append({"role": "user", "content": msg_coder})
            continue
        elif handoff_destino == "jarvis":
            print(f"🔄 Terminal redirecionado para o Jarvis. Motivo: '{motivo}'")
            agente_ativo = "jarvis"
            msg_jarvis = f"[SISTEMA - RETORNO DO CODER]\nO agente Coder finalizou o trabalho técnico e devolveu o controle com este relatório: '{motivo}'.\nATENÇÃO: Leia o relatório e atenda a solicitação não-técnica do usuário. NÃO acione a ferramenta de código agora."
            historico_jarvis.append({"role": "user", "content": msg_jarvis})
            continue

    tempo_total= time.perf_counter() - inicio_tarefa
    mostrar_stats(stats, tempo_total)

    stats= new_stats()
    inicio_tarefa= time.perf_counter()

    print("\n")
    question= input("Você: ")
    historico_da_vez.append({"role": "user", "content": question})
    ####    Looping de Mensagem    ####      


