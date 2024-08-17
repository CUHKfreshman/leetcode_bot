from nonebot import on_message, logger
from nonebot.rule import to_me
from nonebot.adapters.qq import Message, MessageEvent, MessageSegment
from nonebot.params import CommandArg
from io import BytesIO
# this is plugin to receive any message with any prefix
# and reply with llm response
from ..utils import get_llm_response
from .dailyChallenge import get_daily_challenge
from .problem import get_problem
llm_chat = on_message(rule=to_me(),priority=10,block=True)
ALLOWED_TASKS = ["help", "chat", "daily", "每日挑战", "problem","题目",""]
@llm_chat.handle()
async def handle_chat(event: MessageEvent):
    
    request_text = event.get_plaintext()
    logger.debug(f"**************************")
    logger.debug(f"Received message: {request_text}")
    logger.debug(f"User ID: {event.get_user_id()}")
    response = await get_llm_response(request_text, "json", "rp")
    if response:
        task = response.get("task", "")
        questionId = response.get("questionId", "")
        reply = response.get("reply", "")
        logger.debug(f"Task: {task}, Question ID: {questionId}, Reply: {reply}")
        # if task
        if reply:
            logger.debug(f"sending reply: {reply}")
            await llm_chat.send(reply)
        if task in ALLOWED_TASKS:
            # if help task, get better llm to help
            if task == "help":
                response = await get_llm_response(request_text, "img", "solver")
                if response:
                    img_buffer = BytesIO()
                    response.save(img_buffer, format="PNG")
                    text = "帮你问到了哦，来看看吧~"
                    msg = Message([MessageSegment.text(text), MessageSegment.file_image(img_buffer.getvalue())])
                    await llm_chat.finish(msg)
                else:
                    await llm_chat.finish(Message("我哥不在哦，等会再问问吧~"))
            else:
                # hack
                event.__setattr__("_message",Message(task))
                if task in ("daily", "每日挑战"):
                    await get_daily_challenge(event)
                elif task in ("problem","题目"):
                    await get_problem(event, Message(questionId))
    else:
        await llm_chat.finish(Message("好像听不懂呢~"))



