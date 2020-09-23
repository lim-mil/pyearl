from werkzeug import Request


def wsgi_app(app, environ, start_response):
    """

    :param app:
    :param environ:
    :param start_response:
    :return:
    """
    # 解析请求头
    request = Request(environ)

    # 响应
    response = app.dispatch_request(request)

    return response(environ, start_response)
