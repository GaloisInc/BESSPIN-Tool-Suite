from fett.base.utils.misc import *
import fett.target.qemu

class qemuTarget(fett.target.qemu.qemuTarget):

    @decorate.debugWrap
    @decorate.timeWrap
    def runApp(self, sendFiles=False, timeout=30): #executes the app
        if not sendFiles:
            self.shutdownAndExit("<runApp>: sendFiles must be True for CWEs "
                                 "evaluation",
                                 exitCode = EXIT.Configuration)
        self.sendTar(timeout=timeout)

        self.interact()

        self.shutdownAndExit(f"<runApp> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Dev_Bug)



