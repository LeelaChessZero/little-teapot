#!/usr/bin/env python3

from flask import Flask, redirect
from teapotbot.db import ListUrls, LoadUrl, LoadSetting
from waitress import serve


def GetUrl(name):
    return LoadSetting('urls', 'url_prefix') + name


app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    url = LoadUrl(path)
    if url:
        return redirect(url[1])
    return (
        '<style>table,td { border: 1px solid gray; '
        'border-collapse: collapse;}</style>'
        '<body>Available URLs:<table>%s</table>' % ''.join([
            '<tr><td><a href="%s" target="_blank">%s</a></td><td>%s</td></tr>'
            % (full_url, GetUrl(url), desc if desc else '(no decription)')
            for url, desc, full_url in ListUrls()
        ]))


if __name__ == '__main__':
    serve(app, host='127.0.0.1', port=3905)
