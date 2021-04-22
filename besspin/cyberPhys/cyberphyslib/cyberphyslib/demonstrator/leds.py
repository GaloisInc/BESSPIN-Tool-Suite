"""
Project: SSITH CyberPhysical Demonstrator
leds.py
Author: Kristofer Dobelstein <kris.dobelstein@agilehardwarenwllc.com>, Ethan Lew <elew@galois.com>
Date: 01/18/2021
Python 3.8.3
O/S: Windows 10

objects to generate the required patterns for LED strings on the cyberphysical demonstrator. Defines
a collection of LED patterns, which iteratively evolve the led strings to produces the required
animations. An LED string is abstracted as having a table of possible patterns, an initial pattern,
and state.
"""

import typing as typ
import numpy as np
import abc


class LedPattern(abc.ABC):
    """LedPattern defines a motion sequence for an led string

    A pattern is interpreted as an equation for a discrete time
    (possibly non-autonomous) dynamical system,

        $x_{n+1} = \operatorname{update}(n, x_n)$

    The led colors are the state space, and no output / input spaces
    are involved.

    Time invariant parameters can be created by class initialization,
    and all evolving behavior is captured via the update method

    This object just holds just the transformation information, and no
    state vectors are stored.
    """
    @abc.abstractmethod
    def update(self, dtime: int, state: np.ndarray) -> np.ndarray:
        """given an led string state, produce a new state"""
        raise NotImplementedError


class PulsePattern(LedPattern):
    """produces a uniform pulse"""
    def __init__(self, color: typ.Sequence[float], strength: float,
                 rise_time: int, low_time: int):
        """
        :param color: pulse color
        :param strength: multiplier applied to the pulse signal
        :param rise_time: digital time to go to max value
        :param low_time: digital time to stay off
        """
        self.color = color

        # shape the digital signal
        self._signal = np.array(
            list(range(rise_time)) + list(range(rise_time)[::-1]) +
            [0.0] * low_time)
        self._signal /= max(self._signal)
        self._signal *= strength

    def update(self, dtime: int, state: np.ndarray) -> np.ndarray:
        """non-autonomous pulse (function of digital time)"""
        mult = self._signal[dtime % len(self._signal)]
        return np.tile(np.array(self.color) * mult, (len(state), 1))


class AntsPattern(LedPattern):
    """produces a marching ants pattern"""
    def __init__(self, color: typ.Sequence[int], spacing: int,
                 direction: bool):
        self.color = color
        self.spacing = spacing
        self.direction = direction

    def update(self, dtime: int, state: np.ndarray) -> np.ndarray:
        """
        updates produce a zig zag marching pattern, requiring only
        state to produce the correct pattern. the pattern accepts
        arbitrary initialization, finding the next best pixel based
        on best distance to the initialized color.
        """
        state = np.copy(state)

        # change direction of the ants
        if self.direction:
            state = state[::-1]

        # shift state by one
        new_state = np.vstack(([0.0, 0.0, 0.0], state[:-1]))

        # find distance to peaks
        dists = state - np.tile(self.color, (len(state), 1))
        norms = np.sum(dists**2, axis=1)
        loc = np.argwhere(np.abs(norms) <= 1E-8).flatten()

        # color the new pixel based on distance to desired color peak
        if len(loc) == 0:
            new_pixel = self.color
        else:
            if min(loc) >= self.spacing:
                new_pixel = self.color
            else:
                new_pixel = np.array(
                    self.color) * (self.spacing - min(loc) - 1) / self.spacing

        new_state[0] = new_pixel

        # change direction of the ants
        if self.direction:
            new_state = new_state[::-1]

        return new_state


class ConstantPattern(LedPattern):
    """hold all LEDs at a constant color"""
    def __init__(self, color):
        self.color = color

    def update(self, dtime, state):
        return np.array(np.tile(self.color, (len(state), 1)))


class LedString:
    """ LedStrings models a fixed length string on leds, preset with a collection of patterns
    that can be selected as the time is updated.
    """
    def __init__(self, name: str, patterns: typ.Dict[typ.Hashable, LedPattern],
                 default_pattern: typ.Hashable, length: int):
        self.name = name
        self.length = length
        self._patterns = patterns
        self._active_pattern = self._patterns[default_pattern]
        self.dtime = None
        self.pixel_array = None
        self.reset()

    def reset(self):
        """reset time and turn off the led string"""
        self.pixel_array = np.zeros((self.length, 3))
        self.dtime = 0
        for _ in range(self.length):
            self.update()

    def update(self):
        """advance the led string one unit of time"""
        self.pixel_array = self._active_pattern.update(self.dtime, self.pixel_array)
        self.dtime += 1
        return self.pixel_array

    def update_pattern(self, pattern_name: str) -> None:
        """change the pattern that is being applied to the string"""
        assert pattern_name in self._patterns
        self._active_pattern = self._patterns[pattern_name]
        self.reset()
