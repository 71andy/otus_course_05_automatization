import re
import os
import asyncio
from datetime import datetime
import string
from optparse import OptionParser
from multiprocessing import Process
from urllib import response
from urllib.parse import urlparse, unquote
import mimetypes


class Request:
    def __init__(self, data):
        self._path = None
        self._valid = False
        self._header = {}
        self._req_type = None
        self._request = data.decode()
        self._parse_request()

    def is_valid(self):
        return self._valid

    @property
    def type(self):
        return self._req_type

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, dir):
        r = urlparse(unquote(dir)).path
        if r.endswith("/"):
            r += "index.html"
        self._path = r

    def _parse_request(self):
        regexp = r"^(GET|HEAD|POST|PUT|DELETE) .* HTTP/1.[01].*\r\n\r\n"
        if re.search(regexp, self._request, flags=re.DOTALL) is None:
            self._valid = False
            return

        self._valid = True
        headers = self._request.split("\r\n")
        # Из первой строки получить тип запроса и путь к файлу
        req_line = headers[0].split()
        self._req_type = req_line[0]
        self.path = req_line[1]
        # Сгенерить словарь с полями заголовка запроса
        for i in range(1, len(headers) - 1):
            s = headers[i]
            hdr = [x.strip() for x in s.split(":")]
            if len(hdr) == 2:
                self._header[hdr[0]] = hdr[1]


class Responser:
    def __init__(self, request: Request, rootdir: str):
        self.request = request
        self.rootdir = rootdir

    def _get_content(self):

        req_type = self.request.type
        if req_type != "GET" and req_type != "HEAD":
            return 405, 0, b"Method Not Allowed"

        filename = self.rootdir + self.request.path

        if not os.path.abspath(filename).startswith(os.path.abspath(self.rootdir)):
            return 403, 0, b"Forbidden"

        if not os.path.isfile(filename):
            return 404, 0, b"File not found"

        fsize = os.path.getsize(filename)
        if req_type == "HEAD":
            return 200, fsize, b""

        with open(filename, "rb") as file:
            return 200, fsize, file.read()

    def get_response(self):
        code, content_size, content = self._get_content()
        mt = mimetypes.guess_type(self.request.path)[0]
        r = ""
        if code == 200:
            r += "HTTP/1.1 200 OK\r\n"
        elif code == 404:
            r += "HTTP/1.1 404 Not Found\r\n"
        elif code == 403:
            r += "HTTP/1.1 403 Forbidden\r\n"
        else:
            r += "HTTP/1.1 405 Method Not Allowed\r\n"
        r += "Server: Otus course http server\r\n"
        r += f"Date: { datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT') }\r\n"
        r += f"Content-Length: {str(content_size)}\r\n"
        if mt:
            r += f"Content-Type: {mt}\r\n"
        r += "Connection: close\r\n"
        r += "\r\n"
        return r.encode("utf-8") + content


class HttpServerProtocol(asyncio.Protocol):
    def __init__(self, rootdir=".", name="_"):
        super().__init__()
        self._name = name
        self._rootdir = rootdir

    def connection_made(self, transport):
        """Хук на установление соединения"""
        self.transport = transport

    def data_received(self, data):
        """Хук на прием данных по соединению. Обработка входящего запроса"""
        request = Request(data)
        if request.is_valid():
            responser = Responser(request, self._rootdir)
            self.transport.write(responser.get_response())

        self.transport.close()  # Close the client socket


def worker_func(opts, name):

    loop = asyncio.get_event_loop()
    servers = []
    coro = loop.create_server(lambda: HttpServerProtocol(opts.root, name), "127.0.0.1", opts.port, reuse_port=True)
    server = loop.run_until_complete(coro)
    servers.append(server)

    print(f"Starting: {name}")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    for i, server in enumerate(servers):
        print(f"Closing: {name}")
        server.close()
        loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-w", "--workers", action="store", dest="workers", type=int, default=1)
    op.add_option("-p", "--port", action="store", dest="port", type=int, default=8080)
    op.add_option("-r", "--root", action="store", type=str, default=".")
    (opts, args) = op.parse_args()

    workers = []
    for i in range(opts.workers):
        worker = Process(target=worker_func, args=(opts, "server " + str(i + 1)), daemon=True)
        worker.start()
        workers.append(worker)

    try:
        print("Running... Press ^C to shutdown")
        for w in workers:
            w.join()
    except KeyboardInterrupt:
        print("Exit...")
