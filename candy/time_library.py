import re
import time
import iso8601
import datetime
from calendar import monthrange

max_point = 200
HOUR = 0
DAY = 1
WEEK = 2
MONTH = 3
SEASON = 4
YEAR = 5
DAY_STEP = 86400
HOUR_STEP = 3600
MINUTE_STEP = 60


def add_time(data_time, days=0, hours=0, minutes=0, seconds=0):
    """
    日期进行加减多少的处理
    :param data_time:  日期
    :param days: 增减的天数
    :param hours: 增减的小时数
    :param minutes: 增减的分钟数
    :param seconds: 增减的秒数
    :return: 返回原格式的日期
    """
    dt = data_time
    try:
        add_sum = days * DAY_STEP + hours * HOUR_STEP + minutes * MINUTE_STEP + seconds
        if isinstance(data_time, (int, float)):
            dt = data_time + add_sum
        elif isinstance(data_time, str):
            dt = int2str(str2int(data_time) + add_sum, fmt=time_format_string(dt))
    except Exception as e:
        print("add_day error : %s" % e)
    return dt


def time_format_string(date_time):
    """
    获取解析的日期格式
    :param date_time:
    :return:
    """
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_time):
        return '%Y-%m-%d'
    elif re.match(r'^\d{4}-\d{2}$', date_time):
        return '%Y-%m'
    elif re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$', date_time):
        return '%Y-%m-%d %H:%M'
    elif re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', date_time):
        return '%Y-%m-%d %H:%M:%S'
    elif re.match(r'^\d{8}$', date_time):
        return '%Y%m%d'
    elif re.match(r'^\d{10}$', date_time):
        return '%Y%m%d%H'
    elif re.match(r'^\d{12}$', date_time):
        return '%Y%m%d%H%M'
    elif re.match(r'^\d{14}$', date_time):
        return '%Y%m%d%H%M%S'
    else:
        raise "Does not recognize the format"


def int2hms(seconds, flag=True):
    """
    秒表格式，最大到小时
    :param seconds:
    :param flag: 保留小数
    :return:
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if flag:
        # 保留小数，2位整数
        return "%02d:%02d:%02d.3f" % (h, m, s)
    else:
        return "%02d:%02d:%02d" % (h, m, s)



def str2full(ts, fmt="T"):
    return ts + fmt + '00:00:00'


def time_interval(st, et=""):
    """
    时间间隔，距离当前多少天，大于24小时才算一天
    :param st:
    :param et:
    :return:
    """
    if not et:
        if isinstance(st, str):
            div = str2int(st) - time.time()
            # print(div, "===============================================")
            return int(div / DAY_STEP)
    else:
        if isinstance(st, str) and isinstance(et, str):
            div = str2int(st) - str2int(et)
            return int(div / DAY_STEP)


def druid_time(start, end, tp="day", res_tp="list"):
    """
    获取druid时间
    :param start: 起始的时间，例：2018-07-01
    :param end: 结束时间，例：2018-07-02
    :param tp: day,按天，hour，按小时
    :param res_tp: list范围，one单一时间

    :return:
    """
    if not isinstance(start, str) and not isinstance(end, str):
        raise "start and end must str"
    else:
        start = str2int(start)
        end = str2int(end)

    if start > end:
        raise "start time must gt end time"

    print(start,end,"+=====")
    if tp == "day":
        step = DAY_STEP
    elif tp == "hour":
        step = HOUR_STEP
    else:
        step = 0

    start_value = start
    if start == end:
        end_value = end + step
    else:
        end_value = end

    if res_tp == "list":
        res = []
        while start_value < end_value:
            s1 = int2iso(start_value)
            start_value += step
            s2 = int2iso(start_value)
            res.append("%s/%s" % (s1, s2))
    elif res_tp == "one":
        s1 = int2iso(start_value)
        s2 = int2iso(end_value)
        res = "%s/%s" % (s1, s2)
    else:
        raise "return type error"
    return res


def day_timestamp(t=None, tp="float"):
    """
    获取当天刚开始的时间戳
    :param t:
    :param tp:
    :return:
    """
    if not t:
        t = time.time()
    if tp == "float":
        return str2int(int2day(t))
    return int(str2int(int2day(t)))


def int2day(value=0, days=0, hours=0, minutes=0, fmt="-"):
    """
    将时间戳改为 日期格式
    """
    fmt_str = fmt.join(["%Y", "%m", "%d"])
    if value:
        value = value + days * DAY_STEP + hours * HOUR_STEP + minutes * MINUTE_STEP
    else:
        value = time.time() + days * DAY_STEP + hours * HOUR_STEP + minutes * MINUTE_STEP
    return time.strftime(fmt_str, time.localtime(value))

def int2hour(value=0, days=0, hours=0, minutes=0, fmt="-"):
    pass

def time_ago(value=0, days=0, hours=0, minutes=0, seconds=0):
    """
    获取多久前的时间戳
    :param value:
    :param days:
    :param hours:
    :param minutes:
    :param seconds:
    :return:
    """
    if value:
        value = value + days * DAY_STEP + hours * HOUR_STEP + minutes * MINUTE_STEP + seconds
    else:
        value = time.time() + days * DAY_STEP + hours * HOUR_STEP + minutes * MINUTE_STEP
    return value


def get_time_gen(start, end, tp="str", unit="day", fmt="-", last=True):
    """
    获取天列表，包括
    :param start:
    :param end:
    :param tp: 类型
    :param unit: day，按天，hour按小时
    :param fmt:
    :param last: 最后一天包含不包含
    :return:
    """
    if unit == "day":
        step = DAY_STEP
    elif unit == "hour":
        step = HOUR_STEP
    else:
        step = 0

    while start <= end:
        if start + step > end and not last:
            break
        if unit == "day":
            yield int2day(start)
        elif unit == "hour":
            yield int2str(start)
        start += step


def get_second(date):
    """
    根据结构化时间、时间字符串、时间戳（小数、字符串、整数）返回时间所在的秒数
    :param date:
    :return:
    """
    second = int(time.strftime("%S", time.localtime(date)))
    return second


def calc_date_difference(first_date, second_date):
    """
    计算日期之差，add Robin 2016-11-01
    :param first_date:  第一个日期
    :param second_date: 第二天日期
    :return:    int，返回两个日期之差
    """
    diff_day = 0
    try:
        if isinstance(first_date, int):
            st = first_date
        elif isinstance(first_date, str):
            st = str2int(first_date)
        if isinstance(second_date, int):
            et = second_date
        elif isinstance(second_date, str):
            et = str2int(second_date)
        diff_day = (et - st) / 86400
        diff_day = abs(diff_day) + 1
    except Exception as e:
        print("calc_date_difference error : %s" % e)
    return diff_day


def add_day(data_time, num=0):
    """
    日期进行加减n天的处理，add Robin 2016-09-27
    :param data_time:   日期
    :param num: 增减的天数
    :return: 返回原格式的日期
    """
    dt = data_time
    try:
        if isinstance(data_time, (int, float)):
            dt = data_time + DAY_STEP * num
        elif isinstance(data_time, str):
            dt = int2day(str2int(data_time) + DAY_STEP * num)
    except Exception as e:
        print("add_day error : %s" % e)
    return dt





def getisotime(z="Z"):
    """
    获取iso8601格式的时间
    :param z: 时间结尾是否带'Z'
    :return: str
    """
    iso_time = datetime.datetime.utcnow().isoformat()
    return iso_time + "Z" if z == "Z" else iso_time


def iso2str(s, h=8, fmt='%Y-%m-%d %H:%M:%S'):
    """
    将iso8601格式的时间格式化
    :param s: iso8601时间，e.g. 2016-05-09T20:38:22.450686Z, 2016-05-09T20:38:22+00:00
    :param h: 正负整数，各地区时间差异的小时数，默认为+8得到中国默认时区
    :param fmt: Y-m-d H:M:S
    :return:    str
    """
    t = iso8601.parse_date(s).strftime('%Y-%m-%d %H:%M:%S')
    ft = int2str(str2int(t) + 3600 * h, fmt)
    return ft


def iso2day(s, h=8):
    """
    将iso8601格式的时间格式化为Y-m-d格式的日期
    :param s: iso8601时间，e.g. 2016-05-09T20:38:22.450686Z, 2016-05-09T20:38:22+00:00
    :param h: 正负整数，各地区时间差异的小时数，默认为+8得到中国默认时区
    :return:    str
    """
    fmt = '%Y-%m-%d %H:%M:%S'
    t = iso8601.parse_date(s).strftime(fmt)

    ft = int2day(str2int(t) + 3600 * h)
    return ft

def iso2hour(s, h=8):
    """
    将iso8601格式的时间格式化为Y-m-d H:00:00格式的日期
    :param s: iso8601时间，e.g. 2016-05-09T20:38:22.450686Z, 2016-05-09T20:38:22+00:00
    :param h: 正负整数，各地区时间差异的小时数，默认为+8得到中国默认时区
    :return:    str
    """
    fmt = '%Y-%m-%d %H:%M:%S'
    t = iso8601.parse_date(s).strftime(fmt)

    ft = int2str(str2int(t) + 3600 * h)
    return ft

def iso2timestamp(s, h=8):
    """
     将iso8601格式的时间转为时间戳
    :param s: iso8601时间，e.g. 2016-05-09T20:38:22.450686Z, 2016-05-09T20:38:22+00:00
    :param h: 正负整数，各地区时间差异的小时数，默认为+8得到中国默认时区
    :return:  int
    """
    return str2int(iso2str(s, h)) if s else 0


def int2iso(v, z='Z', convert_to_utc=True):
    """
    时间戳直接转换为iso时间
    :param v: 时间戳，e.g. 1462948788
    :param z: 时间结尾是否带'Z'
    :param convert_to_utc: 是否转化为utc时间
    :return: str
    """
    t = datetime.datetime.fromtimestamp(v)
    if convert_to_utc:
        t = datetime.datetime.utcfromtimestamp(v)
    return t.isoformat() + ".000Z" if z == "Z" else t.isoformat() + ".000"


def str2iso(s, z='Z', convert_to_utc=True):
    """
    字符串时间转换为iso时间
    :param s: 字符串时间，支持多种字符串形式的日期
    :param z:  时间结尾是否带'Z'
    :param convert_to_utc: 是否转化为utc时间
    :return: str
    """
    return int2iso(str2int(s), z, convert_to_utc)


def datetime2timestamp(dt, h=-8, convert_to_utc=False):
    """
    将datetime转换为iso时间
    :param dt: datetime
    :param h: 正负整数，各地区时间差异的小时数，默认为-8得到中国默认时区
    :param convert_to_utc: 是否转化为utc时间
    :return:
    """
    if isinstance(dt, datetime.datetime):
        if convert_to_utc:
            dt = dt + datetime.timedelta(hours=h)  # 中国默认时区
    return dt.isoformat()


def str2int(s):
    """将常用时间格式字符串转为时间戳，支持时间格式有限
    """
    if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
        return int(time.mktime(time.strptime(s, '%Y-%m-%d')))
    elif re.match(r'^\d{4}-\d{2}$', s):
        return int(time.mktime(time.strptime(s, '%Y-%m')))
    elif re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$', s):
        return int(time.mktime(time.strptime(s, '%Y-%m-%d %H:%M')))
    elif re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', s):
        return int(time.mktime(time.strptime(s, '%Y-%m-%d %H:%M:%S')))
    elif re.match(r'^\d{8}$', s):
        return int(time.mktime(time.strptime(s, '%Y%m%d')))
    elif re.match(r'^\d{10}$', s):
        return int(time.mktime(time.strptime(s, '%Y%m%d%H')))
    elif re.match(r'^\d{12}$', s):
        return int(time.mktime(time.strptime(s, '%Y%m%d%H%M')))
    elif re.match(r'^\d{14}$', s):
        return int(time.mktime(time.strptime(s, '%Y%m%d%H%M%S')))
    else:
        raise "Does not recognize the format"


def utc_datetime2timestamp(utc_s):
    """
    将utc时间字符串转换成时间戳
    :param utc_s: string utc时间字符串
    :return: int
    """
    s = utc_s[:19]
    if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
        ret = int(time.mktime(time.strptime(s, '%Y-%m-%d')))
    elif re.match(r'^\d{4}-\d{2}$', s):
        ret = int(time.mktime(time.strptime(s, '%Y-%m')))
    elif re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$', s):
        ret = int(time.mktime(time.strptime(s, '%Y-%m-%d %H:%M')))
    elif re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', s):
        ret = int(time.mktime(time.strptime(s, '%Y-%m-%d %H:%M:%S')))
    elif re.match(r'^\d{8}$', s):
        ret = int(time.mktime(time.strptime(s, '%Y%m%d')))
    elif re.match(r'^\d{10}$', s):
        ret = int(time.mktime(time.strptime(s, '%Y%m%d%H')))
    elif re.match(r'^\d{12}$', s):
        ret = int(time.mktime(time.strptime(s, '%Y%m%d%H%M')))
    elif re.match(r'^\d{14}$', s):
        ret = int(time.mktime(time.strptime(s, '%Y%m%d%H%M%S')))
    elif re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$', s):
        ret = int(time.mktime(time.strptime(s, '%Y-%m-%dT%H:%M:%S')))
    else:
        raise "Does not recognize the format"
    if ret > 0:
        ret -= time.timezone
    return ret


def int2str(t=None, fmt='%Y-%m-%d %H:%M:%S'):
    """
    将时间戳改为指定格式的字符串
    """
    if not t:
        t = time.time()
    return time.strftime(fmt, time.localtime(t))

# def int2str(t=None, fmt=' '):
#     """
#     将时间戳改为指定格式的字符串
#     """
#     fmt_str = '%Y-%m-%d' + fmt + '%H:%M:%S'
#     if not t:
#         t = time.time()
#     return time.strftime(fmt_str, time.localtime(t))


def int2dayint(value):
    """
    将时间戳改为 日期格式
    """
    format = '%Y%m%d'
    return int(time.strftime(format, time.localtime(value)))


def timestamp_by_step(start_time, end_time, step=86400, check=True, point=max_point, returnType=0,
                      formatStyle="%Y-%m-%d"):
    """
    获取时间列表，增加返回日期字符串形式的时间列表，edit Robin 2017-07-24
    @start_time : 开始时间,时间戳
    @end_time : 结束时间，时间戳
    @step : 时间间隔  单位为秒，整型
    @check : 校验开始时间和结束时间，是否恰好是step的倍数，如果不是，则必须向前或者向后推到step的整数倍时间
    @point : 事件列表的最大元素数量
    return list 时间列表  时间戳
    """
    if isinstance(start_time, str):
        start_time = str2int(start_time)
    if isinstance(end_time, str):
        end_time = str2int(end_time)
    point = point > max_point and max_point or point
    mo = start_time % DAY_STEP
    mo_2 = end_time % DAY_STEP
    if check:
        start_time = start_time - mo
        end_time = end_time - mo_2
        start_more = start_time % step
        start_time = start_time - start_more
        end_more = end_time % step
        if end_more > 0:
            end_time = end_time + (step - end_more)
        start_time = start_time + mo
        end_time = end_time + mo_2
    time_list = []
    for i in range(point):
        if start_time > end_time:
            break
        time_list.append(start_time)
        start_time = start_time + step
    if returnType:
        new_time_list = []
        for i in time_list:
            new_time_list.append(int2str(i, format=formatStyle))
        time_list = new_time_list
    return time_list


def take_time_list(int_start, int_end, setp, flag=True):
    """
    获取时间列表
    @start_time 开始时间的时间戳
    @end_time 结束时间的时间戳
    return  返回年份的时间列表,list中是整型
    """
    list_time = []
    if int_start < int_end:
        int_time = int_start

        while int_time <= int_end:
            list_time.append(int_time)
            int_time += setp
            if not flag and int_time == int_end:
                break
    return list_time


def get_year(value):
    """
    获取年份
    @value:时间戳
    """
    return int(time.strftime('%Y', time.localtime(value)))


def get_month(value):
    """
    获取月份
    @value:时间戳
    """
    return int(time.strftime('%m', time.localtime(value)))


def get_day(value):
    """
    获取日期
    @value:时间戳
    """
    return int(time.strftime('%d', time.localtime(value)))


def get_hour(value):
    """
    获取小时
    @value:时间戳
    """
    return int(time.strftime('%H', time.localtime(value)))


def get_hour_minute(value):
    """
    获取时分
    @value:时间戳
    """
    return time.strftime('%H:%M', time.localtime(value))


def get_year_month(value):
    """
    获取年月
    @value:时间戳
    """
    return time.strftime('%Y-%m', time.localtime(value))


def get_year_month_day(value):
    """
    获取年月
    @value:时间戳
    """
    return time.strftime('%Y-%m-%d', time.localtime(value))


def get_week(value):
    """
    获取value 是周几
    @value:时间戳
    """
    return int(time.strftime('%w', time.localtime(value)))


def get_days(year, month):
    """
    获取某年某月有多少天
    @year:年
    @month:月
    return : 天数
    """
    return monthrange(year, month)[1]


def get_start_timestamp_season(year, season):
    """
    获取某年某个季度的开始时间戳
    @season 1~4
    """
    if season == 1:
        return str2int(str(datetime.date(year, 1, 1)))
    elif season == 2:
        return str2int(str(datetime.date(year, 4, 1)))
    elif season == 3:
        return str2int(str(datetime.date(year, 7, 1)))
    elif season == 4:
        return str2int(str(datetime.date(year, 10, 1)))


def get_start_timestamp(value):
    """
    获取value所在天的0点0分0秒的时间戳
    """
    day = int2day(value)
    return str2int(day)


def same_period_month(value, months=-1):
    """
    获取n前或n月后同期的时间戳，默认上月
    @value 时间戳类型
    return 时间戳
    """
    year = get_year(value)
    month = get_month(value)
    day = get_day(value)

    new_month = year * 12 + month + months
    new_year = new_month // 12
    month = new_month % 12
    if month == 0:
        month = 12
        new_year -= 1
    max_day = get_days(new_year, month)
    day = min(day, max_day)
    date = str(datetime.date(new_year, month, day))
    new_value = int(time.mktime(time.strptime(date, '%Y-%m-%d')))
    return new_value


def get_season_by_int(value):
    """
    获取季度信息
    @value 时间戳
    """
    month = get_month(value)
    season = get_season(month)
    return season


def get_season(month):
    """
    获取季度
    @month : 月份
    """
    if month in (1, 2, 3):
        return 1
    elif month in (4, 5, 6):
        return 2
    elif month in (7, 8, 9):
        return 3
    elif month in (10, 11, 12):
        return 4
    else:
        raise "月份传入错误"


def get_week_list(int_start, int_end):
    list_time = []
    while int_start <= int_end:
        if int(time.strftime('%w', time.localtime(int_start))) == 1:
            # if int_start%7 == 1:
            # str_time = time.strftime('%Y-%m-%d',time.localtime(int_start))
            # list_time.append(str_time)
            list_time.append(int_start)
        int_start += 86400
    return sorted(list_time)


def get_month_list(start_time, end_time=int(time.time()), fmt=''):
    """
    返回start_time 到 end_time之间的月份列表
    @start_time 开始时间，int型
    @end_time 结束时间，int型
    return 月份列表，datetime类型，非时间戳
    """
    month_list = []
    if isinstance(start_time, str):
        start_time = str2int(start_time)
    if isinstance(end_time, str):
        end_time = str2int(end_time)
    start_year = get_year(start_time)
    start_month = get_month(start_time)
    end_year = get_year(end_time)
    end_month = get_month(end_time)
    while True:
        if start_month > 12:
            start_month = 1
            start_year += 1
        if start_year > end_year:
            break
        if start_year == end_year:
            if start_month > end_month:
                break
        date = str(datetime.date(start_year, start_month, 1))
        month_list.append(str2int(date))
        start_month += 1
    if fmt:
        new_month_list = []
        for month in month_list:
            new_month_list.append(time.strftime(fmt, time.localtime(month)))
        month_list = new_month_list
    return month_list


def get_year_list(value, n=5):
    """
    获取年份列表
    @value 传入的时间戳
    @n 前后n年 ，默认为5
    return  返回value前后n前的时间列表,list中是整型
    """
    year = get_year(value)
    year_list = [year]
    before_list = [year - (n - i) for i in range(n)]
    later_list = [year + i + 1 for i in range(n)]
    year_list = before_list + year_list + later_list
    return year_list


def get_yearlist(start_time, end_time):
    """
    获取年份列表 add Robin 2013-09
    @start_time 开始时间的时间戳
    @end_time 结束时间的时间戳
    return  返回年份的时间列表,list中是整型,如[2013,2014]
    """
    s_year = int(time.strftime('%Y', time.localtime(start_time)))
    e_year = int(time.strftime('%Y', time.localtime(end_time)))
    year_list = [s_year]
    try:
        while s_year < e_year:
            year_list.append(s_year + 1)
            s_year += 1
    except Exception as e:
        raise e
    return year_list


def get_last_minute_timestamp():
    """
    获取上一分钟的时间戳,
    """
    now = int(time.time())  # 此时的时间戳
    start_time = now - (now % 60 + 60)
    return start_time


def get_start_end_timestamp(data_time, time_type):
    """
    计算data_time所在时间内的time_type的自然的开始时间，所在周/月/季/年的开始时间，和下一个周期的开始时间
    @time_type:0：小时，1：日 2：周，3：月，4：季，5：年
    @data_time:时间
    return data_time所在季度的开始时间以及下一季度的开始时间
    """
    start_time, end_time = "", ""
    year = get_year(data_time)
    month = get_month(data_time)
    if time_type == HOUR:  # 获取小时开始和结束
        start_time = str2int(int2str(data_time, '%Y-%m-%d %H:00:00'))
        end_time = start_time + HOUR_STEP
    elif time_type == DAY:  # 获取昨天日数据
        start_time = get_start_timestamp(data_time)  # date_time所在日的0点0分0秒
        end_time = start_time + DAY_STEP
    elif time_type == WEEK:  # 获取周数据
        week = get_week(data_time)
        week = week if week > 0 else 7
        start_day = get_start_timestamp(data_time)
        diff_day = week - 1 if week > 0 else 7
        start_time = start_day - diff_day * DAY_STEP
        end_time = start_time + 7 * DAY_STEP
    elif time_type == MONTH:
        start_time = str2int(str(datetime.date(year, month, 1)))  # 本月1日0点
        end_time = same_period_month(start_time, 1)  # 下月同期

    elif time_type == SEASON:
        season = get_season(month)
        start_time = get_start_timestamp_season(year, season)  # 季度开始时间
        end_time = same_period_month(start_time, 3)  # 下季度开始时间，本季度结束时间

    elif time_type == YEAR:
        start_time = str2int(str(datetime.date(year, 1, 1)))  # 年开始时间
        end_time = same_period_month(start_time, 12)  # 下年开始时间，本年结束时间
    return start_time, end_time


def day_begin_timestamp(offset=0):
    """
    计算某一天00:00:00时刻的时间戳，即某一天的开始时间戳
    :param offset: int 指定偏移量，0表示当日的开始时间戳，负数表示向前正数表示向后，比如：-1是昨日，-2昨日的昨日， 1是明日，2明日的明日，依次类推
    :return: int 时间戳
    """
    now_timestamp = time.time() + DAY_STEP * offset
    return str2int(time.strftime("%Y-%m-%d", time.localtime(now_timestamp)))


def get_week_period(start_time, end_time, flag=False):
    """
    计算给定时间范围内的所包括的自然周起始时间区间，add Robin 2016-11-16
    :param start_time: 开始日期
    :param end_time: 结束日期
    :param flag: True表示前开后闭
    :return: set，自然周集合
    """
    week_set = set()
    try:
        if isinstance(start_time, str):
            start_time = str2int(start_time)
        if isinstance(end_time, str):
            end_time = str2int(end_time)
        for dt in take_time_list(start_time, end_time, DAY_STEP, flag=flag):
            ret = get_start_end_timestamp(dt, WEEK)
            week_set.add(ret)
    except Exception as e:
        print("get_week_period error : %s" % e)
    return week_set


def get_month_period(start_time, end_time, flag=False):
    """
    计算给定时间范围内的所包括的自然月起始时间区间，add Robin 2016-11-16
    :param start_time: 开始日期
    :param end_time: 结束日期
    :return: set，自然月集合
    """
    month_set = set()
    # try:
    if isinstance(start_time, str):
        start_time = str2int(start_time)
    if isinstance(end_time, str):
        end_time = str2int(end_time)
    for dt in take_time_list(start_time, end_time, DAY_STEP, flag=flag):
        ret_month = get_start_end_timestamp(dt, MONTH)
        month_set.add(ret_month)
    # except Exception as e:
    #     print("get_month_period error : %s" % e)
    return month_set


def get_week_month_period(start_time, end_time):
    """
    计算给定时间范围内的所包括的自然周起始时间区间和自然月起始时间区间，add Robin 2016-11-16
    :param start_time: 开始日期
    :param end_time: 结束日期
    :return: tuple，自然周集合、自然月集合
    """
    week_set = set()
    month_set = set()
    try:
        if isinstance(start_time, str):
            start_time = str2int(start_time)
        if isinstance(end_time, str):
            end_time = str2int(end_time)
        for dt in take_time_list(start_time, end_time, DAY_STEP):
            ret = get_start_end_timestamp(dt, WEEK)
            ret_month = get_start_end_timestamp(dt, MONTH)
            week_set.add(ret)
            month_set.add(ret_month)
    except Exception as e:
        print("get_week_month_period error : %s" % e)
    return week_set, month_set


def get_current_timestamp_str():
    """
    返回当前时间戳字符串，并去掉小数点
    :return:
    """
    return "".join(str(time.time()).split("."))


if __name__ == '__main__':
    # a, b = get_start_end_timestamp(str2int("2018-06-22"),2)
    # print(int2day(a),int2day(b))
    print(int2hms(time.time()))