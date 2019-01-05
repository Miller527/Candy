#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Miller"
# Date: 2018/12/11

import abc


class IBehaviorLog(metaclass=abc.ABCMeta):
    """日志对象接口"""
    __instance = None
    __init_flag = False

    def __new__(cls,*args,**kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            return cls.__instance
        else:
            return cls.__instance

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.init()
    @classmethod
    def clear(cls):
        cls.__instance = None
        cls.__init_flag = False
    @abc.abstractmethod
    async def init(self):
        """连接对象、配置对象信息等"""
        pass

    @abc.abstractmethod
    def write(self, data: dict):
        """写数据"""
        pass

    @abc.abstractmethod
    def close(self):
        """断开连接清理内存"""
        pass


