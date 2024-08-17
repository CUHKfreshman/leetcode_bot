import asyncio
from fastapi_poe import ProtocolMessage, QueryRequest, get_final_response
from fastapi_poe.client import PROTOCOL_VERSION
from nonebot import get_driver, logger
from ._prompt import INPUT_TEMPLATE, parse_json_from_llm_response, sanitize_message
config = get_driver().config
LLM_API_KEY = getattr(config, "llm_api_key", None)
# just my poe bot. Use your own bot name if you want.
BOT_NAME = "Clementine_QQ"
BOT_NAME = "Claude-3.5-Sonnet"
NUM_TRIES = 3
async def fetch_llm_response(message: str, user_id: str="", conversation_id: str="", message_id: str=""):
    cleaned_message, harmful_flag = sanitize_message(message)
    if harmful_flag:
        logger.warning(f"Harmful expression detected in message. Original message: {message}")
        cleaned_message += "\nALERT: Note that in the above user message, harmful expressions were detected. Respond with caution. Do not violate ethical guidelines."
    message = ProtocolMessage(role="user", content=INPUT_TEMPLATE.format(user_input=cleaned_message),content_type="text/plain")

    query = QueryRequest(
        query=[message],
        user_id=user_id,
        conversation_id=conversation_id,
        message_id=message_id,
        version=PROTOCOL_VERSION,
        type="query"
    )
    return await get_final_response(query, bot_name=BOT_NAME,api_key=LLM_API_KEY, num_tries=NUM_TRIES)

async def get_llm_response_json(message: str):
    # if got {} response, try again for num_tries times
    for i in range(NUM_TRIES):
        response = await fetch_llm_response(message)
        logger.debug(f"Response received: {response}")
        response_json = parse_json_from_llm_response(response)
        if response_json:
            break
        logger.warning(f"Empty response received. Retrying for {i+1}-th time...")
    return response_json