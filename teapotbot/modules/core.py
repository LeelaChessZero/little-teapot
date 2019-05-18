from teapotbot.discord import CmdHandler, Escape
from teapotbot.db import ListSettings, StoreSetting
import ast


@CmdHandler
async def CmdBotVars(context):
    mask = context.ParseParams(1)
    mask = mask[0] if mask else ''

    values = []

    for entry, value in ListSettings():
        if entry == 'discord.token':
            continue
        if mask not in entry:
            continue
        values.append((entry, value))

    if values:
        await context.message.channel.send('%s' % '\n'.join([
            '**%s** `%s`' % (x[0], Escape(repr(x[1]))) for x in sorted(values)
        ]))
    else:
        await context.Send('(nothing found)')


@CmdHandler
async def CmdSetBotVar(context):
    entry, value = tuple(context.ParseParams(1))
    value = ast.literal_eval(value)
    module, entry = entry.split('.', 2)
    StoreSetting(module, entry, value)
    await context.Done()
