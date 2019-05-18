import websocket
import ssl
import json
import threading
import re
import time
import asyncio
from teapotbot.discord import SendMessageToChannel
from teapotbot.db import LoadSetting, StoreSetting
from teapotbot.discord import CmdHandler

players = []
games = []
last_is_leela = False

_loop = asyncio.get_event_loop()


async def on_new_game(player1, player2):
    player_re = re.compile(LoadSetting('cccc', 'player_re'))
    if not player_re.search(player1) and not player_re.search(player2):
        last_is_leela = False
        return
    if not LoadSetting('cccc', 'allow_back_to_back') and last_is_leela:
        return

    last_is_leela = True

    ts = int(time.time())
    ts_limit = LoadSetting('cccc', 'suspend_until')

    if ts < ts_limit:
        return

    ts += LoadSetting('cccc', 'autosuspend')
    if ts > ts_limit:
        StoreSetting('cccc', 'suspend_until', ts)

    await SendMessageToChannel(
        LoadSetting('cccc', 'channel_id'),
        LoadSetting('cccc', 'message').format(player1=player1,
                                              player2=player2),
        LoadSetting('cccc', 'duck_url'))


def on_message(ws, message):
    if not LoadSetting('cccc', 'enabled'):
        return
    global players
    global games
    cur_game = LoadSetting('cccc', 'cur_game')
    msg = json.loads(message)
    if 'players' in msg:
        players = msg['players']
    if 'schedule' in msg:
        games = msg['schedule']
        new_cur_game = next(i for i in range(len(games))
                            if 'res' not in games[i])
        if new_cur_game > cur_game or new_cur_game < (cur_game - 2):
            game = games[new_cur_game]['p']
            p1 = players[game[0]]
            p2 = players[game[1]]
            asyncio.run_coroutine_threadsafe(on_new_game(p1, p2), _loop)
            StoreSetting('cccc', 'cur_game', new_cur_game)


websocket.enableTrace(True)
ws = websocket.WebSocketApp("wss://cccc.chess.com/websocket",
                            on_message=on_message)

wst = threading.Thread(target=ws.run_forever,
                       kwargs={'sslopt': {
                           "cert_reqs": ssl.CERT_NONE
                       }})
wst.daemon = True
wst.start()


@CmdHandler
async def CmdCcccSuspend(context):
    params = context.ParseParams(1)
    if not params:
        await context.SendUsage('!CcccSuspend <number of seconds>')
        return
    ts = int(time.time())
    StoreSetting('cccc', 'suspend_until', ts + int(params[0]))
    await context.Done()
