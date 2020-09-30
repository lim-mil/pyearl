class DBResult:
    """
    查询执行结果
    """
    success = False                 # 执行是否成功
    result = None                   # 返回结果
    error = None                    # 异常信息
    rows = 0                        # 影响行数

    def index_of(self, index):
        """

        :param int:
        :return:
        """
        if self.success and isinstance(index, int) and self.rows > index >= -self.rows:
            return self.result[index]
        return None

    def get_first(self):
        """

        :return:
        """
        return self.index_of(0)

    def get_last(self):
        """

        :return:
        """
        return self.index_of(-1)
