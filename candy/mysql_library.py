#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Miller"
# Date: 2019/01/5

import pymysql
from conf import settings
from lib.error_library import CustomBaseError, ErrorInfo
from lib.log_library import mysql_log_


class InputParamsError(CustomBaseError):
    """
    传入的参数有误
    """
    def __str__(self):
        if self.message:
            return repr(self.message)
        else:
            return repr("Input params error.")


class MySQLLibrary(object):
    """
    MySql数据库框架
    """
    def __init__(self, **kwargs):
        """
        初始化参数
        :param kwargs:
            'host':    数据库地址      string
            'port':    端口号         int
            'user':    用户名         string
            'passwd':  密码           string
            'db':      数据库名       string
            'charset': 字符编码       string
        """
        self._db_config = settings.DB_CONFIG
        self._params_verify(kwargs)

        self._db_obj = None
        self._cursor = None

    def _params_verify(self, kwargs):
        """
        参数检测并更新参数
        :param kwargs:
        :return:
        """
        for k, v in kwargs.items():
            if k in self._db_config.keys():
                if (k == "port" and not isinstance(v, int)) or isinstance(v, str):
                    raise InputParamsError("Input params value error KEY:[%s]")
                self._db_config[k] = v
            else:
                raise InputParamsError("Input params error, not found key [%s]" % str(k))

    def db_initialize(self):
        """
        初始化数据库连接
        :return:
        """
        f_name = "db_initialize"
        try:
            self._db_obj = self.db_connection()
            self._cursor = self._db_obj.cursor()
            mysql_log_.info("StatusCode[107] Database initialize complete...")
        except Exception as e:
            mysql_log_.error(
                'StatusCode[201] Function: ["%s"] ERROR: ["%s"] LINE: ["%s"]' % (f_name, e, ErrorInfo.line))

    def db_connection(self):
        """
        获取数据库连接对象
        :return: 数据库连接对象
        """
        return pymysql.connect(**self._db_config)

    def run(self):
        """
        获取数据, 可重写该字段
        :return:
        """
        f_name = "run"
        try:
            self.db_initialize()
            try:
                self.business()
                self.db_close()
            except Exception as e:
                mysql_log_.error(
                    'StatusCode[201] Function: ["%s"] ERROR: ["%s"] LINE: ["%s"]' % ("business", e, ErrorInfo.line))
                # 事务回滚
                self.db_close(True)
        except Exception as e:
            mysql_log_.error(
                'StatusCode[201] Function: ["%s"] ERROR: ["%s"] LINE: ["%s"]' % (f_name, e, ErrorInfo.line))

    def business(self, *args, **kwargs):
        """
        业务相关
        :return:
        """
        pass

    def select(self, select_sql, *args):
        """
        查询语句，返回数据
        :return:
        """
        if args:
            select_sql = select_sql % tuple(args)
        self._cursor.execute(select_sql)
        result = self._cursor.fetchall()
        return result

    def update(self, update_sql, *args):
        """
        更新语句
        :return:
        """
        if args:
            update_sql = update_sql % tuple(args)
        return self._cursor.execute(update_sql)

    def db_close(self, rollback=False):
        """
        关闭数据库
        :param rollback:
        :return:
        """
        if rollback:
            self._db_obj.rollback()
        else:
            self._db_obj.commit()
        self._cursor.close()
        self._db_obj.close()

    def db_commit(self):
        self._db_obj.commit()

    def insert(self, insert_sql, *args):
        """
        插入语句
        :param insert_sql:
        :param args:
        :return:
        """
        if args:
            insert_sql = insert_sql % tuple(args)
        return self._cursor.execute(insert_sql)

    def sql_joint(self, sql, *args):
        """
        拼接sql
        :param sql:
        :param args:
        :return:
        """
        pass


record_obj = MySQLLibrary()

from interface import IBehaviorLog


class MySQLDB(IBehaviorLog):
    def init(self):
        self.pool = self.kwargs.get("pool")

    async def _select(self, sql, **kwargs):
        async with (await self.pool.acquire()) as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql)
                if kwargs.get("fetchone") is True:
                    r = await cur.fetchone()
                else:
                    r = await cur.fetchall()
            conn.close()
        return r

    async def _execute(self, sql):
        async with (await self.pool.acquire()) as conn:
            async with conn.cursor() as cur:
                res = await cur.execute(sql)
                await conn.commit()
            conn.close()
        return res

    def select(self, sql, *args, **kwargs):

        sql = sql % tuple(args) if args else sql
        return self._select(sql, **kwargs)

    def insert(self, sql, *args):
        sql = self.join_sql(sql, *args)
        res = self._execute(sql)
        return res

    def delete(self, sql, *args):
        sql = self.join_sql(sql, *args)
        res = self._execute(sql)
        return res

    def update(self, sql, *args):
        sql = self.join_sql(sql, *args)
        res = self._execute(sql)
        return res

    async def _transact(self, *args):
        async with (await self.pool.acquire()) as conn:
            async with conn.cursor() as cur:
                status = True
                for sql in args:
                    res = await cur.execute(sql)
                    if not res:
                        status = False
                if status:
                    await conn.commit()
            conn.close()
        return status

    def transact(self, *args):
        if not args:
            return False

        return self._transact(*args)

    @staticmethod
    def join_sql(sql, *args):
        return sql % tuple(args) if args else sql

    def close(self):
        pass

    def write(self, data: dict):
        pass
