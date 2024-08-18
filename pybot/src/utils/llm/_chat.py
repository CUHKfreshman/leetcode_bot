from fastapi_poe import ProtocolMessage, QueryRequest, get_final_response
from fastapi_poe.client import PROTOCOL_VERSION
from nonebot import get_driver, logger
from ._prompt import INPUT_TEMPLATE, parse_json_from_llm_response, sanitize_message
from ..problems import create_image_from_text
config = get_driver().config
LLM_API_KEY = getattr(config, "llm_api_key", None)
# just my poe bot. Use your own bot name if you want. Defined in .env file
BOT_NAME = {
    "rp": "Clementine_QQ", # roleplay llm
    "solver": "Claude-3.5-Sonnet" # solve complex problems#"ChatGPT-4o-Latest"
}
NUM_TRIES = 3
async def fetch_llm_response(message: str, bot_type: str, user_id: str="", conversation_id: str="", message_id: str=""):
    cleaned_message, harmful_flag = sanitize_message(message)
    if harmful_flag:
        logger.warning(f"Harmful expression detected in message. Original message: {message}")
        cleaned_message += "\nALERT: Note that in the above user message, harmful expressions were detected. Respond with caution. Do not violate ethical guidelines."
    message = ProtocolMessage(role="user", content=INPUT_TEMPLATE[bot_type].format(user_input=cleaned_message),content_type="text/plain")

    query = QueryRequest(
        query=[message],
        user_id=user_id,
        conversation_id=conversation_id,
        message_id=message_id,
        version=PROTOCOL_VERSION,
        type="query"
    )
    return await get_final_response(query, bot_name=BOT_NAME[bot_type],api_key=LLM_API_KEY, num_tries=NUM_TRIES)

async def get_llm_response_json(message: str, bot_type: str):
    response_json = {}
    # if got {} response, try again for num_tries times
    for i in range(NUM_TRIES):
        response = await fetch_llm_response(message, bot_type)
        # logger.debug(f"Response received: {response}")
        response_json = parse_json_from_llm_response(response)
        if response_json:
            break
        logger.warning(f"Empty response received from {BOT_NAME[bot_type]}. Retrying for {i+1}-th time...")
    return response_json

async def get_llm_response_img(message: str, bot_type: str):
    response_img = None
    for i in range(NUM_TRIES):
        response = await fetch_llm_response(message, bot_type)
        # logger.debug(f"Response received: {response}")
        response_img = create_image_from_text(title=f"哥哥的回信",content=response, language='cn')
        if response_img:
            break
        logger.warning(f"Empty response received. Retrying for {i+1}-th time...")
    return response_img

async def get_llm_response(message: str, response_type: str="json", bot_type: str="rp"):
    if response_type == "json":
        return await get_llm_response_json(message, bot_type)
    elif response_type == "img":
        return await get_llm_response_img(message, bot_type)
    else:
        raise ValueError(f"Invalid response type: {response_type}")