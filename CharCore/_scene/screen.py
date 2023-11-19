from abc import ABC, abstractmethod
from uuid import uuid4

import pyglet.graphics

_SCREEN_TYPES = ['MENU', 'MESSAGE', 'CINEMATIC', 'POPUP']
_SCREEN_STATES = ['ACTIVE', 'INACTIVE', 'QUEUED']


class AbstractScreen(ABC):
    _screen_type = None

    def __new__(cls, *args, **kwargs):
        if cls is AbstractScreen:
            raise TypeError("Abstract class 'AbstractScreen' cannot be instantiated")
        elif cls._screen_type is None or cls._screen_type not in _SCREEN_TYPES:
            raise TypeError("Screen must have a valid type")
        return super().__new__(cls)


class BaseScreen(AbstractScreen):
    def __init__(self):
        super(BaseScreen, self).__init__()
        self._scene = None
        self._title = None
        self._screen_id = None
        self._screen_state = None
        self._active = None
        self._visible = None

        self._elements = None
        self._labels = None
        self._screen_batch = None

    @property
    def scene(self):
        return self._scene

    @scene.setter
    def scene(self, scene):
        self._scene = scene

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title: str):
        self._title = title

    @property
    def screen_id(self):
        return self._screen_id

    @screen_id.setter
    def screen_id(self, screen_id):
        self._screen_id = screen_id

    @property
    def screen_state(self):
        return self._screen_state

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active: bool):
        if self._active != active:
            self._active = active
            if self.scene.active_screen == self:
                self.scene.active_screen = self if active else None
            elif self.scene.active_screen is not None:
                if active:
                    self.scene.active_screen.deactivate()
                    self.scene.active_screen = self

    @property
    def visible(self):
        return self._visible

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self, elements):
        self._elements = elements
        self.scene.element_delegate.add_element_dict('screen', elements)

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, labels):
        self._labels = labels

    @property
    def batch(self):
        return self._screen_batch

    @batch.setter
    def batch(self, batch):
        self._screen_batch = batch
        self.scene.batch_delegate.add_batch('screen', batch)

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def deactivate(self):
        pass

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def render(self):
        pass


class Screen(BaseScreen):
    def __init__(self, scene, title, screen_id=None, *args, **kwargs):
        super(Screen, self).__init__()
        self.scene = scene
        self.title = title
        self.screen_id = screen_id if screen_id is not None else uuid4()
        self.batch = pyglet.graphics.Batch()

    def activate(self):
        super().activate()
        if not self.active:
            self.active = True

    def deactivate(self):
        super().deactivate()
        if self.active:
            self.active = False

    def update(self, dt):
        super().update(dt)

    def render(self):
        super().render()


class ScreenManager:
    def __init__(self, scene):
        self._scene = scene
        self._set = set()
        self._screens = []
        self._deleted_screens = []
        self._active_screen = None
        self._discarded = []

    def __call__(self):
        self.active_screen = self.set_.pop()
        return self.active_screen

    @property
    def scene(self):
        return self._scene

    @property
    def set_(self):
        return self._set

    @property
    def screens(self):
        return self._screens

    @property
    def deleted_screens(self):
        return self._deleted_screens

    @property
    def active_screen(self):
        return self._active_screen

    @active_screen.setter
    def active_screen(self, screen):
        if screen is not None and self._active_screen != screen:
            if self._active_screen is not None:
                self._active_screen.deactivate()
            self.scene.active_screen = screen
            screen.activate()
        self._active_screen = screen

    @property
    def discarded(self):
        return self._discarded

    def __iter__(self):
        return iter(self.set_)

    def __len__(self):
        return len(self.set_)

    def __contains__(self, screen):
        return screen in self.set_

    def add_screen(self, screen):
        self.screens.append(screen)
        self.set_.add(screen)
        screen.set_ = self.set_
        if self.active_screen is None and self.screens.index(screen) == 0:
            self.active_screen = screen

    def add_screens(self, *screens):
        for screen in screens:
            self.add_screen(screen)

    def remove_screen(self, screen):
        self.set_.remove(screen)
        self.screens.remove(screen)
        screen.set_ = None
        screen.queue_pos = None
        self.discarded.append(screen)

    def get_screen(self):
        return self.active_screen

    def set_screen(self, screen):
        self.active_screen = screen
