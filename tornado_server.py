from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from app import app
from tornado import platform
import sys

if sys.platform == 'win32':
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(5002, address='0.0.0.0')
IOLoop.current().start()
