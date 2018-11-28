import os
PROJECT_PATH = os.path.split(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0])[0]

# True表示测试lib使用，不导入用户settings
DEBUG = False

# 业务相关的开发模式
MODE = "test"

# todo  -------------- Log start --------------
# 配置项目：日志目录名
RUN_LOGS_DIR = "logs"
# 目录路径
RUN_LOGS_PATH = os.path.join(PROJECT_PATH, RUN_LOGS_DIR)
# todo  -------------- Log stop --------------
