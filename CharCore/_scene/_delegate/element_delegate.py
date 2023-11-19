from .base_delegate import *

class AbstractElement(ABC):
    element_type = None
    element_id = None
    pass

class ElementDelegate(Delegate):
    _represents = 'Element'
    _element_types = ['static', 'dynamic', 'kinematic']

    def __init__(self, scene):
        super(ElementDelegate, self).__init__()
        self._scene = scene
        self._dynamic_elements = {}
        self._static_elements = {}
        self._kinematic_elements = {}
        self._dynamic_sprite_elements = {}
        self._static_sprite_elements = {}
        self._kinematic_sprite_elements = {}
        self._anima_elements = {}
        self._elements = {
                'static':    self.static_elements,
                'dynamic':   self.dynamic_elements,
                'kinematic': self.kinematic_elements
        }
        self._screen_elements = {}
        self._element_count = 0
        self._dynamic_element_count = 0
        self._static_element_count = 0
        self._kinematic_element_count = 0
        self._sprite_count = 0
        self._dynamic_sprite_count = 0
        self._static_sprite_count = 0
        self._kinematic_sprite_count = 0
        self._active_element_count = 0

    @property
    def elements(self) -> dict[str, dict[uuid.UUID, AbstractElement]]:
        return self._elements

    @elements.setter
    def elements(self, elements: Optional[dict[str, dict[uuid.UUID, AbstractElement]]] = None) -> None:
        self._elements = elements
        self._update_elements()

    @property
    def screen_elements(self) -> dict[str, dict[uuid.UUID, AbstractElement]]:
        return self._screen_elements

    @screen_elements.setter
    def screen_elements(self, screen_elements: Optional[dict[str, dict[uuid.UUID, AbstractElement]]] = None) -> None:
        self._screen_elements = screen_elements
        self._update_elements()

    @property
    def dynamic_elements(self) -> dict[uuid.UUID, AbstractElement]:
        return self._dynamic_elements

    @dynamic_elements.setter
    def dynamic_elements(self, dynamic_elements: Optional[dict[uuid.UUID, AbstractElement]] = None) -> None:
        self._dynamic_elements = dynamic_elements
        self._update_elements()

    @property
    def static_elements(self) -> dict[uuid.UUID, AbstractElement]:
        return self._static_elements

    @static_elements.setter
    def static_elements(self, static_elements: Optional[dict[uuid.UUID, AbstractElement]] = None) -> None:
        self._static_elements = static_elements
        self._update_elements()

    @property
    def kinematic_elements(self) -> dict[uuid.UUID, AbstractElement]:
        return self._kinematic_elements

    @kinematic_elements.setter
    def kinematic_elements(self, kinematic_elements: Optional[dict[uuid.UUID, AbstractElement]] = None) -> None:
        self._kinematic_elements = kinematic_elements
        self._update_elements()

    @property
    def dynamic_sprite_elements(self) -> dict[uuid.UUID, AbstractElement]:
        return self._dynamic_sprite_elements

    @dynamic_sprite_elements.setter
    def dynamic_sprite_elements(
            self,
            dynamic_sprite_elements: Optional[dict[uuid.UUID, AbstractElement]] = None
            ) -> None:
        self._dynamic_sprite_elements = dynamic_sprite_elements
        self._update_elements()

    @property
    def static_sprite_elements(self) -> dict[uuid.UUID, AbstractElement]:
        return self._static_sprite_elements

    @static_sprite_elements.setter
    def static_sprite_elements(self, static_sprite_elements: Optional[dict[uuid.UUID, AbstractElement]] = None) -> None:
        self._static_sprite_elements = static_sprite_elements
        self._update_elements()

    @property
    def kinematic_sprite_elements(self) -> dict[uuid.UUID, AbstractElement]:
        return self._kinematic_sprite_elements

    @kinematic_sprite_elements.setter
    def kinematic_sprite_elements(
            self,
            kinematic_sprite_elements: Optional[dict[uuid.UUID, AbstractElement]] = None
            ) -> None:
        self._kinematic_sprite_elements = kinematic_sprite_elements
        self._update_elements()

    @property
    def sprite_elements(self) -> dict[str, dict[uuid.UUID, AbstractElement]]:
        self._update_elements()
        return self._sprite_elements

    @property
    def anima_elements(self) -> dict[uuid.UUID, AbstractElement]:
        return self._anima_elements
    
    @anima_elements.setter
    def anima_elements(self, anima_elements: Optional[dict[uuid.UUID, AbstractElement]] = None) -> None:
        self._anima_elements = anima_elements

    @property
    def element_count(self) -> int:
        return self._element_count

    @element_count.setter
    def element_count(self, element_count: Optional[int] = None) -> None:
        self._element_count = element_count

    @property
    def dynamic_element_count(self) -> int:
        return self._dynamic_element_count

    @dynamic_element_count.setter
    def dynamic_element_count(self, dynamic_element_count: Optional[int] = None) -> None:
        self._dynamic_element_count = dynamic_element_count

    @property
    def static_element_count(self) -> int:
        return self._static_element_count

    @static_element_count.setter
    def static_element_count(self, static_element_count: Optional[int] = None) -> None:
        self._static_element_count = static_element_count

    @property
    def kinematic_element_count(self) -> int:
        return self._kinematic_element_count

    @kinematic_element_count.setter
    def kinematic_element_count(self, kinematic_element_count: Optional[int] = None) -> None:
        self._kinematic_element_count = kinematic_element_count

    @property
    def sprite_count(self) -> int:
        return self._sprite_count

    @sprite_count.setter
    def sprite_count(self, sprite_count: Optional[int] = None) -> None:
        self._sprite_count = sprite_count

    @property
    def dynamic_sprite_count(self) -> int:
        return self._dynamic_sprite_count

    @dynamic_sprite_count.setter
    def dynamic_sprite_count(self, dynamic_sprite_count: Optional[int] = None) -> None:
        self._dynamic_sprite_count = dynamic_sprite_count

    @property
    def static_sprite_count(self) -> int:
        return self._static_sprite_count

    @static_sprite_count.setter
    def static_sprite_count(self, static_sprite_count: Optional[int] = None) -> None:
        self._static_sprite_count = static_sprite_count

    @property
    def kinematic_sprite_count(self) -> int:
        return self._kinematic_sprite_count

    @kinematic_sprite_count.setter
    def kinematic_sprite_count(self, kinematic_sprite_count: Optional[int] = None) -> None:
        self._kinematic_sprite_count = kinematic_sprite_count

    @property
    def active_element_count(self) -> int:
        return self._active_element_count

    @active_element_count.setter
    def active_element_count(self, active_element_count: Optional[int] = None) -> None:
        self._active_element_count = active_element_count

    def _update_elements(self):
        self._elements = {elem_type: getattr(self, f'{elem_type}_elements') for elem_type in
                          self._element_types}
        self._update_sprite_elements()

    def _update_sprite_elements(self):
        self._sprite_elements = {elem_type: getattr(self, f'{elem_type}_sprite_elements') for elem_type in
                                 self._element_types}

    def _add_element_dict(
            self,
            element_type: str = None,
            element_dict: Optional[Union[dict[uuid.UUID, AbstractElement], dict[None], None]] = None
            ) -> None:
        setattr(self, f'_{element_type}_elements', element_dict)
        setattr(
            self.__class__, f'{element_type}_elements',
            property(lambda self: getattr(self, f'_{element_type}_elements'))
            )
        self._element_types.append(element_type)
        self._update_elements()

    def add_element(self, element: Optional[AbstractElement] = None, element_type: Optional[str] = None) -> None:
        if element_type is None:
            if hasattr(element, 'is_sprite') and element.is_sprite:
                elements = getattr(self, f'{element.element_type}_sprite_elements')
            else:
                elements = getattr(self, f'{element.element_type}_elements')
        else:
            elements = getattr(self, f'{element_type}_elements')
        if elements.get(element.element_id) is not None:
            return
        self.element_count += 1
        elements[element.element_id] = element

    def add_elements(self, elements):
        for element in elements:
            self.add_element(element)

    def remove_element(self, element):
        for elem_type, elems in self.elements.items():
            if element.element_id in elems.copy().keys():
                self.elements[elem_type][element.element_id] = None
                del self.elements[elem_type][element.element_id]
                del element
                return

    def remove_elements(self, elements):
        for element in elements:
            self.remove_element(element)

    def get_element(self, elem_id):
        if self.static_elements.get(elem_id) is not None:
            return self.static_elements[elem_id]
        elif self.dynamic_elements.get(elem_id) is not None:
            return self.dynamic_elements[elem_id]
        elif self.kinematic_elements.get(elem_id) is not None:
            return self.kinematic_elements[elem_id]
        else:
            return None
        
    def clean_offscreen_elements(self):
        for elem_type, elems in self.elements.items():
            for elem in elems.copy().values():
                if elem is not None and elem.offscreen:
                    self.remove_element(elem)

    def update_elements(self, dt):
        for elem_type in self._element_types:
            for element in getattr(self, f'{elem_type}_elements').copy().values():
                if element.active:
                    element.update(dt)
                else:
                    self.remove_element(element)

    def update_counts(self):
        self.element_count = len(self.elements)
        self.static_element_count = len(self.static_elements)
        self.dynamic_element_count = len(self.dynamic_elements)
        self.kinematic_element_count = len(self.kinematic_elements)
        self.sprite_count = len(self.sprite_elements)
        self.dynamic_sprite_count = len(self.dynamic_sprite_elements)
        self.static_sprite_count = len(self.static_sprite_elements)
        self.kinematic_sprite_count = len(self.kinematic_sprite_elements)
        self.active_element_count = self.static_element_count + self.dynamic_element_count + \
                                    self.kinematic_element_count + self.dynamic_sprite_count + \
                                    self.static_sprite_count + self.kinematic_sprite_count

    def update(self, dt):
        self.update_elements(dt)
        self.update_counts()
        self.clean_offscreen_elements()