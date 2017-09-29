#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ 'jnuyanfa'

'''
async web application.
'''

import logging; logging.basicConfig(level=logging.INFO, \
format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
import asyncio, os, json, time
from datetime import datetime
from aiohttp import web
import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('-b', '--bind', dest='bind_host', default='localhost')
parser.add_argument('-p', '--port', dest='port', default=9000)
args = parser.parse_args()

def index(request):
    return web.Response(body=b'<h1>Awesome</h1>', content_type='text/html')

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = await loop.create_server(app.make_handler(), args.bind_host, args.port)
    logging.info('server started at http://%s:%s...', args.bind_host, args.port)
    return srv

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()
