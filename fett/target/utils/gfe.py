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
            "gdb_port 0",
            # Disable tcl and telnet servers, since they are unused and because
            # the port numbers will conflict if multiple OpenOCD processes are
            # running on the same server.
            "--command",
            "tcl_port disabled",
            "--command",
            "telnet_port disabled",
        ]

        if config:
            try:
                assert os.path.exists(config)
                config_filepath = config
                cmd += ["-f", config_filepath]
            except AssertionError as exc:
                errorAndLog(f"gfe util: unable to find config file {config}", exc=exc)

        if debug:
            cmd.append("-d")

        logfile = ftOpenFile(os.path.join(getSetting('workDir'),'openocd.out'), 'w+')
        env_entries = ("REMOTE_BITBANG_HOST", "REMOTE_BITBANG_PORT")
        env_entries = [key for key in env_entries if key in os.environ]
        logfile.write("+ %s%s\n" % (
            "".join("%s=%s " % (key, os.environ[key]) for key in env_entries),
            " ".join(map(pipes.quote, cmd))))
        logfile.flush()

        self.gdb_ports = []
        self.process = self.start(cmd, logfile)

    def start(self, cmd, logfile):
        cmd_q = [cmd[0]] + [f"'{c}'" if cmd[idx] == '--command' else c for idx, c in enumerate(cmd[1:]) ]
        process = pexpect.spawn(" ".join(cmd_q), encoding='utf-8', logfile=logfile)
        try:
            # Wait for OpenOCD to have made it through riscv_examine(). When
            # using OpenOCD to communicate with a simulator this may take a
            # long time, and gdb will time out when trying to connect if we
            # attempt too early.
            start = time.time()
            messaged = False
            while True:
                line = process.readline()[:-1]
                if not line:
                    time.sleep(0.1)
                    continue

                m = re.search(r"Listening on port (\d+) for gdb connections",
                              line)
                if m:
                    printAndLog(f"OpenOCD found port {int(m.group(1))}", doPrint=False)
                    self.gdb_ports.append(int(m.group(1)))

                if "telnet server disabled" in line:
                    return process

                if not messaged and time.time() - start > 1:
                    messaged = True
                    printAndLog(f"GFE Util: waiting for openOCD to start...", doPrint=False)
                if (time.time() - start) > self.timeout:
                    errorAndLog("GFE Util: Timed out waiting for OpenOCD to listen for gdb")

        except Exception as exc:
            errorAndLog(f"GFE Util: start failed", exc=exc)

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
