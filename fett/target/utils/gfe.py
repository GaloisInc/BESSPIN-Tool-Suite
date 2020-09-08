import shlex
import collections
import pipes

import pexpect
from fett.base.utils.misc import *


class Openocd(object):
    def __init__(self, server_cmd=None, config=None, debug=False, timeout=60):
        self.logname = os.path.join(getSetting('workDir'),'openocd.out')
        self.timeout = timeout

        if server_cmd:
            cmd = shlex.split(server_cmd)
        else:
            openocd = "openocd"
            cmd = [openocd]
            if debug:
                cmd.append("-d")

        # This command needs to come before any config scripts on the command
        # line, since they are executed in order.
        cmd += [
            # Tell OpenOCD to bind gdb to an unused, ephemeral port.
            "--command",
            "'gdb_port 0'",
            # Disable tcl and telnet servers, since they are unused and because
            # the port numbers will conflict if multiple OpenOCD processes are
            # running on the same server.
            "--command",
            "'tcl_port disabled'",
            "--command",
            "'telnet_port disabled'",
        ]

        if config:
            try:
                assert os.path.exists(config)
                config_filepath = config
                cmd += ["-f", config_filepath]
            except AssertionError as exc:
                logAndExit(f"gfe util: unable to find config file {config}", exc=exc)

        if debug:
            cmd.append("-d")

        logfile = ftOpenFile(self.logname, 'a')
        env_entries = ("REMOTE_BITBANG_HOST", "REMOTE_BITBANG_PORT")
        env_entries = [key for key in env_entries if key in os.environ]
        logfile.write("+ %s%s\n" % (
            "".join("%s=%s " % (key, os.environ[key]) for key in env_entries),
            " ".join(map(pipes.quote, cmd))))
        logfile.flush()

        self.gdb_ports = []
        self.process = self.start(cmd, logfile)

    def start(self, cmd, logfile):
        process = pexpect.spawn(" ".join(cmd), encoding='utf-8', logfile=logfile)
        message = ''
        try:
            process.expect("telnet server disabled", timeout=90)
            message = process.before
        except pexpect.TIMEOUT as exc:
            logAndExit("GFE Util: Timed out waiting for OpenOCD to listen for gdb", exc=exc)
        except Exception as exc:
            logAndExit("GFE Util: Error occured while trying to listen for gdb", exc=exc)

        for line in message.split('\n'):
            m = re.search(r"Listening on port (\d+) for gdb connections",
                          line)
            if m:
                printAndLog(f"OpenOCD found port {int(m.group(1))}", doPrint=False)
                self.gdb_ports.append(int(m.group(1)))

        return process

    def tearDown(self):
        def kill_process(proc):
            if (self.process.isalive()):
                try:
                    sudoShellCommand(['kill', '-9', f"{proc.pid}"])
                except Exception as exc:
                    warnAndLog("targetTearDown: Failed to kill process.",doPrint=False,exc=exc)
        try:
            self.process.terminate()
            kill_process(self.process)
        except (OSError, AttributeError):
            pass
