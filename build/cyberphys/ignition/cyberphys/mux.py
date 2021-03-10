"""
Project: SSITH CyberPhysical Demonstrator
Name: mux.py
Author: Steven Osborn, Ethan Lew <elew@galois.com>
Date: 24 August 2020

Cyberphys Demonstrator Button (security mux replacement for testing)
"""
import typing as typ
import logging
import logging.config
import keyboard


class CallbackButton:
    """
    CallbackButton registers callback functions to keystrokes. This use is limited to creating
    interactive tests modes for the cyberphys demonstrators, or hardware devices that operate by
    sending keystrokes. It stores internal states (as int) and an toggle method that updates the
    internal state, as well as call the appropriate action.
    """
    def __init__(self, callback: typ.Union[None, typ.Callable]=None,
                 nstates: int = 2,
                 keystroke: str="ctrl+f7"):
        """
        :param callback: callable that accepts the internal state int
        :param nstates: number of states to store
        :param keystroke: keystrokes to associate with the "button"
        """
        self.current_state: int = 0
        self.callback = callback
        self.nstates = nstates
        keyboard.add_hotkey(keystroke, self.toggle)

    @property
    def enabled(self) -> int:
        return self.current_state

    def toggle(self) -> None:
        """update current state and call the button action"""
        old_state = self.current_state
        self.current_state += 1
        self.current_state %= self.nstates
        logging.debug(f"{self.__class__.__name__} registered with {self.callback}"
                      f" {old_state} -> {self.current_state}")
        if self.callback:
            self.callback(self.current_state)
