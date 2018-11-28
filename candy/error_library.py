import os
import sys


class _ErrorInfo(object):
    """
    获取错误信息
    """
    @property
    def line(self):     # 获取异常出现的行号
        return self._line()

    @property
    def type(self):     # 获取异常错误类型名称
        return self._type()

    @property
    def path(self):     # 获取异常出现的文件路径
        return self._path()

    @property
    def file(self):     # 获取异常出现的文件名字
        return self._file()

    @staticmethod
    def _path():
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return exc_tb.tb_frame.f_code.co_filename

    @staticmethod
    def _file():
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_path, file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)
        return file_name

    @staticmethod
    def _line():
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return exc_tb.tb_lineno

    @staticmethod
    def _type():
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return exc_type.__name__


ErrorInfo = _ErrorInfo()


class CustomBaseError(Exception):
    """
    自定义错误基类
    """
    def __init__(self, msg="", extend_msg=""):
        if msg and isinstance(msg, str):
            self.message = msg
        else:
            self.message = ""
        self.extend_msg = extend_msg


# settings.py error
class SettingsError(CustomBaseError):
    """
    配置文件错误
    """
    def __str__(self):
        if self.message:
            return repr(self.message)
        else:
            return repr("Error in settings.py.")
