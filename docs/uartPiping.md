# Using the UART pipe on a remote instance

## Overview

In production, FETT currently pipes the direct UART connection with the FPGA to **TCP port 8278**. Please note that this port is the configurable option `uartFwdPort` in `fett/base/utils/setupEnv.json`.

## Usage manual

The F1 host is listening using the following command:

```
socat STDIO,ignoreeof TCP-LISTEN:8278,reuseaddr,fork,max-children=1
```

To connect, you may use:
```
socat - TCP4:<FPGA-IP>:8278
```

## Networking notes

The port 8278 was chosen arbitrarily (`8278 = UART`). However, to make this piping possible/safer, we chose to do the following:
1. Any outgoing traffic from the FPGA on TCP port 8278 is rejected using an `iptables` rule.
2. Any incoming traffic to `<FPGA-IP>:8278` is redirected to the socat connection listening on the host's main IP.

