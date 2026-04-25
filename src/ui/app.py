import chainlit as cl
from src.api.dependencies import get_agent
from src.core.config import settings
import asyncio

@cl.on_chat_start
async def start():
    await cl.Message(content="Привет! Я AetherChat — спросите меня о чём угодно из загруженных документов.").send()

@cl.on_message
async def main(message: cl.Message):
    # Получаем историю из Chainlit
    history = []
    for m in cl.context.session.messages[:-1]:  # кроме текущего
        history.append({"role": "user" if m.author == "user" else "assistant", "content": m.content})
    
    agent = get_agent()
    answer = await agent.arun(message.content, history)
    await cl.Message(content=answer).send()