import serial
import serial.tools.list_ports

import shlex
import subprocess
import sys
import tempfile
import collections
import pipes

import pexpect
from fett.base.utils.misc import *


def find_file(path):
    # TODO: move to misc
    for directory in (os.getcwd(), os.path.dirname(__file__)):
        fullpath = os.path.join(directory, path)
        relpath = os.path.relpath(fullpath)
        if len(relpath) >= len(fullpath):
            relpath = fullpath
        if os.path.exists(relpath):
            return relpath
    return None


class Gfe:
    """Collection of functions and state used to interact with the GFE fpga.
    This code can be used to coordinate and control actions over the
    physical interfaces to the GFE"""
    def __init__(
        self,
        gdb_port=getSettingDict("gfeInfo", "gdbPort"),
        gdb_path=getSettingDict("gfeInfo", "gdbPath"),
        openocd_command=getSettingDict("gfeInfo", "openocdCommand"),
        openocd_cfg_path=getSettingDict("gfeInfo", "openocdCfgPath"),
        xlen=32
    ):
        super().__init__()
        self.gdb_port = gdb_port
        self.openocd_command = openocd_command
        self.openocd_cfg_path = openocd_cfg_path
        self.gdb_path = gdb_path
        self.gdb_session = None
        self.openocd_session = None
        self.uart_session = None
        self.xlen = xlen

    # ------------------ GDB/JTAG Functions ------------------

    def startGdb(
        self,
        port=None,
        binary=None,
        server_cmd=None,
        config=None,
        riscv_gdb_cmd=None,
        verbose=False
    ):
        """Start a gdb session with the riscv core on the GFE

        Args:
            port (int, optional): TCP port for GDB connection over openocd
            server_cmd (string, optional): The base openocd command to run
            config (string, optional): Path to the openocd debugger
            configuration riscv_gdb_cmd (string, optional): Base gdb
            command for the riscv gdb program
        """
        if not server_cmd:
            server_cmd = self.openocd_command
        if not config:
            config = self.openocd_cfg_path
        if not riscv_gdb_cmd:
            riscv_gdb_cmd = self.gdb_path
        self.openocd_session = Openocd(
            server_cmd=server_cmd,
            config=config,
            debug=False)
        self.gdb_session = Gdb(
            cmd=riscv_gdb_cmd,
            ports=self.openocd_session.gdb_ports,
            binary=binary,
            xlen=self.xlen)
        self.gdb_session.connect()

    def endGdb(self):
        del self.openocd_session
        del self.gdb_session

    def launchElf(self, binary, gdb_log=False, openocd_log=False, verify=True):
        """Launch a binary on the GFE using GDB
        
        Args:
            binary (string): path to riscv elf file 
            gdb_log (bool, optional): Print the gdb log
                if the gdb commands raise an exception
            openocd_log (bool, optional): Print openocd log
                if the openocd command raise an exception
        """

        if not self.gdb_session:
            self.startGdb()
        gdblog = open(self.gdb_session.logfiles[0].name, 'r')
        openocdlog = open(self.openocd_session.logfile.name, 'r')
        binary = os.path.abspath(binary)
        try:
            self.gdb_session.command("file {}".format(binary))
            self.gdb_session.load(verify)
            self.gdb_session.c(wait=False)
        except Exception as e:
            if gdb_log:
                print("------- GDB Log -------")
                print(gdblog.read())
            if openocd_log:
                print("------- OpenOCD Log -------")
                print(openocdlog.read())
            openocdlog.close()
            gdblog.close()
            raise e


    def runElfTest(
        self, binary, gdb_log=False, openocd_log=False, runtime=0.5,
        tohost=0x80001000):
        """Run a binary test on the GFE using GDB.
        
        Args:
            binary (string): path to riscv elf file 
            gdb_log (bool, optional): Print the gdb log
                if the gdb commands raise an exception
            openocd_log (bool, optional): Print openocd log
                if the openocd command raise an exception
            runtime (float, optional): Time (seconds) to wait while
                the test to run
            tohost (int, optional): Memory address to check for
                the passing condition at the end of the test.
                A "0x1" written to this address indicates the test passed
        
        Returns:
            (passed, msg) (bool, string): passed is true if the test passed 
                msg that can be printed to further describe the passing or 
                failure condition
        
        Raises:
            e: Exception from gdb or openocd if an error occurs (i.e. no riscv detected)
        """
        
        self.launchElf(binary=binary, gdb_log=gdb_log, openocd_log=openocd_log)
        time.sleep(runtime)
        self.gdb_session.interrupt()
        tohost_val = self.riscvRead32(tohost)
        msg = ""

        # Check if the test passed
        if tohost_val == 1:
            msg = "passed"
            passed = True
        elif tohost_val == 0:
            msg = "did not complete. tohost value = 0"
            passed = False
        else:
            msg = "failed"
            passed = False

        return (passed, msg)

    def getGdbLog(self):
        if self.gdb_session:
            with open(self.gdb_session.logfiles[0].name, 'r') as gdblog:
                data = gdblog.read()
            return data
        else:
            return "No gdb_session open."

    def riscvRead32(self, address, verbose=False, dbg_txt=""):
        """Read 32 bits from memory using the riscv core

        Args:
            address (int): Memory address

        Returns:
            int: Value at the address
        """
        if not self.gdb_session:
            self.startGdb()

        value = self.gdb_session.x(address=address, size="1w")

        if verbose:
            print("{} Read: {} from {}".format(dbg_txt, hex(value), hex(address)))

        return value

    def riscvWrite(self, address, value, size, verbose=False, dbg_txt=""):
        """Use GDB to perform a write with the synchronous riscv core

        Args:
            address (int): Write address
            value (int): Write value
            size (int): Write data size in bits (8, 32, or 64 bits)

        Raises:
            Exception: Invalid write size
        """

        size_options = {8: "char", 32: "int"}

        # Validate input
        if size not in size_options:
            raise Exception(
                "Write size {} must be one of {}".format(
                    size, list(size_options.keys())))

        if not self.gdb_session:
            self.startGdb()

        # Perform the write command using the gdb set command
        output = self.gdb_session.command(
            "set *(({} *) 0x{:x}) = 0x{:x}".format(
                size_options[size], address, value))

        if verbose:
            print("{} Write: {} to {}".format(dbg_txt, hex(value), hex(address)))

        # Check for an error message from gdb
        m = re.search("Cannot access memory", output)
        if m:
            raise CannotAccess(address)

    def riscvWrite32(self, address, value, verbose=False, dbg_txt=""):
        self.riscvWrite(address, value, 32, verbose=verbose, dbg_txt=dbg_txt)

    def softReset(self):
        print("Performing a soft reset of the GFE...")
        self.riscvWrite32(int(getSettingDict("gfeInfo", "resetBase"), base=16),
                          int(getSettingDict("gfeInfo", "resetVal"), base=16))
        self.endGdb()
        self.startGdb()
        # Note: There is a bug that prevents loading an elf later in the test script
        # without first continuing and interrupting. This is fine for now, but may
        # not be compatible with future tests that require a completely clean start point
        self.gdb_session.c(wait=False)
        self.gdb_session.interrupt()

    # ------------------ UART Functions ------------------
    def findUartPort(
        self,
        search_vid=0x10C4,
        search_pid=0xEA70,
        port_num=1):

        # Get a list of all serial ports with the desired VID/PID
        ports = [port for port in serial.tools.list_ports.comports() if port.vid == search_vid and port.pid == search_pid]

        for port in ports:
            #print "Checking port: %s" % port.hwid
            # Silabs chip on VCU118 has two ports. Locate port 1 from the hardware description
            m = re.search('LOCATION=.*:1.(\d)', port.hwid)
            if m:
                if m.group(1) == '1':
                    print("Located UART device at %s with serial number %s" % (port.device, port.serial_number))
                    extraMsg = "In case there is no output shown from the target's UART, "
                    extraMsg += "please make sure the tty is not used by any other tool (e.g. minicom), "
                    extraMsg += f"and is reset properly (use 'stty -F {port.device} min 0 time 0' to reset it)."
                    try:
                        #Check if no one else is using the serial port. Especially Minicom.
                        sttyOut = str(subprocess.check_output (f"stty -F {port.device} | grep min",stderr=subprocess.STDOUT,shell=True),'utf-8')
                        sttyMatch = re.match(r"^.*min = (?P<vMin>\d+); time = (?P<vTime>\d+);$", sttyOut)
                        if ( (int(sttyMatch.group('vMin')) != 0) or (int(sttyMatch.group('vTime')) != 0)):
                            print (f"Warning: The UART {port.device} status is not as expected. {extraMsg}")
                    except:
                        print (f"Warning: Failed to get the status of {port.device}. {extraMsg}")
                    return port.device
        raise Exception(
                "Could not find a UART port with expected VID:PID = %X:%X" % (search_vid, search_pid))

    def setupUart(
        self,
        timeout=None, # wait forever on read data
        port=getSettingDict("gfeInfo", "uartSerialDev"),
        baud=9600,
        parity="ODD",
        stopbits=2,
        bytesize=8):

        # Get the UART port
        if port == "auto":
            port = self.findUartPort()

        # Translate inputs into serial settings
        if parity.lower() == "odd":
            parity = serial.PARITY_ODD
        elif parity.lower() == "even":
            parity = serial.PARITY_EVEN
        elif parity.lower() == "none" or parity == None:
            parity = serial.PARITY_NONE
        else:
            raise Exception(
                "Parity {} must be even or odd".format(parity))

        if stopbits == 1:
            stopbits = serial.STOPBITS_ONE
        elif stopbits ==2:
            stopbits = serial.STOPBITS_TWO
        else:
            raise Exception(
                "Stop bits {} must be 1 or 2".format(stopbits))

        if bytesize == 5:
            bytesize = serial.FIVEBITS
        elif bytesize == 6:
            bytesize = serial.SIXBITS
        elif bytesize == 7:
            bytesize = serial.SEVENBITS
        elif bytesize == 8:
            bytesize = serial.EIGHTBITS
        else:
            raise Exception(
                "bytesize {} must be 5,6,7 or 8".format(bytesize))           

        # configure the serial connections 
        self.uart_session = serial.Serial(
            port=port,
            baudrate=baud,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout,
            bytesize=bytesize
        )

        if not self.uart_session.is_open:
            self.uart_session.open()


class Openocd(object):
    logfile = tempfile.NamedTemporaryFile(prefix='openocd', suffix='.log')
    logname = logfile.name

    def __init__(self, server_cmd=None, config=None, debug=False, timeout=60):
        self.timeout = timeout

        if server_cmd:
            cmd = shlex.split(server_cmd)
        else:
            openocd = os.path.expandvars("$RISCV/bin/openocd")
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
            f = find_file(config)
            if f is None:
                print("Unable to read file " + config)
                exit(1)

            cmd += ["-f", f]
        if debug:
            cmd.append("-d")

        logfile = open(Openocd.logname, "w")
        env_entries = ("REMOTE_BITBANG_HOST", "REMOTE_BITBANG_PORT")
        env_entries = [key for key in env_entries if key in os.environ]
        logfile.write("+ %s%s\n" % (
            "".join("%s=%s " % (key, os.environ[key]) for key in env_entries),
            " ".join(map(pipes.quote, cmd))))
        logfile.flush()

        self.gdb_ports = []
        self.process = self.start(cmd, logfile)

    def start(self, cmd, logfile):
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                   stdout=logfile, stderr=logfile)

        try:
            # Wait for OpenOCD to have made it through riscv_examine(). When
            # using OpenOCD to communicate with a simulator this may take a
            # long time, and gdb will time out when trying to connect if we
            # attempt too early.
            start = time.time()
            messaged = False
            fd = open(Openocd.logname, "r")
            while True:
                line = fd.readline()
                if not line:
                    if not process.poll() is None:
                        raise Exception("OpenOCD exited early.")
                    time.sleep(0.1)
                    continue

                m = re.search(r"Listening on port (\d+) for gdb connections",
                              line)
                if m:
                    self.gdb_ports.append(int(m.group(1)))

                if "telnet server disabled" in line:
                    return process

                if not messaged and time.time() - start > 1:
                    messaged = True
                    print("Waiting for OpenOCD to start...")
                if (time.time() - start) > self.timeout:
                    raise Exception("Timed out waiting for OpenOCD to "
                                    "listen for gdb")

        except Exception:
            raise

    def __del__(self):
        try:
            self.process.terminate()
            start = time.time()
            while time.time() < start + 10000:
                if self.process.poll():
                    break
            else:
                self.process.kill()
            self.process.wait()
        except (OSError, AttributeError):
            pass


class CannotAccess(Exception):
    def __init__(self, address):
        Exception.__init__(self)
        self.address = address


class CouldNotFetch(Exception):
    def __init__(self, regname, explanation):
        Exception.__init__(self)
        self.regname = regname
        self.explanation = explanation


Thread = collections.namedtuple('Thread', ('id', 'description', 'target_id',
                                           'name', 'frame'))


class Gdb(object):
    """A single gdb class which can interact with one or more gdb instances."""

    # pylint: disable=too-many-public-methods
    # pylint: disable=too-many-instance-attributes

    def __init__(self, ports,
                 cmd=os.path.expandvars("$RISCV/bin/riscv64-unknown-elf-gdb"),
                 timeout=60, binary=None, xlen=32):
        assert ports

        self.ports = ports
        self.cmd = cmd
        self.timeout = timeout
        self.binary = binary
        self.xlen = xlen

        self.stack = []
        self.harts = {}

        self.logfiles = []
        self.children = []
        for port in ports:
            logfile = tempfile.NamedTemporaryFile(prefix="gdb@%d-" % port,
                                                  suffix=".log", mode='w+', encoding='utf-8')
            self.logfiles.append(logfile)
            child = pexpect.spawn(cmd, encoding='utf-8')
            child.logfile = logfile
            child.logfile.write("+ %s\n" % cmd)
            self.children.append(child)
        self.active_child = self.children[0]

    def connect(self):
        for port, child in zip(self.ports, self.children):
            print("Connecting on {}".format(port))
            self.select_child(child)
            self.wait()
            self.command("set confirm off")
            self.command("set width 0")
            self.command("set height 0")
            # Force consistency.
            self.command("set print entry-values no")
            self.command("set remotetimeout %d" % self.timeout)
            self.command("set architecture riscv:rv%d" % self.xlen)
            self.command("target extended-remote localhost:%d" % port)
            if self.binary:
                self.command("file %s" % self.binary)
            threads = self.threads()
            for t in threads:
                hartid = None
                if t.name:
                    m = re.search(r"Hart (\d+)", t.name)
                    if m:
                        hartid = int(m.group(1))
                if hartid is None:
                    if self.harts:
                        hartid = max(self.harts) + 1
                    else:
                        hartid = 0
                # solo: True iff this is the only thread on this child
                self.harts[hartid] = {'child': child,
                                      'thread': t,
                                      'solo': len(threads) == 1}

    def __del__(self):
        for child in self.children:
            del child

    def one_hart_per_gdb(self):
        return all(h['solo'] for h in self.harts.values())

    def lognames(self):
        return [logfile.name for logfile in self.logfiles]

    def select_child(self, child):
        self.active_child = child

    def select_hart(self, hart):
        h = self.harts[hart.id]
        self.select_child(h['child'])
        if not h['solo']:
            output = self.command("thread %s" % h['thread'].id, ops=5)
            assert "Unknown" not in output

    def push_state(self):
        self.stack.append({
            'active_child': self.active_child
        })

    def pop_state(self):
        state = self.stack.pop()
        self.active_child = state['active_child']

    def wait(self):
        """Wait for prompt."""
        self.active_child.expect(r"\(gdb\)")

    def command(self, command, ops=1):
        """ops is the estimated number of operations gdb will have to perform
        to perform this command. It is used to compute a timeout based on
        self.timeout."""
        timeout = ops * self.timeout
        self.active_child.sendline(command)
        self.active_child.expect("\n", timeout=timeout)
        self.active_child.expect(r"\(gdb\)", timeout=timeout)
        return self.active_child.before.strip()

    def global_command(self, command):
        """Execute this command on every gdb that we control."""
        with PrivateState(self):
            for child in self.children:
                self.select_child(child)
                self.command(command)

    def c(self, wait=True, asynch=False):
        """
        Dumb c command.
        In RTOS mode, gdb will resume all harts.
        In multi-gdb mode, this command will just go to the current gdb, so
        will only resume one hart.
        """
        if asynch:
            asynch = "&"
        else:
            asynch = ""
        ops = 10
        if wait:
            output = self.command("c" + asynch, ops=ops)
            assert "Continuing" in output
            return output
        else:
            self.active_child.sendline("c" + asynch)
            self.active_child.expect("Continuing", timeout=ops * self.timeout)

    def c_all(self, wait=True):
        """
        Resume every hart.

        This function works fine when using multiple gdb sessions, but the
        caller must be careful when using it nonetheless. gdb's behavior is to
        not set breakpoints until just before the hart is resumed, and then
        clears them as soon as the hart halts. That means that you can't set
        one software breakpoint, and expect multiple harts to hit it. It's
        possible that the first hart completes set/run/halt/clear before the
        second hart even gets to resume, so it will never hit the breakpoint.
        """
        with PrivateState(self):
            for child in self.children:
                child.sendline("c")
                child.expect("Continuing")

            if wait:
                for child in self.children:
                    child.expect(r"\(gdb\)")

    def interrupt(self):
        self.active_child.send("\003")
        self.active_child.expect(r"\(gdb\)", timeout=6000)
        return self.active_child.before.strip()

    def interrupt_all(self):
        for child in self.children:
            self.select_child(child)
            self.interrupt()

    def x(self, address, size='w'):
        output = self.command("x/%s %s" % (size, address))
        value = int(output.split(':')[1].strip(), 0)
        return value

    def p_raw(self, obj):
        output = self.command("p %s" % obj)
        m = re.search("Cannot access memory at address (0x[0-9a-f]+)", output)
        if m:
            raise CannotAccess(int(m.group(1), 0))
        return output.split('=')[-1].strip()

    def parse_string(self, text):
        text = text.strip()
        if text.startswith("{") and text.endswith("}"):
            inner = text[1:-1]
            return [self.parse_string(t) for t in inner.split(", ")]
        elif text.startswith('"') and text.endswith('"'):
            return text[1:-1]
        else:
            return int(text, 0)

    def p(self, obj, fmt="/x"):
        output = self.command("p%s %s" % (fmt, obj))
        m = re.search("Cannot access memory at address (0x[0-9a-f]+)", output)
        if m:
            raise CannotAccess(int(m.group(1), 0))
        m = re.search(r"Could not fetch register \"(\w+)\"; (.*)$", output)
        if m:
            raise CouldNotFetch(m.group(1), m.group(2))
        rhs = output.split('=')[-1]
        return self.parse_string(rhs)

    def p_string(self, obj):
        output = self.command("p %s" % obj)
        value = shlex.split(output.split('=')[-1].strip())[1]
        return value

    def info_registers(self, group):
        output = self.command("info registers %s" % group)
        result = {}
        for line in output.splitlines():
            parts = line.split()
            name = parts[0]
            if "Could not fetch" in line:
                result[name] = " ".join(parts[1:])
            else:
                result[name] = int(parts[1], 0)
        return result

    def stepi(self):
        output = self.command("stepi", ops=10)
        return output

    def load(self, verify=True):
        output = self.command("load", ops=1000)
        assert "failed" not in  output
        assert "Transfer rate" in output
        if verify:
            output = self.command("compare-sections", ops=1000)
            assert "MIS" not in output

    def b(self, location):
        output = self.command("b %s" % location, ops=5)
        assert "not defined" not in output
        assert "Breakpoint" in output
        return output

    def hbreak(self, location):
        output = self.command("hbreak %s" % location, ops=5)
        assert "not defined" not in output
        assert "Hardware assisted breakpoint" in output
        return output

    def threads(self):
        output = self.command("info threads", ops=100)
        threads = []
        for line in output.splitlines():
            m = re.match(
                r"[\s\*]*(\d+)\s*"
                r"(Remote target|Thread (\d+)\s*\(Name: ([^\)]+))"
                r"\s*(.*)", line)
            if m:
                threads.append(Thread(*m.groups()))
        #assert threads
        #>>>if not threads:
        #>>>    threads.append(Thread('1', '1', 'Default', '???'))
        return threads

    def thread(self, thread):
        return self.command("thread %s" % thread.id)

    def where(self):
        return self.command("where 1")

class PrivateState(object):
    def __init__(self, gdb):
        self.gdb = gdb

    def __enter__(self):
        self.gdb.push_state()

    def __exit__(self, _type, _value, _traceback):
        self.gdb.pop_state()

