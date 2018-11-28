import os
import importlib
from . import default


class UpdateSettings(object):
    """
    用户自定义配置更新默认配置
    """

    def __init__(self):
        # 生成默认配置
        for item in dir(default):

            if item.isupper():
                value = getattr(default, item)
                setattr(self, item, value)

        # 导入用户自定义配置，DEBUG是为了lib库的测试，防止settings配置影响
        if not default.DEBUG:
            setting_path = os.environ.get('CURRENT_SETTINGS')
            md_settings = importlib.import_module(setting_path)
            for item in dir(md_settings):
                if item.isupper():
                    value = getattr(md_settings, item)
                    setattr(self, item, value)


settings = UpdateSettings()
