from __future__ import annotations


from . import logger, log_method
from .camera import *

from abc import ABC, abstractmethod
from typing import Optional, Any, AnyStr, Union
import uuid

import pyglet
from pyglet.event import EventDispatcher
from pyglet.math import Vec2
from pyglet.window import key, mouse
from pyglet.gl import *

import pymunk
from pymunk import Vec2d

from .screen import ScreenManager
from ._meta import SceneMeta


class AbstractElement(ABC):
    pass


class AbstractEntity(ABC):
    pass


_BATCH_NAMES = ['background', 'main', 'sprite', 'label', 'dynamic', 'static', 'kinematic', 'entity', 'anima']


class AbstractScene(metaclass=type):
    logger.log(2, 'Initializing AbstractScene.')
    HANDLERS = {
            'on_key_press':     'recv_key_press',
            'on_key_release':   'recv_key_release',
            'on_mouse_press':   'recv_mouse_press',
            'on_mouse_release': 'recv_mouse_release',
            'on_mouse_drag':    'recv_mouse_drag',
            'on_mouse_motion':  'recv_mouse_motion',
            'on_refresh':       'refresh',
            'on_render':        'render'
    }

    CUSTOM_EVENTS = {
            'recv_key_press':     'key_press',
            'recv_key_release':   'key_release',
            'recv_mouse_press':   'mouse_press',
            'recv_mouse_release': 'mouse_release',
            'recv_mouse_drag':    'mouse_drag',
            'recv_mouse_motion':  'mouse_motion'
    }

    _scene_id = None
    _title = None
    _window = None
    _frame_count = None
    _debug = None
    _debug_objects = None
    _screen_manager = None
    _active_screen = None
    _mouse_pos = None
    _mouse_x = None
    _mouse_y = None
    _mouse_dx = None
    _mouse_dy = None
    _buttons = []

    _button_bin = None
    _button_locker = None

    _paused = False
    _active = None

    _time_scale = None

    _camera = None
    _label_camera = None

    _buffer_manager = None

    @property
    def scene_id(self) -> str:
        return self._scene_id.hex

    @scene_id.setter
    def scene_id(self, scene_id: Optional[uuid.UUID] = None) -> None:
        if scene_id is None:
            self._scene_id = uuid.uuid4()

        elif isinstance(scene_id, uuid.UUID):
            self._scene_id = scene_id
        else:
            raise TypeError('Scene ID must be a UUID.')

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, title: Optional[str] = None) -> None:
        self._title = title if title is not None else 'Untitled Scene'

    @property
    def window(self) -> pyglet.window.Window:
        return self._window

    @window.setter
    def window(self, window: Optional[pyglet.window.Window] = None) -> None:
        logger.log(2, 'Setting window.')
        self._window = window
        self.link(window)

    @property
    def background_batch(self):
        return self.batch_delegate.background_batch

    @property
    def main_batch(self) -> pyglet.graphics.Batch:
        return self.batch_delegate.main_batch

    @property
    def sprite_batch(self) -> pyglet.graphics.Batch:
        return self.batch_delegate.sprite_batch

    @property
    def dynamic_batch(self) -> pyglet.graphics.Batch:
        return self.batch_delegate.dynamic_batch

    @property
    def static_batch(self) -> pyglet.graphics.Batch:
        return self.batch_delegate.static_batch

    @property
    def kinematic_batch(self) -> pyglet.graphics.Batch:
        return self.batch_delegate.kinematic_batch

    @property
    def entity_batch(self) -> pyglet.graphics.Batch:
        return self.batch_delegate.entity_batch

    @property
    def anima_batch(self):
        return self.batch_delegate.anima_batch

    @property
    def screen_batch(self):
        return self.batch_delegate.screen_batch

    @property
    def batches(self) -> dict[str, pyglet.graphics.Batch]:
        return self.batch_delegate.batches

    @property
    def receivers(self) -> dict[str, list[uuid.UUID]]:
        return self.entity_delegate.receivers

    @receivers.setter
    def receivers(self, receivers: Optional[dict[str, list[uuid.UUID]]] = None) -> None:
        self.entity_delegate.receivers = receivers

    @property
    def entities(self) -> dict[uuid.UUID, AbstractEntity]:
        return self.entity_delegate.entities

    @entities.setter
    def entities(self, entities: Optional[dict[uuid.UUID, AbstractEntity]] = None) -> None:
        self.entity_delegate.entities = entities

    @property
    def entity_count(self) -> int:
        return self.entity_delegate.entity_count

    @entity_count.setter
    def entity_count(self, entity_count: Optional[int] = None) -> None:
        self.entity_delegate.entity_count = entity_count

    @property
    def screen_manager(self):
        return self._screen_manager

    @property
    def active_screen(self):
        if self._active_screen is None and len(self.screen_manager) > 0:
            self._active_screen = self.screen_manager()
        return self._active_screen

    @active_screen.setter
    def active_screen(self, active_screen):
        self.screen_manager._active_screen = active_screen

    @property
    def mouse_pos(self):
        if self._mouse_pos is None:
            self._mouse_pos = (
                    self._mouse_x, self._mouse_y) if self._mouse_x is not None and self._mouse_y is not None else (0, 0)
        return self._mouse_pos

    @mouse_pos.setter
    def mouse_pos(self, value):
        self._mouse_x = value[0]
        self._mouse_y = value[1]
        self._mouse_pos = value

    @property
    def buttons(self):
        return self._buttons

    @buttons.setter
    def buttons(self, value):
        self._buttons = value

    @property
    def button_bin(self):
        return self._button_bin

    @button_bin.setter
    def button_bin(self, value):
        self._button_bin = value

    @property
    def button_locker(self):
        return self._button_locker

    @button_locker.setter
    def button_locker(self, value):
        self._button_locker = value

    @property
    def keys_(self):
        return self.window.keys_

    @property
    def paused(self):
        return self._paused

    @paused.setter
    def paused(self, value):
        self._paused = value

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        if value is not None:
            if not value:
                if self.window is not None and self.window.active_scene == self:
                    self.window.active_scene = None
                self._active = False
            else:
                if self.window is not None:
                    self.window.activate_scene(self.title)
                self._active = True

    @property
    def time_scale(self):
        return self._time_scale

    @time_scale.setter
    def time_scale(self, value):
        self._time_scale = max(value, 1)

    @property
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, camera):
        if camera is not None and isinstance(camera, Camera):
            self._camera = camera
        elif not camera and self._camera is not None:
            self._camera = None

    @property
    def label_camera(self):
        return self._label_camera

    @property
    def buffer_manager(self):
        return self._buffer_manager

    @abstractmethod
    def create_scene(self, *args, **kwargs):
        pass

    @abstractmethod
    def world_step(self, dt: Optional[float] = None) -> None:
        pass

    @abstractmethod
    def add_dynamic_label(
            self,
            label_subject: Optional[Any] = None,
            label_attr: Optional[AnyStr] = None,
            placement: Optional[Union[tuple[int, int], Vec2, Vec2d]] = None,
            duration: Optional[int] = None,
            width: Optional[int] = None,
            style: Optional[Any] = None,
            perishable: Optional[bool] = None, persistent: Optional[bool] = None
    ) -> None:
        pass

    @abstractmethod
    def add_static_label(
            self,
            label_subject: Optional[Any] = None,
            label_attr: Optional[AnyStr] = None,
            placement: Optional[Union[tuple[int, int], Vec2, Vec2d]] = None,
            duration: Optional[int] = None,
            width: Optional[int] = None,
            style: Optional[Any] = None,
            perishable: Optional[bool] = None, persistent: Optional[bool] = None
    ) -> None:
        pass

    @abstractmethod
    def add_unassociated_label(
            self,
            label_text: Optional[AnyStr] = None,
            placement: Optional[Union[tuple[int, int], Vec2, Vec2d]] = None,
            duration: Optional[int] = None,
            width: Optional[int] = None,
            color: Optional[Union[tuple[int, int, int], tuple[int, int, int, int]]] = None,
            style: Optional[Any] = None,
            perishable: Optional[bool] = None, persistent: Optional[bool] = None
    ) -> None:
        pass

    @abstractmethod
    def remove_label(self, label_num: Optional[int] = None) -> None:
        pass

    @abstractmethod
    def add_element(self, element: Optional[AbstractElement] = None) -> None:
        pass

    @abstractmethod
    def add_elements(self, *elements: list[AbstractElement]) -> None:
        pass

    @abstractmethod
    def remove_element(self, element: AbstractElement) -> None:
        pass

    @abstractmethod
    def remove_elements(self, *elements: list[AbstractElement]) -> None:
        pass

    @abstractmethod
    def add_button(self, button) -> None:
        pass

    @abstractmethod
    def add_entity(self, entity) -> None:
        pass

    @abstractmethod
    def remove_entity(self, entity) -> None:
        pass

    @abstractmethod
    def link(self, window: Optional[type[pyglet.window.Window]]) -> None:
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def add_screen(self, screen):
        pass

    @screen_manager.setter
    def screen_manager(self, value):
        self._screen_manager = value


class Scene(AbstractScene):
    """An abstract base class for scene objects."""

    def __init__(
            self,
            scene_id: Optional[str] = None,
            window: Optional[object] = None,
            title: str = None,
            *args, **kwargs
    ):
        super(Scene, self).__init__(*args, **kwargs)
        self._scene_id = scene_id
        self._window = window
        self._title = title
        self._screen_manager = ScreenManager(self)
        self._active_screen = None
        self._label_count = 0
        self._button_bin = []
        self._button_locker = []
        self._time_scale = 1
        self._buffer_manager = pyglet.image.get_buffer_manager()
        self._label_camera = Camera(self.window, max_zoom=1)

    @abstractmethod
    def create_scene(self, *args, **kwargs):
        pass

    @abstractmethod
    def world_step(self, dt: Optional[float] = None) -> None:
        pass

    @log_method
    def link(self, window: Optional[type[pyglet.window.Window]] = None):
        logger.log(2, 'Linking scene to window.')
        if window is not None:
            window.add_scene(self)
        if self.window.scenes.get(self.title) is not None:
            logger.log(2, 'Successfully linked scene to window.')
        else:
            logger.log(2, 'Warning: Scene was not found in scenes list. Something went wrong.')

    #       Activation Methods      #
    @log_method
    def activate(self):
        if self.active:
            logger.log(2, 'Scene attempted to activate while already active.')
            return
        self.active = True

    @log_method
    def deactivate(self):
        logger.log(2, 'Deactivating scene.')
        logger.log(2, 'Removing handlers.')
        self.window.remove_handler('on_deactivate', self.deactivate)
        for event_type in self.window.event_types:
            if event_type in self.HANDLERS:
                logger.log(2, 'Removing %s for event type: "%s"', self.HANDLERS[event_type], event_type)
                self.window.remove_handler(event_type, getattr(self, self.HANDLERS[event_type]))
        if self.active:
            self.active = False
        logger.log(2, 'Successfully deactivated scene.')

    def reactivate(self):
        logger.log(2, 'Reactivating scene.')
        self.deactivate()
        self.__init__(window=self.window)
        self.activate()
        logger.log(2, 'Successfully reactivated scene.')

    @log_method
    def pause(self):
        self.paused = True
        self.active = False

    @log_method
    def resume(self):
        self.paused = False
        self.active = True


    #       Label Methods       #
    @log_method
    def add_static_label(
            self,
            label_subject: Optional[Any] = None,
            label_attr: Optional[AnyStr] = None,
            placement: Optional[Union[tuple[int, int], Vec2, Vec2d]] = None,
            duration: Optional[int] = None,
            width: Optional[int] = None,
            style: Optional[Any] = None,
            perishable: Optional[bool] = None, persistent: Optional[bool] = None
    ) -> None:
        """Calls the add_static_label method of the label delegate. """
        return self.label_delegate.add_static_label(
                label_subject, label_attr, placement, duration, width, style,
                perishable, persistent
        )

    @log_method
    def add_dynamic_label(
            self,
            label_subject: Optional[Any] = None,
            label_attr: Optional[AnyStr] = None,
            placement: Optional[Union[tuple[int, int], Vec2, Vec2d]] = None,
            duration: Optional[int] = None,
            width: Optional[int] = None,
            style: Optional[Any] = None,
            perishable: Optional[bool] = None, persistent: Optional[bool] = None
    ) -> None:
        """Calls the add_dynamic_label method of the label delegate. """
        return self.label_delegate.add_dynamic_label(label_subject, label_attr, placement, duration, width, style, )

    @log_method
    def add_unassociated_label(
            self,
            label_text: Optional[AnyStr] = None,
            placement: Optional[Union[tuple[int, int], Vec2, Vec2d]] = None,
            duration: Optional[int] = None,
            width: Optional[int] = 500,
            color: Optional[Union[tuple[int, int, int], tuple[int, int, int, int]]] = (255, 255, 255, 255),
            style: Optional[Any] = None,
            perishable: Optional[bool] = None, persistent: Optional[bool] = None
    ) -> None:
        return self.label_delegate.add_unassociated_label(
                label_text, placement, duration, width, color, perishable, persistent
        )

    def remove_label(self, label_num: Optional[int] = None) -> None:
        return self.label_delegate.remove_label(label_num)

    #       Element Methods         #
    def add_element(self, element: Optional[AbstractElement] = None) -> None:
        return self.element_delegate.add_element(element)

    def add_elements(self, *elements):
        return self.element_delegate.add_elements(elements)

    def remove_element(self, element):
        return self.element_delegate.remove_element(element)

    def remove_elements(self, elements):
        return self.element_delegate.remove_elements(elements)

    def get_element(self, elem_id):
        return self.element_delegate.get_element(elem_id)

    #       Entity Methods      #
    @log_method
    def add_entity(self, entity: AbstractEntity = None):
        return self.entity_delegate.add_entity(entity)

    @log_method
    def remove_entity(self, entity: AbstractEntity = None):
        return self.entity_delegate.remove_entity(entity)

    @log_method
    def remove_receiver(self, entity_id):
        return self.entity_delegate.remove_receiver(entity_id)

    def update_entities(self, dt):
        return self.entity_delegate.update_enitities(dt)

    def get_entity(self, entity_id):
        return self.entity_delegate.get_entity(entity_id)

    def update_counts(self):
        self.entity_delegate.update_counts()

    #       Input Methods       #
    def recv_key_press(self, symbol, modifiers):
        #        logger.log(2, 'Received key press event. Symbol: %s', key.symbol_string(symbol))
        # for receiver in self.receivers['key_press']:
        #     receiver = self.get_entity(receiver)
        #     if receiver is not None:
        #         #                logger.log(2, f'Sending key press event to entity: {receiver.entity_id}')
        #         receiver.recv_key_press(symbol, modifiers)
        if symbol == key.F1:
            self.label_delegate.debug = not self.label_delegate.debug
        elif symbol == key.F3:
            self.time_scale += 1
        elif symbol == key.F4:
            self.time_scale -= 1
        elif symbol == key.F5:
            self.time_scale = 1
        self.dispatcher.dispatch_event('recv_key_press', symbol, modifiers)

    def recv_key_release(self, symbol, modifiers):
        #        logger.log(2, 'Received key release event. Symbol: %s', key.symbol_string(symbol))
        # for receiver in self.receivers['key_release']:
        #     receiver = self.get_entity(receiver)
        #     if receiver is not None:
        #         #                logger.log(2, f'Sending key release event to entity: {receiver.entity_id}')
        #         receiver.recv_key_release(symbol, modifiers)
        self.dispatcher.dispatch_event('recv_key_release', symbol, modifiers)

    def recv_mouse_press(self, x, y, btn, modifiers):
        #        logger.log(2, 'Received mouse press event @ (%s, %s) - Button: %s', x, y, mouse.buttons_string(btn))
        self.mouse_pos = (x, y)
        # for receiver in self.receivers['mouse_press']:
        #     receiver = self.get_entity(receiver)
        #     if receiver is not None:
        #         #                logger.log(2, f'Sending mouse press event to entity: {receiver.entity_id}')
        #         receiver.recv_mouse_press(x, y, btn, modifiers)
        self.dispatcher.dispatch_event('recv_mouse_press', x, y, btn, modifiers)
        for button in self.buttons:
            if button.hovered and btn == mouse.LEFT:
                button.on_press()

    def recv_mouse_release(self, x, y, btn, modifiers):
        #        logger.log(2, 'Received mouse release event @ (%s, %s) - Button: %s', x, y, mouse.buttons_string(btn))
        self.mouse_pos = (x, y)
        # for receiver in self.receivers['mouse_release']:
        #     receiver = self.get_entity(receiver)
        #     if receiver is not None:
        #         #                logger.log(2, f'Sending mouse release event to entity: {receiver.entity_id}')
        #         receiver.recv_mouse_release(x, y, btn, modifiers)
        self.dispatcher.dispatch_event('recv_mouse_release', x, y, btn, modifiers)
        for button in self.buttons:
            if button.hovered and button.pressed and btn == mouse.LEFT:
                button.on_release()
                button.on_click()

    def recv_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        # for receiver in self.receivers['mouse_drag']:
        #     receiver = self.get_entity(receiver)
        #     if receiver is not None:
        #         receiver.recv_mouse_drag(x, y, dx, dy, buttons, modifiers)
        self.dispatcher.dispatch_event('recv_mouse_drag', x, y, dx, dy, buttons, modifiers)

    def recv_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = (x, y)
        # for receiver in self.receivers['mouse_motion']:
        #     receiver = self.get_entity(receiver)
        #     if receiver is not None:
        #         receiver.recv_mouse_motion(x, y, dx, dy)
        self.dispatcher.dispatch_event('recv_mouse_motion', x, y, dx, dy)
        for button in self.buttons:
            if button.check(x, y):
                if not button.hovered:
                    button.on_enter()
            elif button.hovered:
                button.on_leave()

    #       Button Methods      #
    def add_button(self, button, persistent=None, perishable=None):
        self.buttons.append(button)
        button.dispatcher.set_handler('on_click', self.recv_payload)
        if perishable:
            self.button_bin.append(button)
        elif persistent:
            self.button_locker.append(button)

    def remove_button(self, button):
        button.sprite.delete()
        button.sprite2.delete()
        if hasattr(button, 'sprite3') and button.sprite3 is not None:
            button.sprite3.delete()
        if hasattr(button, 'sprite4') and button.sprite4 is not None:
            button.sprite4.delete()
        if button in self.buttons:
            self.buttons.remove(button)

    def recv_payload(self, payload):
        logger.log(2, 'Received payload: %s', payload)

    def check_buttons(self):
        for btn in self.buttons:
            if not btn.hovered and btn.check(*self.mouse_pos):
                btn.on_enter()
            elif btn.hovered and not btn.check(*self.mouse_pos):
                btn.on_leave()

    def draw_buttons(self):
        if self.buttons:
            for button in self.buttons:
                button.draw()

    @log_method
    def add_screen(self, screen):
        self.screen_manager.add_screen(screen)

    def refresh(self, dt):
        if not self.active:
            return
        self._frame_count = self.window.frame_count
        if self.active_screen is not None:
            self.active_screen.update(dt)
        self.element_delegate.update(dt)
        if hasattr(self, 'is_physical') and self.is_physical:
            self.world_step(dt / self.time_scale)
        self.batch_delegate.update(dt)
        self.label_delegate.update(dt)
        self.check_buttons()
        self.update_counts()

    def render(self):
        if not self.paused and not self.active:
            return
        if self.camera is None:
            self._extracted_from_render_4()
        else:
            with self.camera:
                self._extracted_from_render_4()
        with self.label_camera:
            self.label_delegate.draw()

    # TODO Rename this here and in `render`
    def _extracted_from_render_4(self):
        self.batch_delegate.draw()
        if self.active_screen is not None:
            self.active_screen.render()
        self.draw_buttons()



class BaseScene(Scene, metaclass=SceneMeta('SceneMeta', (type,), {})):
    """BaseScene is a base class from which all scenes should inherit. It provides a number of useful methods and
    attributes for handling user inputs and rendering objects on the screen. The run() method runs the demo loop until
    the user quits the demo. The create_scene() method is called by the __init__() method     
    """

    def __init__(
            self,
            scene_id: Optional[str] = None,
            window: Optional[object] = None,
            title: str = None,
            *args, **kwargs
    ):
        self.dispatcher = EventDispatcher()
        for event in self.CUSTOM_EVENTS:
            self.dispatcher.register_event_type(event)
        logger.log(2, 'Creating scene: %s', title)
        self.create_scene(scene_id, window, title, *args, **kwargs)
        logger.log(2, 'Successfully created scene: %s', title)
        if self.window.active_scene is None:
            self.window.activate_scene(self.title)

    def world_step(self, dt: Optional[float] = None, *args, **kwargs):
        self.world.step(dt)

    @log_method
    def create_scene(
            self,
            scene_id: Optional[str] = None,
            window: Optional[object] = None,
            title: str = None,
            *args, **kwargs
    ):
        super(BaseScene, self).__init__(scene_id, window, title, *args, **kwargs)
        logger.log(2, 'Instantiating delegates.')
        self.element_delegate = self.element_delegate(self)
        logger.log(2, f'Element delegate: {self.element_delegate}')
        self.batch_delegate = self.batch_delegate(self)
        logger.log(2, f'Batch delegate: {self.batch_delegate}')
        self.label_delegate = self.label_delegate(self)
        logger.log(2, f'Label delegate: {self.label_delegate}')
        self.entity_delegate = self.entity_delegate(self)
        logger.log(2, f'Entity delegate: {self.entity_delegate}')
        self.scene_id = scene_id
        logger.log(2, 'Scene ID: %s', self.scene_id)
        self.title = title if title is not None else self.__class__.__name__
        self.window = window

    def refresh(self, dt):
        super().refresh(dt)

