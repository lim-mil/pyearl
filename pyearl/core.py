from pathlib import Path, PurePath
from urllib.parse import urlparse

import filetype
from werkzeug import run_simple, Response

from pyearl.exceptions import URLExistsError, EndpointExistsError
from pyearl.route import Route, ERROR_MAP
from pyearl.session import session
from pyearl.utils.producer import create_session_id
from pyearl.wsgi_app import wsgi_app


class Pyearl:

    def __init__(self):
        """
        实例化方法
        """
        self.host = '127.0.0.1'                 # 默认主机
        self.port = 7382                        # 默认端口

        self.session_path = '.session'          # session 存储路径
        self.route = Route(self)                # 路由装饰器
        self.url_map = {}                       # URL 与 endpoint 的映射
        self.static_map = {}                    # URL 与静态资源的映射
        self.function_map = {}                  # endpoint 与 视图 函数的映射
        self.static_url = '/static'              # 静态资源路由
        self.static_root = 'static'             # 静态资源目录

        self.base_dir = Path('.')

    def add_url_rule(self, url, func, func_type, *, endpoint=None, **options):
        """

        :param url:
        :param func:
        :param func_type:
        :param endpoint:
        :param options:
        :return:
        """
        # 节点默认名为函数名
        if endpoint is None:
            endpoint = func.__name__

        # URL 已存在
        if url in self.url_map:
            raise URLExistsError()

        # endpoint 已存在，且不是静态资源
        if endpoint in self.function_map and func_type != 'static':
            raise EndpointExistsError()

        self.url_map[url] = endpoint
        self.function_map[endpoint] = HandlerFunc(func, func_type, **options)

    def dispatch_request(self, request):
        """
        匹配路由
        :return:
        """
        url: str = urlparse(request.url).path

        # 响应头
        headers = {
            'Server': 'pyearl'
        }

        # 获取cookie
        cookies = request.cookies
        if'session_id' not in cookies:
            headers['Set-Cookie'] = 'session_id={}'.format(create_session_id())

        if url.startswith(self.static_url):
            # 静态资源
            endpoint = 'statis'
            url = url[1:]
        else:
            # 非静态资源的静态路由
            endpoint = self.url_map.get(url, None)

        if endpoint is None:
            return ERROR_MAP['404']

        handler_func: HandlerFunc = self.function_map[endpoint]

        if handler_func.func_type == 'route':
            pass
            # """
            # 路由处理
            # """
            # # 判断请求方法是否支持
            # if request.method in handler_func.options.get('methods'):
            #     """ 路由处理结果 """
            #
            #     # 判断路由的执行函数是否需要请求体进行内部处理
            #     argcount = handler_func.func.__code__.co_argcount
            #
            #     if argcount > 0:
            #         # 需要附带请求体进行结果处理
            #         rep = handler_func.func(request)
            #     else:
            #         # 不需要附带请求体进行结果处理
            #         rep = handler_func.func()
            # else:
            #     """
            #     未知请求方法
            #     """
            #     # 返回 401 错误响应体
            #     return ERROR_MAP['401']
        elif handler_func.func_type == 'view':
            """
            视图处理
            """
            rep =  handler_func.func(request)
        elif handler_func.func_type == 'static':
            """
            静态资源处理
            静态资源的请求统一由 dispatch_static 方法处理
            """
            return handler_func.func(url)
        else:
            """
            未知类型
            """
            return ERROR_MAP['503']

        # 重定向
        if isinstance(rep, Response):
            return rep

        status = 200
        content_type = 'text/html'

        return Response(rep, content_type=f'{content_type}; charset=UTF-8', headers=headers, status=status)

    def dispatch_static(self, static_path):
        """

        :param static_path:
        :return:
        """
        if self.base_dir.exists(static_path):
            file_suffix = PurePath(static_path).suffix
            try:
                doc_type = TYPE_MAP.get(file_suffix[1:], 'text/plain')
            except Exception as e:
                doc_type = 'text/plain'

            with open(static_path, 'rb') as f:
                rep = f.read()

            return Response(rep, content_type=doc_type)
        else:
            return ERROR_MAP['404']

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

        self.function_map['static'] = HandlerFunc(func=self.dispatch_static, func_type='static')

        session.set_storage_path(self.session_path)
        session.load_session_storage()

        run_simple(hostname=self.host, port=self.port, application=self, **options)

    def __call__(self, environ, start_response):
        """

        :param args:
        :param kwargs:
        :return:
        """
        return wsgi_app(self, environ, start_response)


class HandlerFunc:
    def __init__(self, func, func_type, **options):
        self.func = func                    # 处理函数
        self.func_type = func_type          # 函数类型
        self.options = options              # 参数选项


# 定义文件类型
TYPE_MAP = {
    'css':  'text/css',
    'js': 'text/js',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg'
}