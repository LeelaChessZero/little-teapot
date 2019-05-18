import re
from teapotbot.discord import CmdHandler, HasHandler, CmdHook
from teapotbot.db import (LoadSetting, StoreUrl, RemoveUrl, LoadUrl,
                          FeatureUrl, ListUrls, StoreUrlDescription)

RE_URL = re.compile(r'<(https?://.*)>|(https?://.*)')


def GetUrl(name):
    return LoadSetting('urls', 'url_prefix') + name


@CmdHandler
async def CmdAddUrl(context):
    params = context.ParseParams(3)  # id url [desc]
    if len(params) < 2 or not RE_URL.match(params[1]):
        context.SendUsage('!addurl id url [description]')
        return
    m = RE_URL.match(params[1])
    full_url = m.group(1) or m.group(2)
    url = params[0]
    if HasHandler(url):
        await context.Send('**Error:** Cannot override built-in command')
        return
    desc = params[2] if len(params) >= 3 else None
    StoreUrl(url, full_url, desc)
    await context.Send('<%s> is now available as <%s>' %
                       (full_url, GetUrl(url)))


@CmdHandler
async def CmdRmUrl(context):
    url = tuple(context.ParseParams(1))
    RemoveUrl(url)
    await context.Done()


@CmdHandler
async def CmdUnhideUrl(context):
    url, = tuple(context.ParseParams(1))
    FeatureUrl(url)
    await context.Done()


@CmdHandler
async def CmdUrls(context):
    msg = '\n'.join([
        '<%s>: %s' % (GetUrl(url),
                      ('%s' % desc if desc else '*(no description)*'))
        for url, desc, _ in ListUrls()
    ])
    await context.Send(msg)


@CmdHandler
async def CmdHiddenUrls(context):
    msg = ' '.join(
        ['●<%s>' % GetUrl(url) for url, _, _ in ListUrls(hidden=True)])
    await context.Send(msg)


@CmdHandler
async def CmdSetUrlDesc(context):
    params = tuple(context.ParseParams(2))
    url = params[0]
    desc = params[1] if len(params) >= 2 else None
    StoreUrlDescription(url, desc)
    await context.Done()


@CmdHook
async def OnCommand(context):
    data = LoadUrl(context.cmd)
    if not data:
        return False
    url, full_url, comment, _ = data
    await context.Send(
        '%s<%s>\nFull URL is: <%s>.' %
        (('%s: ' % comment) if comment else '', GetUrl(url), full_url))
    return True
