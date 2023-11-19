from .base_delegate import *

_BATCH_NAMES = ['background', 'cell', 'sprite', 'dynamic', 'static', 'kinematic', 'entity', 'anima', 'screen', 'label', 'main']


class BatchDelegate(Delegate):
    _represents = 'Batch'
    _BATCH_NAMES = _BATCH_NAMES
    for batch_name in _BATCH_NAMES:
        exec(f'_{batch_name}_batch = None', globals(), locals())

    def __init__(self, scene):
        super(BatchDelegate, self).__init__()
        self._scene = scene
        self._batches = {batch_name: getattr(self, f'_{batch_name}_batch') for batch_name in _BATCH_NAMES}
        self.init_batches()

    @property
    def scene(self):
        return self._scene

    @property
    def background_batch(self):
        return self._background_batch

    @background_batch.setter
    def background_batch(self, background_batch: Optional[pyglet.graphics.Batch] = None) -> None:
        self._background_batch = background_batch
        self._update_batches()

    @property
    def cell_batch(self):
        return self._cell_batch

    @cell_batch.setter
    def cell_batch(self, cell_batch: Optional[pyglet.graphics.Batch] = None) -> None:
        self._cell_batch = cell_batch
        self._update_batches()

    @property
    def main_batch(self) -> pyglet.graphics.Batch:
        return self._main_batch

    @main_batch.setter
    def main_batch(self, main_batch: Optional[pyglet.graphics.Batch] = None) -> None:
        self._main_batch = main_batch
        self._update_batches()

    @property
    def sprite_batch(self) -> pyglet.graphics.Batch:
        return self._sprite_batch

    @sprite_batch.setter
    def sprite_batch(self, sprite_batch: Optional[pyglet.graphics.Batch] = None) -> None:
        self._sprite_batch = sprite_batch
        self._update_batches()

    @property
    def label_batch(self) -> pyglet.graphics.Batch:
        return self._label_batch

    @label_batch.setter
    def label_batch(self, label_batch: Optional[pyglet.graphics.Batch] = None) -> None:
        self._label_batch = label_batch
        self._update_batches()

    @property
    def dynamic_batch(self) -> pyglet.graphics.Batch:
        return self._dynamic_batch

    @dynamic_batch.setter
    def dynamic_batch(self, dynamic_batch: Optional[pyglet.graphics.Batch] = None) -> None:
        self._dynamic_batch = dynamic_batch
        self._update_batches()

    @property
    def static_batch(self) -> pyglet.graphics.Batch:
        return self._static_batch

    @static_batch.setter
    def static_batch(self, static_batch: Optional[pyglet.graphics.Batch] = None) -> None:
        self._static_batch = static_batch
        self._update_batches()

    @property
    def kinematic_batch(self) -> pyglet.graphics.Batch:
        return self._kinematic_batch

    @kinematic_batch.setter
    def kinematic_batch(self, kinematic_batch: Optional[pyglet.graphics.Batch] = None) -> None:
        self._kinematic_batch = kinematic_batch
        self._update_batches()

    @property
    def entity_batch(self) -> pyglet.graphics.Batch:
        return self._entity_batch

    @entity_batch.setter
    def entity_batch(self, entity_batch: Optional[pyglet.graphics.Batch] = None) -> None:
        self._entity_batch = entity_batch
        self._update_batches()

    @property
    def anima_batch(self):
        return self._anima_batch

    @anima_batch.setter
    def anima_batch(self, anima_batch: Optional[pyglet.graphics.Batch] = None) -> None:
        self._anima_batch = anima_batch
        self._update_batches()

    @property
    def screen_batch(self):
        return self._screen_batch

    @screen_batch.setter
    def screen_batch(self, screen_batch: Optional[pyglet.graphics.Batch] = None) -> None:
        self._screen_batch = screen_batch
        self._update_batches()

    @property
    def label_batch(self):
        return self._label_batch

    @label_batch.setter
    def label_batch(self, label_batch: Optional[pyglet.graphics.Batch] = None) -> None:
        self._label_batch = label_batch
        self._update_batches()

    @property
    def batches(self) -> dict[str, pyglet.graphics.Batch]:
        self._update_batches()
        return self._batches

    def init_batches(self):
        for batch_name in _BATCH_NAMES:
            setattr(self, f'{batch_name}_batch', pyglet.graphics.Batch())

    def _update_batches(self):
        names = self._BATCH_NAMES
        self._batches = {name: getattr(self, f'_{name}_batch') for name in names}

    def update_dynamic_batch(self):
        new_batch = pyglet.graphics.Batch()
        for id, element in self.scene.element_delegate.dynamic_elements.copy().items():
            vertex_list = element.shape._vertex_list
            self.dynamic_batch.migrate(vertex_list, pyglet.gl.GL_TRIANGLES, None, new_batch)
        self.dynamic_batch = new_batch

    def update_static_batch(self):
        new_batch = pyglet.graphics.Batch()
        for id, element in self.scene.element_delegate.static_elements.copy().items():
            vertex_list = element.shape._vertex_list
            self.static_batch.migrate(vertex_list, pyglet.gl.GL_TRIANGLES, None, new_batch)
        self.static_batch = new_batch

    def update_kinematic_batch(self):
        new_batch = pyglet.graphics.Batch()
        for id, element in self.scene.element_delegate.kinematic_elements.copy().items():
            vertex_list = element.shape._vertex_list
            self.kinematic_batch.migrate(vertex_list, pyglet.gl.GL_TRIANGLES, None, new_batch)
        self.kinematic_batch = new_batch

    def _update_screen_batch(self):
        self._screen_batch = self.scene.active_screen.batch

    def update_main_batch(self):
        self.main_batch.invalidate()

    def update_element_batches(self):
        self.update_dynamic_batch()
        self.update_static_batch()
        self.update_kinematic_batch()

    def draw_elements(self):
        self.static_batch.draw()
        self.dynamic_batch.draw()
        self.kinematic_batch.draw()

    @log_method
    def add_batch(self, batch_name, batch):
        setattr(self, f'_{batch_name}_batch', batch)
        setattr(self, batch_name, getattr(self, f'_{batch_name}_batch'))
        setattr(self.scene, batch_name, getattr(self, f'_{batch_name}_batch'))
        self._BATCH_NAMES.append(batch_name)
        self._update_batches()

    def get_batch(self, batch_name):
        return getattr(self, batch_name)

    def update(self, dt):
        self.update_element_batches()
        self.update_main_batch()

    @log_method
    def draw(self):
        for batch_name, batch in self.batches.items():
            if batch_name != 'label':
                batch.draw()
            else:
                with self.scene.label_camera:
                    batch.draw()
