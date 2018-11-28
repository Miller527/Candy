import os


def candy_settings(file_path):
    os.environ.setdefault("CURRENT_SETTINGS", file_path)


candy_settings("conf.settings")
