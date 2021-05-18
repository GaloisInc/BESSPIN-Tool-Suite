# Configuration of the Cyberphysical Demonstrator Mode #

When `mode` is set to `cyberPhys` in the `functionality` section, the following sections are loaded:    
- `cyberPhys`: The main settings for controlling this mode ([details](#main-mode-settings)).
- `common`: The common settings as explained in [configuration.md](../base/configuration.md). Note that there aren't any users created in this mode, and thus the unix user related settings are ignored.

Additionally, an extra INI file containing the targets settings will be loaded. This is explained below in more details.

## Main Mode Settings

The parameters of this section are:
  - `nTargets`: Number of targets.
  - `interactiveShell`: Opens the cyberPhys interactive shell. If disabled, the tool will launch the targets then shut them down right after.
  - `resetOnWatchdog`: If a target is detected to be unreachable/down, should we reset(`Yes`) or exit(`No`)?
  - `programBitfileOnReset`: For VCU118 targets, if `resetOnWatchdog` is enabled, in case of a reset, should we re-program(`Yes`) the VCU118 bitfile?
  - `pipeTheUart`: In case the `interactiveShell` is enabled, should we pipe the targets' main tty (UART on vcu118) to a TCP port or not. Note that you can pipe selective targets in the interactiveShell after launch using the command `pipe`.
  - `useCustomCyberPhysConfig`: Regarding the additional INI file needed, whether the tool should use a custom file or the default [cyberPhys.ini](../../cyberPhys.ini)?
  - `pathToCustomCyberPhysConfig`: The path to the custom `cyberPhys` configuration in case `useCustomCyberPhysConfig` is enabled.


## The cyberPhys Extra Targets INI File

In the list of the loaded configuration sections, the `target` section was absent. This is because the tool allows each cyberPhys target to have different settings (with some limits). This extra configuration is provided in an extra file. A suitable template can be found in the default file [cyberPhys.ini](../../cyberPhys.ini). It is already populated with an INI `DEFAULT` section, and empty targets section. If `nTargets` is set to `N`, then this file has to have `N` sections from `target1` to `target${N}`. Naturally, any missing setting from the `target${x}` section will be assigned the value from the `DEFAULT` section. The target's settings are explained in [targets.md](../base/targets.md).

It is worth mentioning that some settings are unmixable, i.e. they have to have consistent values across all targets. These settings are: `useCustomTargetIp`, `useCustomHwTarget`, and `vcu118Mode`. Please refer to [base/configuration.md](../base/configuration.md) and [targets.md](../base/targets.md) for more information about these settings.
