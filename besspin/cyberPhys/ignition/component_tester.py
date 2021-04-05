
from cyberphyslib.demonstrator import simulator, speedometer, infotainment, can
from cyberphyslib.demonstrator import component
from cyberphyslib.demonstrator.message import Envelope, MessageLevel, Message
import zmq


class Example(component.Component):
    """example component for testing procedure"""
    def __init__(self):
        super().__init__("example", [(5050, 'example-commands')], [(5052, 'example-events')])
        print("CREATE EXAMPLE")

    @recv_topic("example-commands")
    def _(self, t, msg):
        print("RESET")
        time.sleep(1.0)
        self.send_message(Message("ack"), "example-events")


class ComponentHandler:
    """componentHandler manages ignition components,

    1. create components
    2. connect to components
    3. communicate with components

    TODO: logger
    """
    # map classes to keywords
    keywords = {'beamng': simulator.Sim, 'speedo': None, 'info': None, 'canm': can.CanMultiverseComponent, 'example': Example}

    def __init__(self):
        self._services = {}
        self._command_entry = {}
        self._events_entry = {}
        self._zmq_context = zmq.Context()
        self.name = "SERVICE"

    def connect_component(self, port_input, port_output, component_name):
        """
        TODO: accept component_cls instead of keyword
        """
        out_sock = self._zmq_context.socket(zmq.PUB)
        out_sock.bind(f"tcp://*:{port_output}")

        self._events_entry[component_name] = (port_input, component_name)
        self._command_entry[component_name] = out_sock

    def disconnect_component(self, component_name):
        if component_name in self._events_entry and component_name in self._command_entry:
            v = self._command_entry[component_name]
            v.close()
            del self._command_entry[component_name]
            del self._events_entry[component_name]

    def start_component(self, keyword):
        if keyword not in self.keywords.keys():
            print(f"{keyword} is not in ({set(self._services.keys())}) started services")
            return
        else:
            print(f"Launching Service {keyword}...")
            comp: component.Component = self.keywords[keyword]()
            ctopic, etopic = f"{comp.name}-commands", f"{comp.name}-events"
            porto = {t:p for p, t in comp._in_ports}.get(ctopic, None)
            porti = {t:p for p, t in comp._out_ports}.get(etopic, None)
            self.connect_component(porti, porto, keyword)
            comp.start()
            self._services[keyword] = comp

    def stop_component(self, keyword):
        if keyword not in self._services:
            print(f"{keyword} is not in ({set(self._services.keys())}) started services")
            return
        else:
            print(f"closing down {keyword}...")
            self._services[keyword].exit()
            self._services[keyword].join()
            del self._services[keyword]

    def message_component(self, component_kw, message, do_receive=True):
        # TODO: FIXME: add a timeout
        import threading
        ret = None

        def _recv_ack(sn):
            nonlocal ret
            _ = sn.recv_string()
            recv: bytes = sn.recv_pyobj()
            env: Envelope = Envelope.deserialize(recv)
            mss = env.message
            sn.close()
            ret = mss

        if do_receive:
            porti, topic = self._events_entry[component_kw]
            context = zmq.Context()
            sn = context.socket(zmq.SUB)
            sn.connect(f"tcp://127.0.0.1:{porti}")
            sn.setsockopt_string(zmq.SUBSCRIBE, f"{topic}-events")
            recv = threading.Thread(target=_recv_ack, args=(sn,), daemon=True)
            recv.start()

        self._command_entry[component_kw].send_string(f"{component_kw}-commands", zmq.SNDMORE)
        self._command_entry[component_kw].send_pyobj(Envelope.serialize(Envelope(self,
                                                                                 Message(message),
                                                                                 level=MessageLevel.NORMAL)))
        if do_receive:
            recv.join()
            context.term()
            return ret

    def exit(self):
        for _, v in self._command_entry.items():
            v.close()

        if self._zmq_context is not None:
            self._zmq_context.term()

        # cast to list as _services will change in size
        for name in list(self._services.keys()):
            print("Termination signal received!")
            self.stop_component(name)


if __name__ == "__main__":
    import time
    sg = ComponentHandler()
    sg.start_component("canm")
    sg.message_component("canm", can.CanMultiverseStatus.READY)
    #sg.start_component("example")
    #sg.start_component("beamng")
    #time.sleep(3)
    #sg.message_component("example", "reset")
    #print(sg.message_component("beamng", simulator.BeamNgCommand.WAIT_READY))
    #print(sg.message_component("beamng", simulator.BeamNgCommand.RESTART))
    #simulator.Sim.kill_beamng()
    sg.exit()
