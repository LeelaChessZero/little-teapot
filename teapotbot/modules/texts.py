from teapotbot.discord import CmdHandler, CmdHook, HasHandler
from teapotbot.db import StoreCommand, RemoveCommand, LoadCommand


@CmdHandler
async def CmdAddCmd(context):
    name, text = tuple(context.ParseParams(2))
    if HasHandler(name):
        await context.Send('**Error:** Cannot override built-in command')
        return
    StoreCommand(name, text)
    await context.Send('Added command **!%s**.' % name)


@CmdHandler
async def CmdRmCmd(context):
    name = tuple(context.ParseParams(1))
    RemoveCommand(name)
    await context.Done()


@CmdHook
async def OnCommand(context):
    msg = LoadCommand(context.cmd)
    if msg:
        await context.Send(msg)
        return True
    return False