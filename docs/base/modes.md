# Modes #

Each mode is already explained in its designated directory's readme, and thus this document will focus on implementation details rather than the functionality or other resources.

## `mode = evaluateSecurityTests` ##

This the mode of running the CWEs evaluation tests. The [CWEs readme](../cwesEvaluation/README.md) has more details about the functionality and the configuration. The tool's flow is as follows:
- `fett.py` loads the configuration and calls `startFett`.
- `startFett` calls `prepareEnv` which:
    - Unix-only: Verify the environment setup, and perform any additional setup or programming it needs to prepare the target for launching.
    - Calls `buildCwesEvaluation` which will collect (or generate if needed) the test sources and other artifacts based on the tests selection and configuration.
- There are two separate flows here based on the OS. FreeRTOS is very special as the kernel is compiled along with the test (or even the test part), so the tool's launch sequence will have to be done for each test part, whereas for Unix OSes, this has to be done only once. Please see [FreeRTOS](#freertos) and [Unix](#unix) below.
- `startFett` returns, and `endFett` is called, which does the following:
    - Unix-only: Shuts down the OS, and tears down all relevant processes.
    - GFE-mode-only: Checks that the scores are valid, i.e., the scores are as expected when the tests run on a baseline non-secure processor.
    - The BESSPIN scale is computed. In case not all of the tests have run, partial categories scores are returned. More details are in the [BESSPIN Scale document](../cwesEvaluation/BESSPIN-Scale.pdf).
- `endFett` returns, and the tool exits.

### FreeRTOS ###

As mentioned above, `prepareEnv` will skip all environment preparation steps, and will just return. `startFett` will thus call `runFreeRTOSCwesEvaluation` and returns directly afterwards. For each test part, `runFreeRTOSCwesEvaluation` will:
- Re-prepare the environment. For example, for Firesim, this will mean removing and re-installing the kernel modules, re-configuring the tap adaptor, and re-flashing the AFI.
- Calls `launchFett`, which will:
    - Builds a FreeRTOS binary with the current test part.
    - Loads the binary and starts the OS.
    - Waits for the test to terminates, or times out (check `FreeRTOStimeout` in [cwesEvaluation/configuration.md](../cwesEvaluation/configuration.md)).
- Tears down the relevant processes.
- Collect any GDB logs if applicable.

Note that for each vulnerability class, the `scoreTests` function will be called before proceeding to the next class. This scores the logs and displays the results table on the screen. 

### Unix ###

- `prepareEnv` will also call `crossCompileUnix` for each vulnerability class to cross-compile any needed C files.
- `startFett` calls `launchFett` which:
    - Boots the OS on the target.
    - The tool sends the tests binaries to the target.
    - The tests are executed and the log files are generated.

Similar to FreeRTOS, for each vulnerability class, the `scoreTests` function will be called before proceeding to the next class. This scores the logs and displays the results table on the screen. 

## `mode = test` ##

The `test` mode is one of the two modes of the bug bounty. The [bug bounty readme](../bugBounty2020/README.md) has more details about the functionality and the configuration. The tool's flow is as follows:
- `fett.py` loads the configuration and calls `startFett`.
- `startFett` calls `prepareEnv` to verify the environment setup, and perform any additional setup or programming it needs to prepare the target for launching.
- `startFett` calls `launchFett` which does the following:
    - Boots the OS on the target.
    - Unix-only: The root password is changed.
    - Unix-only: A non-root user is created.
    - Apps are set and deployment tests are run.
    - Unix-only: The user password is changed and it is given root access (if configured to do so).
- `startFett` returns, and `endFett` is called, which does the following:
    - Unix-only: Collects all relevant kernel logs.
    - Unix-AWS-only: Collect the remote logs that were logged using `rsyslog` on the host.
    - Shuts down the OS, and tears down all relevant processes.
- `endFett` returns, and the tool exits.

## `mode = production` ## 

The `production` mode is one of the two modes of the bug bounty. The [bug bounty readme](../bugBounty2020/README.md) has more details about the functionality and the configuration. The `production` mode works only with the `awsf1` mode. The tool's flow is as follows:
- `fett.py` loads the configuration and calls `startFett`.
- `startFett` calls `prepareEnv` to verify the environment setup, and perform any additional setup or programming it needs to prepare the target for launching.
- `startFett` calls `launchFett` exactly as in the `test` mode described above.
- `startFett` calls `startUartPiping` that pipes the target's TTY to a TCP port.
- `startFett` returns.
- The tool sends an SQS message to the portal to signal successful deployment.
- The tool waits indefinitely for either of the following:
    - Receive a `termination` message (through S3) from the portal [this would continue the normal operation].
    - Receive a `reset` message [See [Reset Button](#reset-button)].
    - The main Firesim/Connectal process seems dead. [See [Dead Process](#dead-process)].
- `endFett` is called, which does the following:
    - Calls `endUartPiping` to get back the control of the TTY.
    - Unix-only: Collects all relevant kernel logs.
    - Unix-only: Collect the remote logs that were logged using `rsyslog` on the host.
    - Shuts down the OS, and tears down all relevant processes.
    - Uploads all the relevant artifacts and collected logs to an S3 bucket.
- `endFett` returns.
- The tool sends an SQS message to the portal to signal successful exit. The portal can thus terminate the host.
- The tool exits.


### Reset Button ###

When `fett.py` receives a `reset` message:
- Calls `resetTarget` which:
    - Calls `endUartPiping` to get back the control of the TTY.
    - Tears down the relevant processes and clears relevant data.
    - Removes and re-installs the kernel modules and re-flashes the FPGA with the AFI.
    - Boots the OS on the target (keep the same disk image and keep settings/credentials).
    - Calls `startUartPiping` to re-pipe the TTY.
- Sends an SQS message to the portal to signal successful reset.
- Go back to the same indefinite loop described above.

### Dead Process ###

When `fett.py` detects that the Firesim/Connectal process is not alive anymore while waiting for portal messages, it will call `endFett` as usual, but skips the kernel logs collection and the proper shutting down. 

When the portal receives the message without sending the termination message, it will know that something went wrong. So it will terminate the host, and report on the researcher's dashboard that the instance is dead. 

### Failures ###

If a failure occurs during any of the steps, the tool exits in an emergency mode during which it collects all the present artifacts, and remote logs (`rsyslog`) if any, then sends an SQS message signaling failure to the protal


## `mode = cyberPhys` ##

The tool's flow is as follows:
- `fett.py` loads the configuration and calls `startCyberPhys` which:
    - For each target, it starts a `startFett` thread that:
        - Calls `prepareEnv` to verify the environment setup, and perform any additional setup or programming it needs to prepare the target for launching.
        - Calls `launchFett` which:
            - Boots the OS on the target.
            - Calls `runCyberPhys` which sets up and starts all the needed application, e.g. infotainment server.
    - Waits for all `startFett` threads to finish.
    - If the interactive shell is enabled, the tool will go to the interactive mode. See [below](#interactive-shell).
    - Waits for all threads to finish.
- When `startCyberPhys` returns, `fett.py` calls `endCyberPhys` which:
    - Runs a thread per target to end TTY piping if it was being piped. And waits for them to finish.
    - Runs an `endFett` thread per target which shuts down the OS and tears down any relevant process. And waits for all of them to finish.
- When `endCyberPhys` returns, the tool exits.

### Interactive Shell ###

The cyberPhys interactive shell responds to the following commands:
- `exit`, `quit`, `Ctrl-d`: exits the shell and shutdown the targets.
- `ip`: displays the IP addresses of the running targets.
- `uart`: displays the ports to which the UART/TTY is piped for the running targets.
- `info`: displays info (`target`, `processor`, `osImage`) about the running targets.
- `pipe [start|stop] TARGET_ID`: starts|stops piping the target.s TTY with the chosen ID.

Also, while the shell is active, a watchdog thread per target periodically:
    - Checks that the main process is still alive.
    - Pings the target.
    - Checks that the running services/applications are still alive.
    - Checks on the heartbeat listener thread that the CAN heartbeat messages are getting proper responses.

Additionally, if `pipeTheUart` setting is enabled, then the main TTY will be piped to a TCP port. Otherwise, this can be altered during the run using `pipe start` as mentioned above.

In case a watchdog detects a problem, and the `resetOnWatchdog` setting is enabled, the non-responding target will reset as follows:
- Stop piping the UART if it was being piped.
- Tear down the relevant processes.
- Re-configure the network configuration if possible, and re-program bitstreams if applicable (and `programBitfileOnReset` is enabled).
- Boots the OS on the target again.
- Start piping the UART if it was configured to be piped.
- Calls `runCyberPhys` to start the needed applications.

If a problem is detected, and `resetOnWatchdog` is not enabled, all targets will be shutdown and the tool will exit; similar to exitting the shell.

## Miscellaneous ##

- The `shutdown` method is where the tool checks for `openConsole` and `gdbDebug`. If either is enabled, the tool will go into the interaction modes prior to shutting down the target.