class PyearlException(Exception):
    """
    pyearl 的错误基类
    """
    def __init__(self, code: str='', message: str='Error'):
        self.code = code
        self.message = message

    def __str__(self):
        return self.message


class EndpointExistsError(PyearlException):
    """
    endpoint 已经存在
    """
    def __init__(self, message='Endpoint exists'):
        super().__init__(message=message)


class URLExistsError(PyearlException):
    """
    URL 已存在
    """
    def __init__(self, message='URL exists'):
        super().__init__(message=message)


class TemplateSyntaxError(ValueError):
    """Raised when a template has a syntax error."""
    pass