
def send_message_user(client, history, tools, model="claude-haiku-4-5-20251001", max_tokens= 1000, tc= "auto"):
    message= client.messages.create(
        model=model,
        max_tokens=max_tokens,
        tools= tools,
        system="Você é um assistente direto e objetivo. NUNCA liste as ferramentas que você possui, a menos que o usuário pergunte explicitamente o que você sabe fazer e nem indique nada relacionado a elas.",
        tool_choice= {"type": tc},
        messages= history,
    )
    return message

def create_return_packet(response, id):
    return_packet= {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": id,
                        "content": str(response)
                    }
                ]
            }
    return return_packet