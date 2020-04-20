# SSITH-FETT-Target
The target platform for the SSITH FETT bug bounty exercise.


## User Manual ##

To run the tool, use the following:
```
fett.py [-h] [-c CONFIGFILE] [-w WORKINGDIRECTORY] [-l LOGFILE] [-d]
```

The default configuration file is `config.ini`, working directory is `$REPO/workDir`, and log file is `$REPO/$WRKDIR/fett.log`. If you run with the debug (`-d`) flag, the log file will have a lot of useful info.

Some useful configuration options:
- `openConsole`: returns an open console for Unix targets.
- `buildApps`: Cross-compile as instructed in `fett/apps/build.py`.

## Developer Manual ##

- For unix, to cross-compile some files, the tool by default will compile any C file inside
`fett/apps/<appName>/`. To transfer binaries or any other files/folders, follow the next point.
- To control which files to be transferred to target, edit the corresponding function inside `fett/apps/build.py`. You'd have to tar the files into a tar file named `os.path.join(getSetting('buildDir'),getSetting('tarballName'))`, and enable the setting for sending the files: `setSetting('sendTarballToTarget',True)`.
- To execute, modify the function `runApp` inside `fett/apps/<appName>/run.py` to do whatever you want. 
- The most important functiosn provided inside the `target` object which will be given by default to `runApp()`, is `runCommand`, `switchUser`, and `openSshConn` (all of which are defined inside `fett/target/common.py`.
- There are other functions that can help you while coding whether the build or the execute functions for your experiments. These functions are defined inside `fett/base/utils/misc.py`:
    - `printAndLog(message)`
    - `warnAndLog(message)`
    - `errorAndLog(message)`
    - `logAndExit(message,exc=None,exitCode=EXIT.Unspecified)`
    - exitCodes are define in the object `EXIT`.
    - `getSetting(setting)`: returns the value of `setting`.
    - `setSetting(setting,val)`: sets the value of `setting`.
    - `isEnabled(setting)`: returns the value of a boolean `setting`.
    - `isEqSetting(setting,val)`: returns True if the setting's value is equal to `val`.
    - `getSettingDict`: parses a setupEnv dictionary and returns the value.
    - `mkdir(dirPath,addToSettings=None)`: makes a directory `dirPath`. If `addToSettings=STR`, then a setting called STR will be created and equal to this path.
    - `cp(src,dest,pattern=None)`: copy (only files for now). If the `pattern=*.c` for example, it will expand the pattern before copying.
    - `make(argsList,dirPath)`: makese a makefile inside dirPath. The `-C` flag is added in the function, you add any other flags to make.
    - `ftOpenFile(filePath,mode)`: safely opens a file, and stores its handle in the trash can. You should still close it cleanly, but if the error handling is complicated, then don't worry about it, everything in the trash can will be destrooyed upon exit.

- To add a configuration option, you have to update the json dictionary in `fett/base/utils/configData.json`.
- To add/change a system setting, you have to update the json dictionary in `fett/base/utils/setupEnv.json`.