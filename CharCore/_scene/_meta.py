from __future__ import annotations

from ._delegate import ElementDelegate, BatchDelegate, LabelDelegate, EntityDelegate

from abc import ABC
import logging as _logging

import pymunk

scene_space_meta_instances = {}


class SceneSpaceMeta(type):
    def __new__(cls, name, bases, attrs):
        return type.__new__(cls, name, bases, attrs)
    
    @classmethod
    def _set_world(cls, instance, gravity):
        instance.world = pymunk.Space()
        instance.world.gravity = gravity

        return instance

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)

        if hasattr(instance, 'is_physical') and instance.is_physical:
            gravity = instance.gravity if hasattr(instance, 'gravity') else (0, -1000)
            if str(instance) != "<class 'begingine.core._scene.scene.BaseScene'>":
                _logging.info(f'Setting world for instance {instance}')

            instance = cls._set_world(instance, gravity)
        return instance


class SceneDelegateMeta(type):
    def __new__(cls, name, bases, attrs):
        return type.__new__(cls, name, bases, attrs)

    @classmethod
    def _set_delegates(cls, instance):
        instance.element_delegate = ElementDelegate
        instance.batch_delegate = BatchDelegate
        instance.label_delegate = LabelDelegate
        instance.entity_delegate = EntityDelegate
        return instance

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)

        instance = cls._set_delegates(instance)

        return instance


class SceneMeta(type('SceneMeta', (SceneSpaceMeta, SceneDelegateMeta, ), {})):
    def __new__(cls, name, bases, attrs):
        attrs['_dispatcher'] = None
        return type.__new__(cls, name, bases, attrs)

    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)
