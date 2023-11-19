from .base_delegate import *

class AbstractEntity(ABC):
    pass

class AbstractScene(ABC):
    pass

class EntityDelegate(Delegate):
    _represents = 'Entity'
    _entities = {}
    _receivers = {
        'key_press'    : [],
        'key_release'  : [],
        'mouse_press'  : [],
        'mouse_release': [],
        'mouse_drag'   : [],
        'mouse_motion' : []
    }
    _entity_count = None
    
    def __init__(self, scene):
        self._scene = scene

    @property
    def scene(self) -> AbstractScene:
        return self._scene
    
    @scene.setter
    def scene(self, scene: Optional[AbstractScene] = None) -> None:
        self._scene = scene
    
    @property
    def receivers(self) -> dict[str, list[uuid.UUID]]:
        return self._receivers

    @receivers.setter
    def receivers(self, receivers: Optional[dict[str, list[uuid.UUID]]] = None) -> None:
        self._receivers = receivers

    @property
    def entities(self) -> dict[uuid.UUID, AbstractEntity]:
        return self._entities

    @entities.setter
    def entities(self, entities: Optional[dict[uuid.UUID, AbstractEntity]] = None) -> None:
        self._entities = entities

    @property
    def entity_count(self) -> int:
        return self._entity_count

    @entity_count.setter
    def entity_count(self, entity_count: Optional[int] = None) -> None:
        self._entity_count = entity_count

#       Entity Methods      #
    @log_method
    def add_entity(self, entity: AbstractEntity = None):
        if entity is not None:
            if self.entities.get(entity.entity_id) is not None:
                return
            if entity._recvs_input:
                for input in entity.inputs:
                    self.scene.dispatcher.set_handler(f'recv_{input}', getattr(entity, f'recv_{input}'))
                    self.receivers[input].append(entity.entity_id)
            self.entities[entity.entity_id] = entity
    
    @log_method
    def remove_entity(self, entity: AbstractEntity = None):
        if entity is not None:
            if entity._recvs_input:
                self.remove_receiver(entity.entity_id)
            self.entities[entity.entity_id] = None
            del self.entities[entity.entity_id]
            del entity

    @log_method
    def remove_receiver(self, entity_id):
        for input in self.receivers:
            if entity_id in self.receivers[input]:
                self.receivers[input].remove(entity_id)

    def update_entities(self, dt):
        for entity in self.entities.copy().values():
            if entity.active:
                entity.update(dt)
            else:
                self.remove_entity(entity)

    def get_entity(self, entity_id):
        if entity_id is not None and self.entities.get(entity_id) is not None:
            return self.entities.get(entity_id)

    def update_counts(self):
        self.entity_count = len(self.entities)