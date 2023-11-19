from .. import log_method, logger

from .base_delegate import *


class LabelDelegate(Delegate):
    _represents = 'Label'

    def __init__(self, scene):
        super(LabelDelegate, self).__init__()
        self._scene = scene
        self._window = scene.window
        self._debug = False
        self._debug_objects = []
        self._dynamic_labels = {}
        self._static_labels = {}
        self._unassoc_labels = {}
        self._labels = {
                'static':  self.static_labels,
                'dynamic': self.dynamic_labels,
                'unassoc': self.unassoc_labels
        }
        self._label_count = 0

        self._label_bin = []
        self._label_locker = []

        self.label_batch = pyglet.graphics.Batch()

    @property
    def scene(self):
        return self._scene

    @property
    def window(self):
        return self._window

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, debug):
        self._debug = debug

    @property
    def debug_objects(self):
        return self._debug_objects

    @debug_objects.setter
    def debug_objects(self, debug_objects):
        self._debug_objects = debug_objects

    @property
    def labels(self):
        self._update_labels()
        return self._labels

    @property
    def dynamic_labels(self):
        return self._dynamic_labels

    @dynamic_labels.setter
    def dynamic_labels(self, value):
        self._dynamic_labels = value
        self._update_labels()

    @property
    def static_labels(self):
        return self._static_labels

    @static_labels.setter
    def static_labels(self, value):
        self._static_labels = value
        self._update_labels()

    @property
    def unassoc_labels(self):
        return self._unassoc_labels

    @unassoc_labels.setter
    def unassoc_labels(self, value):
        self._unassoc_labels = value
        self._update_labels()

    @property
    def label_count(self):
        count = sum(len(labels) for labels in self._labels.values())
        if self._label_count != count:
            self._label_count = count
        return self._label_count

    @label_count.setter
    def label_count(self, value):
        self._label_count = value

    @property
    def label_bin(self):
        return self._label_bin

    @label_bin.setter
    def label_bin(self, value):
        self._label_bin = value

    @property
    def label_locker(self):
        return self._label_locker

    @label_locker.setter
    def label_locker(self, value):
        self._label_locker = value

    # @property
    # def label_batch(self):
    #     return self.scene.batch_delegate.get_batch('_label_batch')
    #
    # @label_batch.setter
    # def label_batch(self, value):
    #     self.scene.batch_delegate.add_batch('label', value)

    def _update_labels(self):
        self._labels = {label_type: getattr(self, f'{label_type}_labels') for label_type in
                        ['dynamic', 'static', 'unassoc']}

    def create_label_id(self):
        return uuid.uuid4().hex[-4:]

    def create_associated_label(self, label_subject=None, label_attr=None, label_placement=None, width=None, style=None):
        width = width if width is not None else 400
        self.label_count += 1
        if label_placement is None:
            x = 100
            y = 10 + (self.label_count * 20)
        else:
            x = label_placement[0]
            y = label_placement[1]
        if label_subject is not None:
            style = \
                [f'{label_attr}: {str(getattr(label_subject, label_attr))}',
                 f'{str(getattr(label_subject, label_attr))}',
                 f'{label_attr}', f'{str(getattr(label_subject, label_attr))}'][style if style is not None else 0]

            return self.create_document(style, x, y, width)
        label_subject = 'self.scene'
        style = \
            [f'{label_attr}: {str(getattr(self.scene, label_attr))}', f'{str(getattr(self.scene, label_attr))}',
             f'{label_attr}',
             f'{str(getattr(self.scene, label_attr))}'][style if style is not None else 0]
        return self.create_document(style, x, y, width)

    def create_document(self, style, x, y, width):
        doc = pyglet.text.document.UnformattedDocument(style)
        doc.set_style(0, len(doc.text), attributes={'color': (255, 255, 255, 255)})
        return pyglet.text.DocumentLabel(
                doc,
                x=x,
                y=y,
                width=width,
                multiline=True,
                batch=self.label_batch,
        )

    def add_static_label(
            self, label_subject, label_attr, placement=None, duration=None, width=None, style=None,
            perishable=None, persistent=None
            ):
        label = self.create_associated_label(label_subject, label_attr, placement, width, style)
        label_id = self.create_label_id()
        if label_subject is None:
            label_subject = 'self'
        if duration is not None:
            self.static_labels[label_id] = {'subject':    label_subject, 'attr': label_attr, 'label': label,
                                            'expiration': self.window.frame_count + duration}
        else:
            self.static_labels[label_id] = {'subject':    label_subject, 'attr': label_attr, 'label': label,
                                            'expiration': None}
        if perishable:
            self.label_bin.append(label_id)
        elif persistent:
            self.label_locker.append(label_id)

    @log_method
    def add_dynamic_label(
            self, label_subject=None, label_attr=None, placement=None, duration=None, width=None,
            style=None, perishable=None, persistent=None
            ):
        label = self.create_associated_label(label_subject, label_attr, placement, width, style)
        label_id = self.create_label_id()
        if label_subject is None:
            label_subject = 'self.scene'
        if duration is not None:
            self.dynamic_labels[label_id] = {'subject':    label_subject, 'attr': label_attr, 'label': label,
                                             'expiration': self.window.frame_count + duration}
        else:
            self.dynamic_labels[label_id] = {'subject':    label_subject, 'attr': label_attr, 'label': label,
                                             'expiration': None}
        if perishable or (perishable is None and persistent is None):
            self.label_bin.append(label_id)
        elif persistent:
            self.label_locker.append(label_id)

    def create_unassociated_label(self, label_text, placement=None, width=500, color=(255, 255, 255, 255)):
        if placement is None:
            x = 100
            y = (self.window.height-100) - (self.label_count * 20)
        else:
            x = placement[0]
            y = placement[1]
        doc = pyglet.text.document.UnformattedDocument(label_text)
        doc.set_style(0, len(label_text), attributes={'color': color})
        return pyglet.text.DocumentLabel(doc, x=x, y=y, width=width, multiline=True, batch=self.label_batch)

    @log_method
    def add_unassociated_label(
            self, label_text, placement=None, duration=None, width=500, color=(255, 255, 255, 255),
            perishable=None, persistent=None
            ):
        self.label_count += 1
        label = self.create_unassociated_label(label_text, placement, width, color)
        label_id = self.create_label_id()
        if duration is not None and persistent:
            self.unassoc_labels[label_id] = {'label':      label,
                                             'expiration': self.scene._frame_count + duration}
            self.label_locker.append(label_id)
        elif perishable:
            self.unassoc_labels[label_id] = {'label': label, 'expiration': None}
            self.label_bin.append(label_id)

    def update_text(self):
        for label_type in self.labels.keys():
            for label_id, info in self.labels[label_type].copy().items():
                if label_type == 'dynamic':
                    info["label"].document.delete_text(0, len(info["label"].text))
                    if info['subject'] != 'self.scene':
                        info["label"].document.insert_text(
                            0, info["attr"] + ': ' + str(
                                    getattr(info['subject'], info["attr"])
                            )
                            )
                    else:
                        info["label"].document.insert_text(
                            0, info["attr"] + ': ' + str(getattr(self.scene, info["attr"]))
                            )
                if info.get('expiration') is not None and info[
                    'expiration'] == self.scene._frame_count and label_id in self.label_locker:
                    self.label_bin.append(self.label_locker.pop(self.label_locker.index(label_id)))
                    info['label'].document.delete_text(0, len(info['label'].text))

    def remove_label(self, label_id):
        # new_batch = pyglet.graphics.Batch()
        # for label_type in self.labels.copy().values():
        #     for info in label_type.copy().values():
        #         if label_type.get(label_id) is None:
        #             for vertex_list in info['label']._vertex_lists:
        #                 self.label_batch.migrate(vertex_list, pyglet.graphics.GL_POINTS, None, new_batch)
        #         elif info['label'] != label_type.copy()[label_id]['label']:
        #             for vertex_list in info['label']._vertex_lists:
        #                 self.label_batch.migrate(vertex_list, pyglet.graphics.GL_POINTS, None, new_batch)
        # self.label_batch = new_batch
        if self.labels['static'].get(label_id) is not None:
            self.delete_entries('static', label_id)
        elif self.labels['dynamic'].get(label_id) is not None:
            self.delete_entries('dynamic', label_id)
        elif self.labels['unassoc'].get(label_id) is not None:
            self.delete_entries('unassoc', label_id)

    # TODO Rename this here and in `remove_label`
    def delete_entries(self, label_type, label_id):
        self.labels[label_type][label_id]['label'].delete()
        self.labels[label_type][label_id] = None
        del self.labels[label_type][label_id]

    def debug_labels(self):
        for l, v in self.scene.element_delegate.__dict__.copy().items():
            self.add_dynamic_label(self.scene.element_delegate, l, width=100000, persistent = True)
            if len(self.dynamic_labels) > 0:
                self.debug_objects.append(list(self.dynamic_labels.keys())[-1])

    def check_debug(self):
        if self.debug and self.debug_objects is None:
            self.debug_objects = []
            self.debug_labels()
        elif not self.debug and self.debug_objects is not None:
            for label_id in self.debug_objects:
                self.remove_label(label_id)
            self.debug_objects = None

    def clear_bin(self):
        if self.label_bin:
            for l in self.label_bin:
                self.remove_label(l)
            self.label_bin = []

    def update(self, dt):
        self.update_text()
        self.clear_bin()
        self.check_debug()

    def draw(self):
        self.label_batch.draw()
        for num, label in self.unassoc_labels.items():
            label['label'].draw()

