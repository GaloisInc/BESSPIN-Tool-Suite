import cyberphyslib.demonstrator.handler as cpdir
import cyberphyslib.demonstrator.simulator as cpsim
import cyberphyslib.demonstrator.component as ccomp
import cyberphyslib.demonstrator.can as ccan
import cyberphyslib.demonstrator.speedometer as cpspeedo

handler = cpdir.ComponentHandler()
#handler.start_component(cpsim.Sim)
#handler.message_component("beamng", ccomp.Message(cpsim.BeamNgCommand.WAIT_READY), do_receive=True)
print(handler.start_component(ccan.CanMultiverseComponent))

while True:
    pass
