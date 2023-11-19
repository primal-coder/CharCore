# %%
from . import _log as log, _log_method as log_method

from abc import ABC as _ABC

from typing import Optional as _Optional
import contextlib as _contextlib
from functools import wraps

import pyglet as _pyglet
from pyglet.window import key as _key, mouse as _mouse
from pyglet.gl import *

log.log(1, 'Importing _window module.')
class MainWindow(_pyglet.window.Window):
    """
    This class is derived from :py:class:`~pyglet.window.Window`.
    It initializes the main window and registers the events to be used.
    It has various methods for handling user inputs and rendering objects on the screen.
    The run() method runs the demo loop until the user quits the demo.
    """
    log.log(1, 'Initializing MainWindow class.')
    _EVENTS = ['on_activate', 'on_deactivate', 'on_reactivate', 'on_refresh', 'on_render']


    for event in _EVENTS:
        log.log(1, f'Registering event: {event}')
        _pyglet.window.Window.register_event_type(event)

    def __init__(self, init: bool = False) -> None:
        log.log(1, 'Call to super(MainWindow, self).__init__(fullscreen=False, resizable=True).')
        if init:
            super(MainWindow, self).__init__(fullscreen=True, resizable=True)
        log.log(1, 'Target frame rate: 60 fps')
        self.fps = 1 / 60
        self.clock = _pyglet.clock.Clock()
        self._frame_count = 0
        self.fps_display = _pyglet.window.FPSDisplay(self)
        self.keys_ = {}
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_dx = 0
        self.mouse_dy = 0
        self._active_scene = None
        self._scenes = {}
        self.active = True
        self.set_clock()
        log.log(1, 'Main window initialized.')

    @property
    def frame_count(self) -> int:
        """Returns the frame count."""
        return self._frame_count

    @frame_count.setter
    def frame_count(self, value: int) -> None:
        """Sets the frame count."""
        self._frame_count = value

    @property
    def active_scene(self) -> _Optional[_ABC]:
        """Returns the active scene."""
        return self._active_scene

    @active_scene.setter
    def active_scene(self, value: _ABC) -> None:
        """Sets the active scene."""
        if self._active_scene is None:
            self.push_handlers(on_activate=value.activate)
            self._active_scene = value
            self.dispatch_event('on_activate')
            self.remove_handler('on_activate', value.activate)
            self.set_scene_handlers()

    @property
    def scenes(self) -> dict:
        """Returns the scenes."""
        return self._scenes

    @scenes.setter
    def scenes(self, value: dict) -> None:
        """Sets the scenes."""
        self._scenes = value

    def init(self, run: bool = False) -> None:
        """Initializes the main window."""
        super(MainWindow, self).__init__(fullscreen=True, resizable=True)
        if run:
            self.run()
    
    def set_clock(self) -> None:
        """Schedules the demo loop to run at the fps specified during init."""
        self.clock.schedule_interval(self.cycle, 1 / 60)

    @log_method
    def add_scene(self, scene=None):
        if scene is not None:
            scene_title = scene.title
            self.scenes[scene_title] = scene

    @log_method
    def deactivate_scene(self) -> None:
        """Dispatches the 'on_deactivate' event."""
        log.log(1, f'Deactivating {self.active_scene.title}.')
        self.dispatch_event('on_deactivate')

    @log_method
    def activate_scene(self, scene_title: str) -> None:
        scene = self.scenes[scene_title]
        if self.active_scene is not None:
            if scene is None:
                return
            if self.active_scene != scene:
                self.deactivate_scene()
        self.active_scene = scene
        log.log(1, 'Successfully activated scene.')

    def set_scene_handlers(self) -> None:
        """Adds event handlers."""
        log.log(1, 'Setting handlers on window.')
        self.push_handlers(on_deactivate=self.active_scene.deactivate, on_reactivate=self.active_scene.reactivate)
        for event_type in self.event_types:
            if event_type in self.active_scene.HANDLERS:
                log.log(1, f'Pushing {self.active_scene.title.replace(" ", "_").lower()}.{self.active_scene.HANDLERS[event_type]} for event type: {event_type}')
                self.set_handler(event_type, getattr(self.active_scene, self.active_scene.HANDLERS[event_type]))

    def reactivate_scene(self) -> None:
        """Dispatches the 'on_reactivate' event."""
        self.dispatch_event('on_reactivate')

    @log_method
    def switch_scene(self, scene_title: str) -> None:
        """Switches the active scene."""
        self.deactivate_scene()
        self.activate_scene(scene_title)
        self.active = False

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        """
        Sets the _mouse position when it is moved
        
        Args:
            x (int): The x coordinate of the _mouse.
            y (int): The y coordinate of the _mouse.
            dx (int): The change in x coordinate of the _mouse.
            dy (int): The change in y coordinate of the _mouse.

        Returns:
            None
        """
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x: int, y: int, btn: int, modifiers: int) -> None:
        """
        Handles the _mouse press event.
        
        Args:
            x (int): The x coordinate of the _mouse.
            y (int): The y coordinate of the _mouse.
            btn (int): The button pressed.
            modifiers (int): The modifiers pressed.
            
        Returns:
            None
        """
        pass

    def on_mouse_release(self, x: int, y: int, btn: int, modifiers: int) -> None:
        """Handles the _mouse release event."""
        pass

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, btn: int, modifiers: int) -> None:
        """Handles the _mouse drag event."""
        self.mouse_dx = dx
        self.mouse_dy = dy

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        with _contextlib.suppress(Exception):
            del self.keys_[symbol]

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handles the key press event."""
        self.keys_[symbol] = True
        if symbol == _key.ESCAPE:
            self.deactivate_scene()
            self.active = False

        elif symbol == _key.F5:
            self.deactivate_scene()
            self.activate_scene('home')

    def refresh(self, dt: float) -> None:
        """Flips the buffer and dispatches the 'on_refresh' event."""
        self.flip()
        self.dispatch_event('on_refresh', dt)

    def render(self) -> None:
        """Clears the screen and dispatches the 'on_render' event."""
        glClear(GL_COLOR_BUFFER_BIT)
        self.fps_display.draw()
        self.dispatch_event('on_render')

    def cycle(self, dt: float) -> None:
        """Calls the refresh and render methods and increments the frame count."""
        self.refresh(dt)
        self.render()
        self.frame_count += 1

    def run(self) -> None:
        """Runs the main loop."""
        log.log(1, 'Running main loop.')

        while self.active:
            self.clock.tick()
            self.dispatch_events()
        log.log(1, 'Game loop exited.')
        self.close()
            
            


# %%
