import cyberphyslib.demonstrator.handler as cphand
import cyberphyslib.demonstrator.director as cpdir
import cyberphyslib.demonstrator.simulator as cpsim
import cyberphyslib.demonstrator.component as ccomp
import cyberphyslib.demonstrator.can as ccan
import cyberphyslib.demonstrator.speedometer as cpspeedo


dir = cpdir.IgnitionDirector()

#handler = cphand.ComponentHandler()
#handler.start_component(cpspeedo.Speedo)
#handler.start_component(cpsim.Sim)
#handler.message_component("beamng", ccomp.Message(cpsim.BeamNgCommand.WAIT_READY), do_receive=True)
#print(handler.start_component(ccan.CanMultiverseComponent))

#c = cpsim.Sim()
#c.start()
while True:
    pass