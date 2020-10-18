import base64
import json
from pathlib import PurePath, Path
import os.path


class Session:
    """
    单例模式
    """
    __instance = None

    def __init__(self):
        self.__session_map__ = {}
        self.__storage_path__ = None

    def set_storage_path(self, storage_path):
        """

        :param storage_path:
        :return:
        """
        self.__storage_path__ = storage_path
        if not os.path.exists(self.__storage_path__):
            os.mkdir(self.__storage_path__)

    def storage(self, session_id):
        """

        :param session_id:
        :return:
        """
        session_path = PurePath(self.__storage_path__).joinpath(session_id)
        if self.__storage_path__ is not None:
            with open(session_path, 'wb') as f:
                # 序列化
                content = json.dumps(self.__session_map__[session_id])

                # base64 编码再写入，防止有些二进制数据无法写入
                f.write(base64.encodebytes(content.encode('utf-8')))

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance

    def push(self, request, item, value):
        """
        更新或添加
        :param request:
        :param item:
        :param value:
        :return:
        """
        session_id = get_session_id(request)

        if session_id in self.__session_map__:
            self.__session_map__[item] = value
        else:
            self.__session_map__[item] = {item: value}

        # session 发生变化，本地缓存
        self.storage(session_id)

    def pop(self, request, item):
        """
        删除
        :param request:
        :param item:
        :return:
        """
        current_session = self.__session_map__.get(get_session_id(request), {})

        if item in current_session:
            current_session.pop(item)

        self.storage(get_session_id(request))

    def load_session_storage(self):
        """

        :return:
        """
        if self.__storage_path__ is not None:
            session_path_list = Path(self.__storage_path__)
            for session_id in session_path_list.iterdir():
                with open(session_path_list.joinpath(session_id), 'rb') as f:
                    content = f.read()

                # 对文件内容进行解码
                content = base64.decodebytes(content)

                self.__session_map__[session_id] = json.loads(content.decode())

    def map(self, request):
        """

        :param request:
        :return:
        """
        return self.__session_map__.get(get_session_id(request), {})

    def get(self, request, item):
        """

        :param request:
        :param item:
        :return:
        """
        return self.map(request).get(item, None)

# 单例全局对象
session = Session()


def get_session_id(request):
    session_id = request.cookie.get('session_id', '')
    return session_id
