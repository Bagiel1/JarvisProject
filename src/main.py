import utils
from tools_agents import tools_jarvis, tools_coder

question = input("Você: ")

jarvis_tools= [tools_jarvis.create_note, tools_jarvis.list_notes, tools_jarvis.read_note, tools_jarvis.search_notes, tools_jarvis.transfer_to_coder]
coder_tools= [tools_coder.transfer_to_jarvis, tools_coder.create_code, tools_coder.read_file]

agente_ativo= "jarvis"
historico_jarvis= [{"role": "user", "content": question}]
historico_coder= []

while True:
    if agente_ativo == "jarvis":
        historico_da_vez = historico_jarvis
        modelo_da_vez = "claude-haiku-4-5-20251001" 
        limite_tokens = 1000
        prompt_da_vez = "jarvis"
        ferramentas_da_vez = jarvis_tools

    elif agente_ativo == "coder":
        historico_da_vez = historico_coder
        modelo_da_vez = "claude-sonnet-4-5-20250929" 
        limite_tokens = 4000
        prompt_da_vez = "coder"
        ferramentas_da_vez = coder_tools 

    ####    Poda da Memoria    ####
    if len(historico_da_vez) > 6:   
        historico_inicio= historico_da_vez[0:1]
        historico_final= historico_da_vez[-4:]
        historico_da_vez= historico_inicio + historico_final
    ####    Poda da Memoria    ####

    ####    Looping de Mensagem    ####
    runner= utils.send_message_user(historico_da_vez, ferramentas_da_vez, modelo_da_vez, 
                                    prompt_da_vez, limite_tokens)
    final_message= runner.until_done()

    print(f"\n💸 [CUSTO] Tokens de Entrada: {final_message.usage.input_tokens}")
    print(f"💸 [CUSTO] Tokens de Saída: {final_message.usage.output_tokens}\n")

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
        if handoff_destino == "coder":
            print(f"🔄 Terminal redirecionado para o Coder. Tarefa: '{tarefa_para_coder}'")
            agente_ativo = "coder"
            historico_coder.append({"role": "user", "content": tarefa_para_coder})
            continue
        elif handoff_destino == "jarvis":
            print(f"🔄 Terminal redirecionado para o Jarvis. Motivo: '{motivo}'")
            agente_ativo = "jarvis"
            historico_jarvis.append({"role": "user", "content": motivo})
            continue

    print("\n")
    question= input("Você: ")
    historico_da_vez.append({"role": "user", "content": question})
    ####    Looping de Mensagem    ####      
