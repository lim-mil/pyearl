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
