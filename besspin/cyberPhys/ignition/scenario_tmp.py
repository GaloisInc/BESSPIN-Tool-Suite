from beamngpy import BeamNGpy, Vehicle, Scenario, ScenarioObject, setup_logging
import cyberphyslib.demonstrator.checkpoint as cchk
import cyberphyslib.demonstrator.config as ccfg
import time

race = cchk.BeamNGRace.for_besspin()
check_manage = cchk.ScenarioCheckpointManager(ccfg.SCENARIO_TIMEOUT, race.checkpoints)

# TODO: change home in the sim
with BeamNGpy('localhost', 64256, home=r'C:\BeamNG.tech') as bmng:
    scenario = Scenario('italy', 'SSITH')

    vehicle = Vehicle('ego_vehicle',
                      color='Red',
                      licence="SSITH",
                      **ccfg.BEAMNG_VEHICLE_CONFIG)

    scenario.add_vehicle(vehicle, **ccfg.BEAMNG_ITALY_SPAWNPOINTS[ccfg.BEAMNG_SCENARIO_SPAWNPOINT])

    scenario.make(bmng)
    bmng.load_scenario(scenario)
    bmng.start_scenario()
    vehicle.connect(bmng)
    check_manage.start()

    while True:
        time.sleep(1.0)
        vehicle.poll_sensors()
        location = (tuple(vehicle.state["pos"]), tuple(vehicle.state["dir"]))
        if check_manage.get_offcourse_dist(location[0]) > 100.0:
            print(vehicle, check_manage.get_time_checkpoint())
            bmng.teleport_vehicle(vehicle, list(check_manage.get_time_checkpoint().flatten()))
