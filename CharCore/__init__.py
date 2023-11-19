from . import __log__
from .__log__ import log_method as _log_method

_log = __log__.logger

def __submodules__():
    """Returns a list of submodules in this package."""
    import os
    return [f[:-3] for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.py') and f != '__init__.py']

from CharTurn import Turn, TurnManager, TurnRecord

from ._scene import BaseScene, Screen, Camera, CenteredCamera
from ._window import MainWindow
from ._event import EventDispatcher

