import json
from pathlib import Path

from werkzeug import Response


class Route:
    """
    路由装饰器
    """
    def __init__(self, app: 'pyearl.core.Pyearl'):
        """

        :param app:
        """
        self.app = app

    def __call__(self, url, **options):
        """

        :param url:
        :param options:
        :return:
        """
        if 'methods' not in options:
            options['methods'] = ['GET']

        def decorator(func):
            self.app.add_url_rule(url, func, 'view', **options)

        return decorator


def redirect(url, status_code=302):
    """

    :param url:
    :param status_code:
    :return:
    """
    response = Response('', status=status_code)
    response.headers['Location'] = url
    return response


def render_json(data):
    """

    :param data:
    :return:
    """
    content_type = 'application/json'

    if isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data)

    return Response(data, content_type=f'{content_type}; charset=UTF-8', status=200)


def render_file(file_path, file_name=None):
    """

    :param file_path:
    :param file_name:
    :return:
    """
    file = Path(file_path)

    if file.exists():
        content = file.read_bytes()
        if file_name is None:
            file_name = file.name

        headers = {
            'Content-Disposition': f'attachment; filename="{file_name}"'
        }

        return Response(content, headers=headers, status=200)

    return ERROR_MAP['404']


# 定义常见服务异常的响应体
ERROR_MAP = {
    '401': Response('<h1>401 Unknown or unsupported method</h1>', content_type='text/html; charset=UTF-8', status=401),
    '404': Response('<h1>404 Source Not Found<h1>', content_type='text/html; charset=UTF-8', status=404),
    '503': Response('<h1>503 Unknown function type</h1>', content_type='text/html; charset=UTF-8',  status=503)
}
