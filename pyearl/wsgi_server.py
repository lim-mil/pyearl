import socket


class WsgiServer:
    def __init__(self):
        pass

    @property
    def application(self):
        return self.application

    @application.setter
    def application(self, app):
        if not callable(app):
            raise ValueError('app must be a callable object!')
        self.application = app

    def connect(self, host: str, port: int, max_num: int, **options):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.socket.bind((host, port))
        self.socket.listen(max_num)
        self.host = host
        self.port = port

    def run(self, host: str = 'localhost', port: int = 7382, max_num=50, **options):
        self.connect(host, port, max_num, **options)
        while True:
            self.connection, address = self.socket.accept()
            request_msg = self.connection.recv(2048).decode('utf-8')
            self.request_handle()
            print(self.connection.recv(2048).decode('utf-8'))
            print(self.connection, address)
            self.connection.sendall('hello'.encode('utf-8'))

    def request_handle(self, ):
        pass

if __name__ == '__main__':
    wsgi_server = WsgiServer()
    wsgi_server.run()
