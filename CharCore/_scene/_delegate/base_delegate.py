from __future__ import annotations

from ...__log__ import log_method

from abc import ABC
import uuid
from typing import Optional, Union

import pyglet


class AbstractDelegate:
    _represents = None

    def __new__(cls):
        return super().__new__(cls)


class Delegate(AbstractDelegate):
    def __new__(cls, scene):
        new_cls = super().__new__(cls)
        if new_cls._represents is not None:
            return new_cls