import tools
import utils

question= input()

historico= [{"role": "user", "content": question}]

while True:
    ####    Poda da Memoria    ####
    if len(historico) > 6:   
        historico_inicio= historico[0:1]
        historico_final= historico[-4:]
        historico= historico_inicio + historico_final
    ####    Poda da Memoria    ####

    ####    Looping de Mensagem    ####
    runner= utils.send_message_user(historico)
    final_message= runner.until_done()
    print(f"\n💸 [CUSTO] Tokens de Entrada: {final_message.usage.input_tokens}")
    print(f"💸 [CUSTO] Tokens de Saída: {final_message.usage.output_tokens}\n")
    for block in final_message.content:
        if block.type == "text":
            print(block.text)
            historico.append({"role": "assistant", "content": block.text})

    print("\n")
    question= input()
    historico.append({"role": "user", "content": question})
    ####    Looping de Mensagem    ####      
