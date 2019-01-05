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

#
# import traceback
# from contextlib import contextmanager
#
# from tornado import gen
# from tornado_mysql.cursors import Cursor
# from lib.pub import *
#
#
# @gen.coroutine
# def select_sql(log, db_link, db_name='', table_name='', fields='*',
# condition={}, like_cond={}, or_cond={}, not_cond={},
#                sql_cond='', group='', order={}, run_sql=""):
#     '''
#     查询操作，返回列表格式的数据
#     :param log:         日志记录句柄
#     :param db_link:     数据库连接
#     :param db_name:     库名
#     :param table_name:  表名
#     :param fields:      查询数据的字段
#     :param condition:   操作条件的字典：字段和值
#     :param like_cond:   条件使用like进行匹配的字典：字段和值
#     :param or_cond:     条件使用or进行匹配的字典：字段和值
#     :param not_cond:    条件使用!=进行匹配的字典：字段和值
#     :param sql_cond:    条件的sql语句，示例：id > 3
#     :param order:       排序所用的字典：排序字段和排序方法，desc降序，asc升序
#     :return:            list
#     '''
#     ret = []
#     sql_where = ""
#     try:
#         if run_sql:
#             data_sql = run_sql
#         else:
#             if condition or like_cond or or_cond or sql_cond:
#                 if condition:
#                     for key, val in condition.iteritems():
#                         sql_where += '''%s = '%s' and ''' % (unicode2str(key), str2unicode(val))
#                 if like_cond:
#                     for key, val in like_cond.iteritems():
#                         sql_where += '''%s like '%%%%%s%%%%' and ''' % (unicode2str(key), str2unicode(val))
#                 if not_cond:
#                     for key, val in not_cond.iteritems():
#                         sql_where += '''%s != '%s' and ''' % (unicode2str(key), str2unicode(val))
#                 if sql_cond:
#                     sql_where += sql_cond
#                 sql_where = sql_where.rstrip('and ')
#                 if or_cond:
#                     if sql_where:
#                         sql_where += ''' and ('''
#                     else:
#                         sql_where += '''('''
#                     for key, val in or_cond.iteritems():
#                         sql_where += '''%s = '%s' or ''' % (unicode2str(key), str2unicode(val))
#                     sql_where = sql_where.rstrip('or ')
#                     sql_where += ''')'''
#
#             else:
#                 sql_where = "1=1 "
#             if order:
#                 sql_where += ''' order by '''
#                 for key, val in order.iteritems():
#                     sql_where += '''%s %s, ''' % (unicode2str(key), str2unicode(val))
#                 sql_where = sql_where.rstrip(', ')
#             if group:
#                 sql_where += ''' group by %s''' % group
#                 sql_where = sql_where.rstrip(', ')
#             data_sql = '''SELECT %s FROM %s.%s WHERE %s;''' % (fields, db_name, table_name, sql_where)
#         log.debug('[MySql] select sql : {}'.format(data_sql))
#         cur = yield db_link.execute(data_sql)
#         ret = cur.fetchall()
#         log.debug("[MySql] select result:{}".format(ret))
#         ret = ret or []
#     except Exception, e:
#         log.error('[MySql] err :\n {}'.format(traceback.format_exc()))
#     raise gen.Return(ret)
#
#
# @gen.coroutine
# def select_db_dict(log, db_link, db_name, table_name, fields='*', key='id', condition={}, like_cond={}, order='desc'):
#     '''
#     查询操作，返回字典形式的数据
#     :param log:         日志记录句柄
#     :param db_link:     数据库连接
#     :param db_name:     库名
#     :param table_name:  表名
#     :param fields:      查询数据的字段
#     :param key:         排序字段名称
#     :param condition:   操作条件的字典：字段和值
#     :param like_cond:   条件使用like进行匹配的字典：字段和值
#     :param order:       排序顺序，desc降序，asc升序
#     :return:            dict
#     '''
#     ret = []
#     dict_data = {}
#     sql_where = ""
#     try:
#         if condition or like_cond:
#             if condition:
#                 for key, val in condition.iteritems():
#                     sql_where += '''%s = '%s' and ''' % (unicode2str(key), str2unicode(val))
#             if like_cond:
#                 for key, val in like_cond.iteritems():
#                     sql_where += '''%s like '%%%%%s%%%%' and ''' % (unicode2str(key), str2unicode(val))
#         else:
#             sql_where = "1=1"
#         sql_where = sql_where.rstrip('and ')
#         data_sql = '''SELECT %s FROM %s.%s WHERE %s ORDER BY %s %s;''' % (
#             fields, db_name, table_name, sql_where, key, order)
#         log.debug('select db dict sql : %s' % data_sql)
#         cur = yield db_link.execute(data_sql)
#         ret = cur.fetchall()
#     except Exception, e:
#         log.error('select db dict sql : %s' % e)
#     for row in ret:
#         if row[key] not in dict_data:
#             dict_data[unicode2str(row[key])] = row
#     raise gen.Return(dict_data)
#
#
# @gen.coroutine
# def insert_sql(log, db_link, db_name, table_name, data_info, result_type=1):
#     '''
#     入库操作
#     :param log:          日志记录句柄
#     :param db_link:      数据库连接
#     :param db_name:      库名
#     :param table_name:   表名
#     :param data_info:    字典：字段和值
#     :param result_type:  返回结果类型：默认返回id，1表示返回id，0表示返回行数
#     :return:             int
#     '''
#     ret = 0
#     sql_field = ""
#     sql_value = ""
#     try:
#         if data_info:
#             for key, val in data_info.iteritems():
#                 sql_field += '''%s,''' % unicode2str(key)
#                 sql_value += ''' '%s',''' % str2unicode(val)
#             sql_field = sql_field.strip(',')
#             sql_value = sql_value.strip(',')
#             data_sql = '''INSERT INTO %s.%s (%s) VALUES (%s);''' % (db_name, table_name, sql_field, sql_value)
#             log.info('[MySql] insert sql : %s' % (unicode2str(data_sql)))
#         else:
#             log.warning('[MySql] insert failed: insert data is empty')
#             ret = -1
#         cur = yield db_link.execute(data_sql)
#         ret = cur.rowcount
#         # print dir(cur)
#         # print "-"*80
#         # print cur.rowcount
#         # print cur.rownumber
#         # print cur.lastrowid
#         # print "-"*80
#         if result_type:
#             ret = cur.lastrowid
#     except Exception, e:
#         log.error('[MySql] err:\n {}'.format(traceback.format_exc()))
#         if e and e[0] and e[0] == 1062:
#             ret = -3
#         else:
#             ret = -2
#     log.info("[MySql] insert result:{}".format(ret))
#     raise gen.Return(ret)
#
#
# @gen.coroutine
# def bulk_insert_sql(log, db_link, db_name, table_name, data_fields, data_list, result_type=1):
#     '''
#     批量入库操作
#     :param log:          日志记录句柄
#     :param db_link:      数据库连接
#     :param db_name:      库名
#     :param table_name:   表名
#     :param data_fields:  列表，包含数据库表字段
#     :param data_list:    列表，包含值元组的列表
#     :param result_type:  返回结果类型：默认返回id，1表示返回id，0表示返回行数
#     :return:             int
#     '''
#     ret = 0
#     if data_fields and data_list:
#         sql_field = "({})".format(",".join(data_fields))
#         try:
#             sql_value = ",".join(["({})".format(",".join(["'{}'".format(str(y)) for y in x])) for x in data_list])
#             data_sql = '''INSERT INTO {0}.{1} {2} VALUES {3};'''.format(db_name, table_name, sql_field, sql_value)
#             cur = yield db_link.execute(data_sql)
#             ret = cur.rowcount
#             if result_type:
#                 ret = cur.lastrowid
#             log.info("[MySql] bulk insert sql:{}".format(data_sql))
#         except Exception, e:
#             log.error('[MySql] err :\n {}'.format(traceback.format_exc()))
#             if e and e[0] and e[0] == 1062:
#                 ret = -3
#             else:
#                 ret = -2
#         log.info("[MySql] bulk insert result:{}".format(ret))
#     raise gen.Return(ret)
#
#
# @gen.coroutine
# def update_sql(log, db_link, db_name, table_name, data_info, condition={}, accumulation=[], like_cond={}):
#     '''
#     更新操作
#     :param log:           日志记录句柄
#     :param db_link:       数据库连接
#     :param db_name:       库名
#     :param table_name:    表名
#     :param data_info:     入库更新数据的字典：字段和值
#     :param condition:     操作条件的字典：字段和值
#     :param accumulation:  需要进行累加计算的字段
#     :param like_cond:     条件使用like进行匹配的字典：字段和值
#     :return:              int
#     '''
#     ret = 0
#     data_sql = ""
#     sql_set = ""
#     sql_where = ""
#     try:
#         if data_info and condition:
#             for key, val in data_info.iteritems():
#                 if key in accumulation:
#                     sql_set += '''%s = %s + '%s',''' % (unicode2str(key), unicode2str(key), str2unicode(val))
#                 else:
#                     sql_set += '''%s = '%s',''' % (unicode2str(key), str2unicode(val))
#             for key, val in condition.iteritems():
#                 sql_where += '''%s = '%s' and ''' % (unicode2str(key), str2unicode(val))
#             if like_cond:
#                 for key, val in like_cond.iteritems():
#                     sql_where += '''%s like '%%%%%s%%%%' and ''' % (unicode2str(key), str2unicode(val))
#             sql_set = sql_set.strip(',')
#             sql_where = sql_where.rstrip('and ')
#             data_sql = '''UPDATE %s.%s SET %s WHERE %s;''' % (db_name, table_name, sql_set, sql_where)
#             log.info('[MySql] update sql : {}'.format(unicode2str(data_sql)))
#         else:
#             log.warning('[MySql] update failed: update data:{} or condition:{} is empty'.format(data_info, condition))
#             ret = -1
#         if data_sql:
#             cur = yield db_link.execute(data_sql)
#             ret = cur.rowcount
#     except Exception, e:
#         log.error('[MySql] err : \n{}'.format(traceback.format_exc()))
#         if e and e[0] and e[0] == 1062:
#             ret = -3
#         else:
#             ret = -2
#     log.info('[MySql] update result : {}'.format(ret))
#     raise gen.Return(ret)
#
#
# @gen.coroutine
# def delete_sql(log, db_link, db_name, table_name, id_list, condition, sql_cond=''):
#     '''
#     删除操作
#     :param log:         日志记录句柄
#     :param db_link:     数据库连接
#     :param db_name:     库名
#     :param table_name:  表名
#     :param id_list:     删除条件的列表：值
#     :param condition:   删除条件的字段：字段
#     :param sql_cond:    条件的sql语句，示例：id > 3
#     :return:            int
#     '''
#     ret = 0
#     sql_where = ""
#     try:
#         if id_list:
#             log.info('[%s.%s] delete info: %s' % (db_name, table_name, id_list))
#             if sql_cond:
#                 sql_where += " and " + sql_cond
#             sql_where = sql_where.rstrip('and ')
#
#             ids_str = "({})".format(",".join(id_list))
#
#             # Pools 中只有execute方法
#             data_sql = '''DELETE FROM {}.{} WHERE {} IN {} {};'''.format(
#                 db_name, table_name, condition, ids_str, sql_where)
#             cur = yield db_link.execute(data_sql)
#             ret += cur.rowcount
#
#             log.info('[MySql] delete sql: {}'.format(data_sql))
#         else:
#             log.warning('[MySql] delete failed: delete data is empty')
#             ret = -1
#     except Exception, e:
#         log.error('[MySql] delete err:\n {}'.format(traceback.format_exc()))
#         ret = -2
#     log.info("[MySql] delete sql result:{}".format(ret))
#     raise gen.Return(ret)
#
#
# def jion_sql(log, db_link, db_name, table_name, data_info):
#     '''
#     组合sql语句
#     :param log:         日志记录句柄
#     :param db_link:     数据库连接
#     :param db_name:     库名
#     :param table_name:  表名
#     :param data_info:   字典：字段和值
#     :return:            str
#     '''
#     insert_id = 0
#     sql_field = ""
#     sql_value = ""
#     try:
#         if data_info:
#             for key, val in data_info.iteritems():
#                 sql_field += '''%s,''' % unicode2str(key)
#                 sql_value += ''' '%s',''' % str2unicode(val)
#             sql_field = sql_field.strip(',')
#             sql_value = sql_value.strip(',')
#             data_sql = '''INSERT INTO %s.%s (%s) VALUES (%s);''' % (db_name, table_name, sql_field, sql_value)
#         else:
#             log.error('[%s.%s] jion sql failed: insert data is empty' % (db_name, table_name))
#             return -1
#         return data_sql
#     except Exception, e:
#         log.error('[%s.%s] jion sql failed : %s' % (db_name, table_name, e))
#         return ''
#
#
# @contextmanager
# def open_db_transaction(log, transaction):
#     """
#     执行事务的上下文管理器，可以自动提交或回滚
#     :param log:日志对象
#     :param transaction:事务对象
#     :return:
#     """
#     try:
#         yield transaction
#     except Exception, e:
#         transaction.rollback()
#         log.error('[MySql][Transaction] err:{}'.format(e))
#         log.info('[MySql][Transaction] has rolled back!')
#     else:
#         transaction.commit()
#         log.info('[MySql][Transaction] has committed!')
#
#
# @gen.coroutine
# def select_sql_in_transaction(log, db_transaction, db_name='', table_name='', fields='*', condition={}, like_cond={},
#                               or_cond={}, not_cond={},
#                               sql_cond='', order={}, run_sql=""):
#     '''
#     查询操作，返回列表格式的数据
#     :param log:         日志记录句柄
#     :param db_link:     数据库连接
#     :param db_name:     库名
#     :param table_name:  表名
#     :param fields:      查询数据的字段
#     :param condition:   操作条件的字典：字段和值
#     :param like_cond:   条件使用like进行匹配的字典：字段和值
#     :param or_cond:     条件使用or进行匹配的字典：字段和值
#     :param not_cond:    条件使用!=进行匹配的字典：字段和值
#     :param sql_cond:    条件的sql语句，示例：id > 3
#     :param order:       排序所用的字典：排序字段和排序方法，desc降序，asc升序
#     :return:            list
#     '''
#     ret = []
#     sql_where = ""
#     try:
#         if run_sql:
#             data_sql = run_sql
#         else:
#             if condition or like_cond or or_cond or sql_cond:
#                 if condition:
#                     for key, val in condition.iteritems():
#                         sql_where += '''%s = '%s' and ''' % (unicode2str(key), str2unicode(val))
#                 if like_cond:
#                     for key, val in like_cond.iteritems():
#                         sql_where += '''%s like '%%%%%s%%%%' and ''' % (unicode2str(key), str2unicode(val))
#                 if not_cond:
#                     for key, val in not_cond.iteritems():
#                         sql_where += '''%s != '%s' and ''' % (unicode2str(key), str2unicode(val))
#                 if sql_cond:
#                     sql_where += sql_cond
#                 sql_where = sql_where.rstrip('and ')
#                 if or_cond:
#                     if sql_where:
#                         sql_where += ''' and ('''
#                     else:
#                         sql_where += '''('''
#                     for key, val in or_cond.iteritems():
#                         sql_where += '''%s = '%s' or ''' % (unicode2str(key), str2unicode(val))
#                     sql_where = sql_where.rstrip('or ')
#                     sql_where += ''')'''
#
#             else:
#                 sql_where = "1=1 "
#             if order:
#                 sql_where += ''' order by '''
#                 for key, val in order.iteritems():
#                     sql_where += '''%s %s, ''' % (unicode2str(key), str2unicode(val))
#                 sql_where = sql_where.rstrip(', ')
#             data_sql = '''SELECT %s FROM %s.%s WHERE %s;''' % (fields, db_name, table_name, sql_where)
#         log.debug('[MySql][Transaction] select sql : {}'.format(data_sql))
#         cur = yield db_transaction.execute(data_sql)
#         ret = cur.fetchall()
#         log.debug("[MySql][Transaction] select result:{}".format(ret))
#     except Exception, e:
#         log.error('[MySql][Transaction] select err :\n {}'.format(traceback.format_exc()))
#     raise gen.Return(ret)
#
#
# @gen.coroutine
# def insert_sql_in_transaction(log, db_transaction, db_name, table_name, data_info, result_type=1):
#     '''
#     入库操作
#     :param log:          日志记录句柄
#     :param db_link:      数据库连接
#     :param db_name:      库名
#     :param table_name:   表名
#     :param data_info:    字典：字段和值
#     :param result_type:  返回结果类型：默认返回id，1表示返回id，0表示返回行数
#     :return:             int
#     '''
#     ret = 0
#     sql_field = ""
#     sql_value = ""
#     for key, val in data_info.iteritems():
#         sql_field += '''%s,''' % unicode2str(key)
#         sql_value += ''' '%s',''' % str2unicode(val)
#     sql_field = sql_field.strip(',')
#     sql_value = sql_value.strip(',')
#     data_sql = '''INSERT INTO %s.%s (%s) VALUES (%s);''' % (db_name, table_name, sql_field, sql_value)
#     log.info('[MySql][Transaction] insert sql : {}'.format(unicode2str(data_sql)))
#     cur = yield db_transaction.execute(data_sql)
#     ret = cur.rowcount
#     if result_type:
#         ret = cur.lastrowid
#     log.info("[MySql][Transaction] insert result:{}".format(ret))
#     raise gen.Return(ret)
#
#
# @gen.coroutine
# def update_sql_in_transaction(log, db_transaction, db_name, table_name, data_info, condition={}, accumulation=[],
#                               like_cond={}):
#     '''
#     更新操作
#     :param log:           日志记录句柄
#     :param db_link:       数据库连接
#     :param db_name:       库名
#     :param table_name:    表名
#     :param data_info:     入库更新数据的字典：字段和值
#     :param condition:     操作条件的字典：字段和值
#     :param accumulation:  需要进行累加计算的字段
#     :param like_cond:     条件使用like进行匹配的字典：字段和值
#     :return:              int
#     '''
#     ret = 0
#     data_sql = ""
#     sql_set = ""
#     sql_where = ""
#     for key, val in data_info.iteritems():
#         if key in accumulation:
#             sql_set += '''%s = %s + '%s',''' % (unicode2str(key), unicode2str(key), str2unicode(val))
#         else:
#             sql_set += '''%s = '%s',''' % (unicode2str(key), str2unicode(val))
#     for key, val in condition.iteritems():
#         sql_where += '''%s = '%s' and ''' % (unicode2str(key), str2unicode(val))
#     if like_cond:
#         for key, val in like_cond.iteritems():
#             sql_where += '''%s like '%%%%%s%%%%' and ''' % (unicode2str(key), str2unicode(val))
#     sql_set = sql_set.strip(',')
#     sql_where = sql_where.rstrip('and ')
#     data_sql = '''UPDATE %s.%s SET %s WHERE %s;''' % (db_name, table_name, sql_set, sql_where)
#     log.info('[MySql][Transaction],update sql : {}'.format(data_sql))
#     cur = yield db_transaction.execute(data_sql)
#     ret = cur.rowcount
#     log.info('[MySql][Transaction] update result : {}'.format(ret))
#     raise gen.Return(ret)
#
#
# @gen.coroutine
# def delete_sql_in_transaction(log, db_transaction, db_name, table_name, id_list, condition, sql_cond=''):
#     '''
#     删除操作
#     :param log:         日志记录句柄
#     :param db_link:     数据库连接
#     :param db_name:     库名
#     :param table_name:  表名
#     :param id_list:     删除条件的列表：值
#     :param condition:   删除条件的字段：字段
#     :param sql_cond:    条件的sql语句，示例：id > 3
#     :return:            int
#     '''
#     ret = 0
#     sql_where = ""
#     log.info('[MySql][Transaction] delete, db_name:{},tb_name:{},'
#              'id_list:{},condition:{},sql_cond:{}'.format(db_name, table_name, id_list, condition, sql_cond))
#     if sql_cond:
#         sql_where += " and " + sql_cond
#     sql_where = sql_where.rstrip('and ')
#
#     # Pools 中只有execute方法
#     ids_str = "({})".format(",".join(id_list))
#     data_sql = '''DELETE FROM {}.{} WHERE {} IN {} {};'''.format(
#         db_name, table_name, condition, ids_str, sql_where)
#     cur = yield db_transaction.execute(data_sql)
#     ret += cur.rowcount
#
#     log.info("[MySql][Transaction] delete sql result:{}".format(ret))
#     raise gen.Return(ret)


if __name__ == '__main__':
    pass
