import chainlit as cl
from src.api.dependencies import get_agent

@cl.on_chat_start
async def start():
    await cl.Message(content="Привет! Я AetherChat — спросите меня о чём угодно из загруженных документов.").send()

@cl.on_message
async def main(message: cl.Message):
    # Получаем историю диалога из сессии Chainlit
    messages = cl.user_session.get("messages", [])
    history = []
    for m in messages[:-1]:  # исключаем текущее сообщение
        role = "user" if m["author"] == "user" else "assistant"
        history.append({"role": role, "content": m["content"]})
    agent = get_agent()
    answer = await agent.arun(message.content, history)
    await cl.Message(content=answer).send()