from nonebot import on_command
from nonebot.adapters.qq import Message, MessageEvent
from nonebot.params import CommandArg

ping = on_command("ping", aliases={"在吗宝宝"})

@ping.handle()
async def handle_first_receive(event: MessageEvent, args:Message = CommandArg()):
    await ping.send("在呢在呢~")