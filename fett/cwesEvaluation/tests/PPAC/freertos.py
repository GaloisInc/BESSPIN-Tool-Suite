"""
FreeRTOS prep for PPAC tests
"""

from fett.base.utils.misc import *
from fett.target.build import prepareFreeRTOSNetworkParameters
from fett.apps.ssl import gen_cert

@decorate.debugWrap
def prepareFreeRTOSforPPAC ():
    # copy extra sources + main FreeRTOS program over
    copyDir(os.path.join(sourcesDir,'libFreeRTOS'),
            os.path.join(getSetting('buildDir'),'lib_PPAC'),
            renameDest=True)
    
    # Needs fettFreeRTOSIPConfig.h
    prepareFreeRTOSNetworkParameters()

    # Certificates
    #[TODO]
    
    # Time fixes
    #[TODO]
    
    # WolfSSL seeds
    #[TODO]