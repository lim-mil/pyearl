from werkzeug import run_simple, Response

from pyearl.wsgi.wsgi_app import wsgi_app


class Pyearl:

    def __init__(self):
        """
        实例化方法
        """
        self.host = '127.0.0.1'  # 默认主机
        self.port = 7382  # 默认端口

    def dispatch_request(self, request):
        """
        匹配路由
        :return:
        """
        status = 200

        headers = {
            'Server': 'pyearl'
        }

        return Response('<h1>hello, pyearl</h1>', content_type='text/html', headers=headers, status=status)

    def run(self, host=None, port=None, **options):
        """
        启动
        :return:
        """
        for key, value in options.items():
            if value is not None:
                self.__setattr__(key, value)

        if host:
            self.host = host
        if port:
            self.port = port

        run_simple(hostname=self.host, port=self.port, application=self, **options)

    def __call__(self, environ, start_response):
        """

        :param args:
        :param kwargs:
        :return:
        """
        return wsgi_app(self, environ, start_response)
