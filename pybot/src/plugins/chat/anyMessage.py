from nonebot import on_message, logger, on_type
from nonebot.rule import is_type
from nonebot.adapters.qq import Message, MessageEvent, MessageSegment, GroupMsgReceiveEvent
from nonebot.params import CommandArg
from io import BytesIO
# this is plugin to receive any message with any prefix
# and reply with llm response
from ...utils import get_llm_response, LLM_TOTAL_COST, LLM_COST_THRESHOLD
from ..problem import get_daily_challenge
from ..problem import get_problem
llm_group_chat = on_message(rule=None,priority=11,block=True)
@llm_group_chat.handle()
async def handle_general_chat(event: MessageEvent):
    logger.debug(f"Received message: {event.get_message()}")
    # currently, QQ do not have api for listening to all group messages