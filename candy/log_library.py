import os
import logging
from logging import handlers

from .init import settings
from candy.error_library import CustomBaseError

M_size = 1024 * 1024  # 计算M的大小


# log_library
class LogSplitRuleError(CustomBaseError):
    """
    日志分割规则错误
    """

    def __str__(self):
        if self.message:
            return repr(self.message)
        else:
            return repr("Error in log file segmentation rules.")


def _get_logger(log_name):
    """
    获取logger对象
    :param log_name:
    :return:
    """
    return logging.getLogger(log_name)


def _init(logger, file_name="", debug=True, log_fmt="", split='time', split_attr='midnight'):
    """
    初始化日志记录模块
    :param file_name: 日志文件名
    :param debug: 指定是否为DEBUG模式
        True: 日志写入文件的同时会输出到终端
        False: 日志只写入文件
    :param log_fmt: 格式化日志内容
    :param split: 日志文件分割规则
        time: 按照时间切分，每天一个文件
        size: 按照文件大小切分，100M一个文件
        :
    :param split_attr:文件切分属性，
                    当split等于time时值可以为'S'每秒一个文件；’M'每分钟一个文件；'H'每小时一个文件；'D'每天一个文件；
                    'midnight'在每天0点创建新文件；'W0'-'W6'每周的某天创建一个文件，0表示周一；
                    当split等于size时值为一个元组，元组的第一个元素表示文件大小（单位M），第二个元素表示保留文件的数量
    :return:
    """
    if isinstance(debug, str):
        debug = True if debug == "test" else False
    if log_fmt:
        fmt = log_fmt
    else:
        fmt = logging.Formatter('%(asctime)s %(levelname)s [%(filename)s %(lineno)d %(funcName)s]  %(message)s')

    if debug:
        logger.setLevel(logging.DEBUG)
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(fmt)
        logger.addHandler(console)
    else:
        logger.setLevel(logging.INFO)
        if split == 'time':
            log_when = split_attr
            file_handler = handlers.TimedRotatingFileHandler(file_name, log_when, interval=1)
        elif split == 'size':
            log_size, log_backup_count = split_attr
            file_handler = handlers.RotatingFileHandler(file_name,
                                                        maxBytes=log_size * M_size,
                                                        backupCount=log_backup_count)
        elif split == "all":
            file_handler = logging.FileHandler(file_name)
        else:
            raise LogSplitRuleError()
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    return logger


def log_init(log_name, split, split_attr):
    """
    生成日志名字
    :param log_name: 日志名字
    :param split: 切割方式
    :param split_attr: 按照大小分割时候，100M一个文件，保留1个
    :return:
    """
    logger = _get_logger(log_name)
    if not os.path.exists(settings.RUN_LOGS_PATH):
        os.mkdir(settings.RUN_LOGS_PATH)
    file_name = "%s.log" % log_name
    log_file = os.path.join(settings.RUN_LOGS_PATH, file_name)
    logger = _init(logger=logger, file_name=log_file, split=split, debug=settings.MODE, split_attr=split_attr)
    return logger


if __name__ == "__main__":
    _alarm_log = log_init(log_name="alarm_log", split="time", split_attr="midnight")
    _mysql_log = log_init(log_name="mysql_log", split="time", split_attr="midnight")
