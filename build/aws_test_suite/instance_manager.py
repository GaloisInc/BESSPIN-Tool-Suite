class InstanceManager:
    def __init__(self, cap=1, instances=None):
        if instances is None:
            instances = []

        self._cap = cap
        self._instances = instances

    def add_instance(self, ami, name):
        pass

    def terminate_instance(self, name):
        pass
