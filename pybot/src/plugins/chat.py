from nonebot import on_message, logger
from nonebot.rule import to_me
from nonebot.adapters.qq import Message, MessageEvent
from nonebot.params import CommandArg
# this is plugin to receive any message with any prefix
# and reply with llm response
from ..utils import get_llm_response_json

llm_chat = on_message(rule=to_me(),priority=10)

@llm_chat.handle()
async def handle_chat(event: MessageEvent):
    logger.debug(f"**************************")
    logger.debug(f"Received message: {event.get_plaintext()}")
    logger.debug(f"User ID: {event.get_user_id()}")
    response = await get_llm_response_json(event.get_plaintext())
    if response:
        await llm_chat.send(Message(response["reply"]))
    else:
        await llm_chat.send(Message("好像听不懂呢~"))



