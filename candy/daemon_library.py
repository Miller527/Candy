import os
import sys
import atexit
import time
from signal import SIGTERM

import psutil

from .init import settings


class Daemon(object):
    COLOUR_DIC = {
        "red": "\033[31;1m %s \033[0m",
        "green": "\033[32;1m %s \033[0m",
    }

    def __init__(self, pidfile, stdin="/dev/null", stdout="/dev/null", stderr="/dev/null",
                 debug=settings.MODE):
        if debug == "test":
            # 调试信息，改为stdin="/dev/stdin", stdout="/dev/stdout", stderr="/dev/stderr"，以root身份运行。
            self.pidfile = pidfile
            self.stdin = os.path.join(settings.TMP_DIR, "stdin.log")
            self.stdout = os.path.join(settings.TMP_DIR, "stdout.log")
            self.stderr = os.path.join(settings.TMP_DIR, "stderr.log")
        else:
            self.pidfile = pidfile
            self.stdin = stdin
            self.stdout = stdout
            self.stderr = stderr

    def _daemonize(self):
        try:
            pid = os.fork()  # 第一次fork，生成子进程，脱离父进程
            if pid > 0:
                sys.exit(0)  # 退出主进程
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        os.chdir("/")  # 修改工作目录
        os.setsid()  # 设置新的会话连接
        os.umask(0)  # 重新设置文件创建权限

        try:
            pid = os.fork()  # 第二次fork，禁止进程打开终端
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # 重定向文件描述符
        # sys.stdout.flush()
        # sys.stderr.flush()
        si = open(self.stdin, "a+")
        so = open(self.stdout, "a+")
        se = open(self.stderr, "a+")
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # 注册退出函数，根据文件pid判断是否存在进程
        atexit.register(self.del_pid)
        pid = str(os.getpid())
        time_date = int2str(time.time())
        open(self.pidfile, "w+").write("%s_%s\n" % (pid, time_date))

    def del_pid(self):
        os.remove(self.pidfile)

    def start(self):
        pid = self._get_pid()
        if pid:
            message = "pidfile %s already exist. Daemon already running!\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
            # 启动监控
        self._daemonize()
        self.run()

    def status(self):
        # 查看状态
        pid = self._get_pid()
        if pid in psutil.pids():
            msg = self.cmd_line(pid)
            print(self.colour(msg, "green"))
        else:
            print(self.colour(f"Not found process [{pid}]"))
            message = "pidfile %s does not exist. Daemon not running!\n"
            sys.stderr.write(message % self.pidfile)

    @staticmethod
    def cmd_line(pid):
        p = psutil.Process(pid)
        cmd_line = p.cmdline()
        return " ".join(cmd_line) + f" Status:[{p.is_running()}] PID:[{pid}]"

    def monitor(self):
        pid = self._get_pid()
        if pid in psutil.pids():
            msg = self.cmd_line(pid)
            print(self.colour(msg, "green"))
        else:
            self.restart()

    def pid(self):
        pid = self._get_pid()
        if not pid:  # 重启不报错
            print(self.colour("Not found pid"))
            return
        print(pid)

    def _get_pid(self):
        """
        获取文件中存在的进程id
        :return:
        """
        try:
            pf = open(self.pidfile, "r")
            pid = int(pf.read().split("_")[0].strip())
            pf.close()
        except IOError:
            pid = None
        return pid

    def stop(self):
        pid = self._get_pid()
        if not pid:  # 重启不报错
            print(self.colour(f"Not found process [{pid}]"))
            message = "pidfile %s does not exist. Daemon not running!\n"
            sys.stderr.write(message % self.pidfile)
            return
            # 杀进程
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                print(self.colour(f"kill process [{pid}] success", "green"))
            else:
                print(str(err))
                sys.exit(1)

    def restart(self):
        """
        重启进程
        :return:
        """
        self.stop()
        self.start()

    def colour(self, string, col="red"):
        """
        给字段加颜色
        :param string:
        :param col:
        :return:
        """
        fmt_str = self.COLOUR_DIC.get(col, "%s")
        return fmt_str % string

    def run(self):
        """ run your function"""
        # while True:
        #     fp=open("/tmp/result","a+")
        #     fp.write("Hello World\n")
        #     sys.stdout.write("%s:hello world\n" % (time.ctime(),))
        #     sys.stdout.flush()
        #     time.sleep(2)
        pass


if __name__ == "__main__":
    # script_file.replace("py", "pid")
    # pid_dir = os.path.join(script_dir, script_file)
    daemon = Daemon("/tmp/watch_process.pid", stdout="/tmp/watch_stdout.log")
    if len(sys.argv) == 2:
        if hasattr(daemon, sys.argv[1]):
            func = getattr(daemon, sys.argv[1])
        else:
            print("unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
