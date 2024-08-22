from nonebot import on_message, logger
from nonebot.exception import FinishedException
from nonebot.rule import to_me
from nonebot.adapters.qq import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg
from io import BytesIO
from PIL.Image import Image
import sys
# this is plugin to receive any message with any prefix
# and reply with llm response
from ...utils import get_llm_response, LLM_TOTAL_COST, LLM_COST_THRESHOLD
from ..problem import get_daily_challenge
from ..problem import get_problem
llm_chat = on_message(rule=to_me(),priority=10,block=True)
ALLOWED_TASKS = ["help", "chat", "daily", "每日挑战", "problem","题目",""]
@llm_chat.handle()
async def handle_dm(event: MessageEvent):
    await llm_chat.finish("pong!")
    if LLM_TOTAL_COST > LLM_COST_THRESHOLD:
        logger.warning(f"Total cost {LLM_TOTAL_COST} exceeds threshold {LLM_COST_THRESHOLD}. Chat request suspended.")
        await llm_chat.finish(Message("好累呀，让我摸一会儿鱼，等等再聊天吧~"))
    request_text = event.get_plaintext()
    logger.debug(f"**************************")
    logger.debug(f"Received message: {request_text}")
    logger.debug(f"User ID: {event.get_user_id()}")
    try:
        response = await get_llm_response(request_text, "json", "rp")
        logger.debug(f"RP Response: {response}")
        if isinstance(response, dict):
            task = response.get("task", "")
            questionId = response.get("questionId", "")
            reply = response.get("reply", "")

            # if task
            if reply:
                logger.debug(f"sending reply: {reply}")
                await llm_chat.send(reply)
            if task in ALLOWED_TASKS:
                # if help task, get better llm to help
                if task == "help":
                    response = await get_llm_response(request_text, "img", "solver")
                    if isinstance(response, Image):
                        img_buffer = BytesIO()
                        response.save(img_buffer, format="PNG")
                        text = "帮你问到了哦，来看看吧~"
                        msg = Message([MessageSegment.text(text), MessageSegment.file_image(img_buffer.getvalue())])
                        await llm_chat.send(msg)
                    else:
                        await llm_chat.finish(Message("我哥不在哦，等会再问问吧~"))
                else:
                    # this is hack, just to make life easier
                    event.__setattr__("_message",Message(task))
                    if task in ("daily", "每日挑战"):
                        await get_daily_challenge(event)
                    elif task in ("problem","题目"):
                        await get_problem(event, Message(questionId))
        else:
            await llm_chat.finish(Message("好像听不懂呢~"))
    except FinishedException:
        logger.debug(f"Chat request finished.")
    except Exception as e:
        # get trace
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(f"Failed to get llm response due to {e} at line {exc_traceback.tb_lineno if exc_traceback else 0}")
        # log detail
        logger.error(f"Exception: {e}, exc_type: {exc_type}, exc_value: {exc_value}, exc_traceback: {exc_traceback}")
        await llm_chat.finish(Message("哎哟，信号不好，等下再试试吧~"))


