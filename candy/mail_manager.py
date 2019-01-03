#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Mr.chai"
# Date: 2018/4/8
import smtplib
import re
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr

from conf import settings
from .error_library import CustomBaseError, SettingsError


class MailTypeSupportError(CustomBaseError):
    """
    邮箱类型指定错误
    """
    def __str__(self):
        if self.message:
            return repr(self.message)
        else:
            return repr("The E-mail type is not supported.")


class MailAddrMatchError(CustomBaseError):
    """
    邮箱地址指定错误
    """
    def __str__(self):
        if self.message:
            return repr(self.message)
        else:
            return repr("No match to E-mail address.")


class InputParamsError(CustomBaseError):
    """
    传入的参数有误
    """
    def __str__(self):
        if self.message:
            return repr(self.message)
        else:
            return repr("Input params error.")


class SendMail(object):
    """
    发送电子邮件
    """
    def __init__(self, subtype="plain"):
        self.subtype = subtype
        self.msg = None
        self.mail_account = None
        self.mail_password = None
        self.mail_username = None
        self.mail_title = None
        self.to_list = None
        self.hostmail = None  # 邮箱的SMTP服务器

    def send(self, recipients, content, **kwargs):
        """
        发送电子邮件
        :param recipients:邮箱地址，支持格式
            list/tuple：元素为字符串，即认为是单个邮箱地址
                        元素为元组或列表，即长度为1认为是单个邮箱地址，长度为2认为是邮箱地址和用户名
            dict: key为邮箱地址，value为用户名
            即使为空，也会使用settings里的默认配置
        :param content: 内容
        :param kwargs:
            subtype: 邮件内容类型，默认普通内容
            account: 用户帐号
            password: 密码或授权码
            username: 用户名
            header: 标题
        :return:
        """
        self.initialize(recipients, content, kwargs)

        return self.connection()

    def connection(self):
        """
        连接邮件账号帐号
        :return:
        """
        # server = smtplib.SMTP()
        # if hostmail in ["smtp.exmail.qq.com", "smtp.qq.com", "smtp.163.com"]:
        server = smtplib.SMTP_SSL(self.hostmail)

        server.connect(self.hostmail)
        server.set_debuglevel(0)
        server.login(self.mail_account, self.mail_password)
        senderrs = server.sendmail(self.mail_account, self.to_list, self.msg.as_string())
        server.quit()
        return senderrs

    def initialize(self, recipients, content, kwargs):
        """
        邮箱数据初始化
        :param recipients: 邮箱地址，支持格式
        :param content:
        :param kwargs:
            title: 标题
            account: 邮箱账号
            password: 邮箱授权号或密码
            username: 邮箱用户名
        :return:
        """
        # 获取接受者列表和信息
        self.to_list, to_format_addr = self._get_mail_address(recipients)
        if kwargs.get("subtype"):
            self.subtype = kwargs.get("subtype")
        self.mail_title = kwargs.get("title", settings.MAIL_INFO.get("mail_title"))
        self.mail_account = kwargs.get("account", settings.MAIL_INFO.get("mail_account"))

        # 判断发送者是否是支持的邮箱类型
        postfix = kwargs.get("postfix", self.mail_account.split("@")[1])
        self.hostmail = settings.MAIL_HOST.get(postfix)
        if not self.hostmail:
            raise MailTypeSupportError()

        self.mail_password = kwargs.get("password", settings.MAIL_INFO.get("mail_password"))
        self.mail_username = kwargs.get("username", settings.MAIL_INFO.get("mail_username"))
        # 获取发送者信息
        _, from_format_addr = self._get_mail_address({self.mail_account: self.mail_username}, True)

        self.msg = self.msg_create(self.mail_title, content, from_format_addr, to_format_addr)

    def msg_create(self, header, content, from_format_addr, to_format_addr):
        """
        单一，plain类型
        :param header:
        :param content:
        :param from_format_addr:
        :param to_format_addr:
        :return:
        """
        msg = MIMEText(content, _subtype=self.subtype, _charset='utf-8')
        to_address = ";".join(to_format_addr)
        from_address = ";".join(from_format_addr)
        msg['Subject'] = Header(header, 'utf-8').encode()
        msg['From'] = from_address
        msg['To'] = to_address
        return msg

    def _get_mail_address(self, recipients, sender=False):
        """
        获取邮件地址格式
        :param recipients: 邮箱地址，支持格式
        :param sender: True表示发送者，如果是发送者，那么不加载配置文件里的默认的接收者信息
        :return:
        """
        default_recipients = settings.MAIL_INFO.get("mail_recipients")
        to_list = []
        format_list = []
        if isinstance(recipients, (list, tuple)):
            if not sender:
                for addr_settings in default_recipients:
                    if isinstance(addr_settings, (list, tuple)) and len(addr_settings) == 2:
                        recipients.append(addr_settings[0])
                    else:
                        raise SettingsError("Settings MAIL_INFO's mail_recipients error")

            for addr in recipients:
                if isinstance(addr, str):
                    strip_addr = self._email_addr_filter(addr)
                    to_list.append(strip_addr)
                    format_list.append(strip_addr)
                else:
                    raise InputParamsError("E-mail recipient address error: input params")
        elif isinstance(recipients, dict):
            if not sender:
                for addr_settings in default_recipients:
                    if isinstance(addr_settings, (list, tuple)) and len(addr_settings) == 2:
                        recipients[addr_settings[0]] = addr_settings[1]
                    else:
                        raise SettingsError("Settings MAIL_INFO's mail_recipients error")
            for addr, name in recipients.items():
                if isinstance(addr, str) and isinstance(name, str):
                    strip_addr = self._email_addr_filter(addr)
                    to_list.append(strip_addr)
                    addr_str = "%s <%s>" % (str(name), strip_addr)
                    format_addr = self._format_addressee(addr_str)
                    format_list.append(format_addr)
                else:
                    raise InputParamsError("E-mail recipient address error: input params")

        return to_list, format_list

    @staticmethod
    def _email_addr_filter(addr, flag=True):
        """
        过滤邮箱地址
        :param addr: 要检测的邮箱地址
        :param flag: 为True，地址是传入的，False是调用的settings
        :return:
        """
        result = False
        strip_addr = ""
        if isinstance(addr, str):
            re_expr = "[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)" \
                      "*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w -]*[\w])?"
            ret = re.search(re_expr, addr.strip())
            if ret.group() == addr.strip():
                result = True
                strip_addr = addr.strip()
        if not result:
            if flag:
                raise MailAddrMatchError()
            else:
                raise SettingsError("Settings MAIL_INFO's mail_recipients error")
        return strip_addr

    @staticmethod
    def _format_addressee(addressee):
        """
        格式化收件人名字
        :param addressee: 收件人字符串管理员 <xxxx@qq.com>
        :return:
        """
        name, address = parseaddr(addressee)
        return formataddr((Header(name, 'utf-8').encode(), address))


class ReceiveMail(object):
    """
    接收电子邮件
    """
    def __init__(self):
        pass

    def receive(self):
        """
        接收电子邮件
        :return:
        """

    def initialize(self):
        pass


if __name__ == '__main__':
    send_mail_obj = SendMail()
    pass
