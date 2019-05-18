import os.path
import sqlite3
import json
import threading
import __main__

CONFIG_FILE = os.path.join(os.path.dirname(__main__.__file__),
                           'data/config.db')


def GetDB():
    data = threading.local()
    if not hasattr(data, 'DB'):
        data.DB = sqlite3.connect(CONFIG_FILE)
    return data.DB


def LoadSetting(module, entry):
    cur = GetDB().cursor()
    cur.execute("SELECT value_json FROM settings where module=? AND entry=?",
                (module, entry))
    row = cur.fetchone()
    if row is None:
        return None
    return json.loads(row[0])


def StoreSetting(module, entry, value):
    db = GetDB()
    cur = db.cursor()
    cur.execute("INSERT OR REPLACE INTO settings VALUES (?, ?, ?)",
                (module, entry, json.dumps(value)))
    db.commit()


def ListSettings():
    db = GetDB()
    cur = db.cursor()
    cur.execute("SELECT module, entry, value_json FROM settings")
    return [('%s.%s' % (x[0], x[1]), json.loads(x[2])) for x in cur.fetchall()]


def StoreUrl(url, full_url, desc):
    db = GetDB()
    cur = db.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO urls(url, redirect, comment) VALUES (?, ?, ?)",
        (url, full_url, desc))
    db.commit()


def RemoveUrl(url):
    db = GetDB()
    cur = db.cursor()
    cur.execute("DELETE FROM urls WHERE url = ?", (url, ))
    db.commit()


def LoadUrl(url):
    cur = GetDB().cursor()
    cur.execute(
        "SELECT url, redirect, comment, featured FROM urls where url=? ",
        (url, ))
    row = cur.fetchone()
    if row is None:
        return None
    return row


def FeatureUrl(url):
    db = GetDB()
    cur = db.cursor()
    cur.execute("UPDATE urls SET featured=1 WHERE url=?", (url, ))
    db.commit()


def ListUrls():
    db = GetDB()
    cur = db.cursor()
    cur.execute(
        "SELECT url, comment, redirect FROM urls WHERE featured=1 ORDER BY url"
    )
    return cur.fetchall()


def StoreUrlDescription(url, desc):
    db = GetDB()
    cur = db.cursor()
    cur.execute("UPDATE urls SET comment=? WHERE url=?", (desc, url))
    db.commit()


def StoreCommand(name, text):
    db = GetDB()
    cur = db.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO commands(command, response) VALUES (?, ?)",
        (name, text))
    db.commit()


def RemoveCommand(name):
    db = GetDB()
    cur = db.cursor()
    cur.execute("DELETE FROM commands WHERE command = ?", (name, ))
    db.commit()


def LoadCommand(name):
    cur = GetDB().cursor()
    cur.execute("SELECT response FROM commands where command=? ", (name, ))
    row = cur.fetchone()
    if row is None:
        return None
    return row[0]