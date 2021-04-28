"""
Project: SSITH CyberPhysical Demonstrator
Name: checkpoint.py
Author: Ethan Lew
Date: 22 April 2021

Checkpoint Management for the SSITH Demonstrator BeamNG Scenario
"""
import os, json, pathlib, time
import numpy as np


class BeamNGRace:
    """data access object of a BeamNG race description"""
    @classmethod
    def for_besspin(cls):
        race_filepath = pathlib.Path(os.path.realpath(__file__)).parent / "utils" / "small_village_airport.race.json"
        return cls.from_json(race_filepath)

    @classmethod
    def from_json(cls, json_fname: str):
        assert os.path.exists(json_fname)
        with open(json_fname, "r") as jf:
            data = json.load(jf)
        return cls(data)

    def __init__(self, race_descr):
        self._rdescr: dict = race_descr

    def __getitem__(self, item: str):
        return self._rdescr.get(item, None)

    @property
    def checkpoints(self):
        return np.array([a['pos'] for a in self._rdescr['pathnodes']])

    @property
    def names(self):
        return [a['name'] for a in self._rdescr['pathnodes']]


class ScenarioCheckpointManager:
    """manage the checkpoint system"""
    @staticmethod
    def get_dist(positions):
        """given a Nx3 array of positions, get the array of distances between them"""
        return np.linalg.norm(
            np.diff(np.array(
                np.vstack(
                    [positions[0],
                     positions]
                )
            ), axis=0),
            axis=1)

    @staticmethod
    def get_cum_dist(positions):
        """given a Nx3 array of positions, get the array of cumulative distances between them"""
        return np.cumsum(ScenarioCheckpointManager.get_dist(positions))

    def __init__(self, time_allowed, positions, max_reasonable_speed = 20.0):
        self.time_allowed = time_allowed
        self.positions = positions

        # normalize cumulative distance relates to percentage of course elapsed
        self.norm_cum_dist = self.get_cum_dist(positions)
        self.max_dist = max(self.norm_cum_dist)
        self.norm_cum_dist /= self.max_dist

        av_travel_speed = self.max_dist / time_allowed
        assert av_travel_speed <= max_reasonable_speed, f"checkpoints require an average speed of {av_travel_speed} m/s "\
                                                       f"which over the max reasonable speed of {max_reasonable_speed} m/s"

        # for timekeeping
        self._init_time = None

    def start(self):
        """start the scenario timer"""
        self._init_time = time.time()

    def get_time_checkpoint(self):
        """return expected checkpoint for time since scenario start"""
        if self._init_time:
            percent_elapsed = (time.time() - self._init_time) / self.time_allowed
            if percent_elapsed > 1.0:
                return self.positions[-1]
            nd = self.norm_cum_dist - percent_elapsed
            nd[nd <= 0.0] = max(nd) + 1.0
            pidx = np.argmin(np.abs(nd))
            return self.positions[pidx]

    def get_offcourse_dist(self, cpos):
        """determine how "off course" the driver currently is"""
        if self._init_time:
            tpos = self.get_time_checkpoint()
            return np.linalg.norm(np.array(cpos) - np.array(tpos))
