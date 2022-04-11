import re
import os
import asyncio
from datetime import datetime
import string
from optparse import OptionParser


def is_hex(s):
    hex_digits = set(string.hexdigits)
    return all(c in hex_digits for c in s)


class HttpServerProtocol(asyncio.Protocol):

    content_types = {
        "html": "text/html",
        "css": "text/css",
        "js": "text/javascript",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "swf": "application/x-shockwave-flash",
    }

    def __init__(self, rootdir=".", name="_"):
        super().__init__
        self._header = {}
        self._req_type = None
        self._directory = "/"
        self._name = name
        self._rootdir = rootdir

    @property
    def directory(self):
        return self._directory

    @directory.setter
    def directory(self, dir):
        r = ""
        i = 0
        while i < len(dir):
            c = dir[i]
            if c == "%" and i + 2 < len(dir) and is_hex(dir[i + 1 : i + 3]):
                r += chr(int(dir[i + 1 : i + 3], 16))
                i += 2
            elif c == "?":
                break
            else:
                r += c
            i += 1

        if r.endswith("/"):
            r += "index.html"

        self._directory = r

    def connection_made(self, transport):
        """Хук на установление соединения"""
        # peername = transport.get_extra_info("peername")
        # print("Connection from {}".format(peername))
        self.transport = transport
        self.data = b""

    def data_received(self, data):
        """Хук на примем данных по соединение. Обработка входящего запроса"""
        regexp = r"^(GET|HEAD|POST|PUT|DELETE) .* HTTP/1.[01].*\r\n\r\n"
        if re.search(regexp, data.decode(), flags=re.DOTALL) is not None:
            self.parse_request(data)
            # print(f"server={self._name} data={data}")
            response = self.get_response()
            self.transport.write(response)

        # Close the client socket
        self.transport.close()

    def parse_request(self, data):
        headers = data.decode().split("\r\n")
        # Из первой строки получить тип запроса и путь к файлу
        req_line = headers[0].split()
        try:
            self._req_type = req_line[0]
        except IndexError:
            print("data=", data)
            print("self.data=", self.data)
            # raise IndexError
        self.directory = req_line[1]
        # Сгенерить словарь с полями заголовка запроса
        self._header.clear()
        for i in range(1, len(headers) - 1):
            s = headers[i]
            hdr = [x.strip() for x in s.split(":")]
            if len(hdr) == 2:
                self._header[hdr[0]] = hdr[1]

    def get_response(self):
        code, content = self.get_content()
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
        r += "Date: " + datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT") + "\r\n"
        r += "Content-Length: " + str(len(content)) + "\r\n"
        r += "Content-Type: " + self.get_content_type() + "\r\n"
        r += "Connection: close\r\n"
        r += "\r\n"
        return r.encode("utf-8") + (b"" if self._req_type == "HEAD" else content)

    def get_content(self):

        if self._req_type != "GET" and self._req_type != "HEAD":
            return 405, b"Method Not Allowed"

        filename = self._rootdir + self.directory

        if not os.path.abspath(filename).startswith(os.path.abspath(self._rootdir)):
            return 403, b"Forbidden"

        if not os.path.isfile(filename):
            return 404, b"File not found"

        with open(filename, "rb") as file:
            return 200, file.read()

    def get_content_type(self):
        _, ext = os.path.splitext(self.directory)
        ctype = self.content_types.get(ext.replace(".", ""))
        return ctype if ctype is not None else "Unknown"


def main(opts):

    loop = asyncio.get_event_loop()
    servers = []
    for i in range(opts.workers):
        print(f"Starting server {i+1}")
        coro = loop.create_server(lambda: HttpServerProtocol(opts.root, str(i + 1)), "127.0.0.1", opts.port, reuse_port=True)
        server = loop.run_until_complete(coro)
        servers.append(server)

    try:
        print("Running... Press ^C to shutdown")
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    for i, server in enumerate(servers):
        print("Closing server {0}".format(i + 1))
        server.close()
        loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-w", "--workers", action="store", dest="workers", type=int, default=1)
    op.add_option("-p", "--port", action="store", dest="port", type=int, default=8080)
    op.add_option("-r", "--root", action="store", type=str, default=".")
    (opts, args) = op.parse_args()
    main(opts)
