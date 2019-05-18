import discord
import re
import teapotbot.db as db

client = discord.Client()

HOOKS = []
CMD_HOOK = []
CMD_HANDLERS = {}


class Command:
    def __init__(self, func, only_admins, only_botspam):
        self.only_admins = only_admins
        self.only_botspam = only_botspam
        self.func = func

    async def Execute(self, context):
        await self.func(context)


def MessageHook(func):
    HOOKS.append(func)
    return func


def CmdHook(func):
    CMD_HOOK.append(func)
    return func


def HasHandler(cmd):
    return cmd in CMD_HANDLERS


def CmdHandler(f, cmd=None, only_admins=True, only_botspam=False):
    if cmd is None:
        cmd = f.__name__
        if cmd.startswith('Cmd'):
            cmd = cmd[3:]
    cmd = cmd.lower()
    CMD_HANDLERS[cmd] = Command(f, only_admins, only_botspam)
    return f


class Context:
    def __init__(self, cmd, message, full_params):
        self.cmd = cmd
        self.message = message
        self.full_params = full_params

    def ParseParams(self, num):
        return self.full_params.split(maxsplit=num - 1)

    def IsAdmin(self):
        admin_role_ids = set(db.LoadSetting('discord', 'admin_role_ids'))
        user_roles = set([x.id for x in self.message.author.roles])
        return bool(admin_role_ids & user_roles)

    async def Send(self, message):
        await self.message.channel.send(message)

    async def Done(self):
        await self.Send('**Done!**')

    async def SendUsage(self, usage):
        await self.Send('**Usage:** %s' % usage)


COMMAND_RE = re.compile(r'(?s)^!(\S+)\s*(.*)')


async def DefaultMessageHandler(message):
    m = COMMAND_RE.match(message.content)
    if not m:
        return False

    cmd = m.group(1).lower()

    context = Context(cmd, message, m.group(2))

    for hook in CMD_HOOK:
        if await hook(context):
            return True

    command = CMD_HANDLERS.get(cmd)
    if not command:
        return False

    if command.only_botspam:
        botspam_channel_ids = db.LoadSetting('discord', 'botspam_ids')
        if message.channel.id not in botspam_channel_ids:
            return False

    if command.only_admins and not context.IsAdmin():
        return False

    await command.Execute(context)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    try:
        for hook in HOOKS:
            if await hook(message):
                return

        await DefaultMessageHandler(message)

    except Exception as e:
        await message.channel.send("Error: ```%s```" % e)
        raise


ESCAPE_RE = re.compile(r'([-`*_\\|])')


def Escape(msg):
    return ESCAPE_RE.sub(r'\\\1', msg)


async def SendMessageToChannel(channel_id, msg, duck_url):
    channel = client.get_channel(id=channel_id)
    embed = discord.Embed()
    embed.set_image(url=duck_url)
    await channel.send(msg, embed=embed)


def Run():
    client.run(db.LoadSetting('discord', 'token'))
