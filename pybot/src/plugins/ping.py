from nonebot import on_command, logger
import nonebot.adapters
from nonebot.adapters.qq import Message, MessageEvent, bot
from nonebot.params import CommandArg
import nonebot
ping = on_command("ping", aliases={"在吗宝宝"}, priority=9,block=True)

@ping.handle()
async def handle_first_receive(event: MessageEvent, args:Message = CommandArg()):
    guild_id = event.get_session_id()
    user_id = event.get_user_id()  
    bot = nonebot.get_bot()
    user_info = await bot.call_api("get_guild_member",user_id=event.get_user_id())
    
    logger.debug("***********")
    logger.debug(user_info)
    await ping.send("在呢在呢~")