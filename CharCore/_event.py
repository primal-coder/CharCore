# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# Copyright (c) 2008-2022 pyglet contributors
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

"""Event dispatch framework.

All objects that produce events in pyglet implement :py:class:`~pyglet._event._EventDispatcher`,
providing a consistent interface for registering and manipulating _event
handlers.  A commonly used _event dispatcher is `pyglet.window.Window`.

Event types
===========

For each _event dispatcher there is a set of events that it dispatches; these
correspond with the type of _event handlers you can attach.  Event types are
identified by their name, for example, ''on_resize''.  If you are creating a
new class which implements :py:class:`~pyglet._event._EventDispatcher`, you must call
`_EventDispatcher._register_event_type` for each _event type.

Attaching _event handlers
========================

An _event handler is simply a function or method.  You can attach an _event
handler by setting the appropriate function on the instance::

    def on_resize(width, height):
        # ...
    dispatcher.on_resize = on_resize

There is also a convenience decorator that reduces typing::

    @dispatcher._event
    def on_resize(width, height):
        # ...

You may prefer to subclass and override the _event handlers instead::

    class MyDispatcher(DispatcherClass):
        def on_resize(self, width, height):
            # ...

Event handler stack
===================

When attaching an _event handler to a dispatcher using the above methods, it
replaces any existing handler (causing the original handler to no longer be
called).  Each dispatcher maintains a stack of _event handlers, allowing you to
insert an _event handler "above" the existing one rather than replacing it.

There are two main use cases for "pushing" _event handlers:

* Temporarily intercepting the events coming from the dispatcher by pushing a
  custom set of handlers onto the dispatcher, then later "popping" them all
  off at once.
* Creating "chains" of _event handlers, where the _event propagates from the
  top-most (most recently added) handler to the bottom, until a handler
  takes care of it.

Use `_EventDispatcher._push_handlers` to create a new level in the stack and
attach handlers to it.  You can push several handlers at once::

    dispatcher._push_handlers(on_resize, on_key_press)

If your function handlers have different names to the events they handle, use
keyword arguments::

    dispatcher._push_handlers(on_resize=my_resize, on_key_press=my_key_press)

After an _event handler has processed an _event, it is passed on to the
next-lowest _event handler, unless the handler returns `_EVENT_HANDLED`, which
prevents further propagation.

To remove all handlers on the top stack level, use
`_EventDispatcher._pop_handlers`.

Note that any handlers pushed onto the stack have precedence over the
handlers set directly on the instance (for example, using the methods
described in the previous section), regardless of when they were set.
For example, handler ``foo`` is called before handler ``bar`` in the following
example::

    dispatcher._push_handlers(on_resize=foo)
    dispatcher.on_resize = bar

Dispatching events
==================

pyglet uses a single-threaded model for all application code.  Event
handlers are only ever invoked as a result of calling
_EventDispatcher.dispatch_events`.

It is up to the specific _event dispatcher to queue relevant events until they
can be dispatched, at which point the handlers are called in the order the
events were originally generated.

This implies that your application runs with a main loop that continuously
updates the application state and checks for new events::

    while True:
        dispatcher.dispatch_events()
        # ... additional per-frame processing

Not all _event dispatchers require the call to ``dispatch_events``; check with
the particular class documentation.

.. note::

    In order to prevent issues with garbage collection, the
    :py:class:`~pyglet._event._EventDispatcher` class only holds weak
    references to pushed _event handlers. That means the following example
    will not work, because the pushed object will fall out of scope and be
    collected::

        dispatcher._push_handlers(MyHandlerClass())

    Instead, you must make sure to keep a reference to the object before pushing
    it. For example::

        my_handler_instance = MyHandlerClass()
        dispatcher._push_handlers(my_handler_instance)

"""

import inspect as _inspect

from functools import partial as _partial
from weakref import WeakMethod as _WeakMethod

_EVENT_HANDLED = True
_EVENT_UNHANDLED = None


class _EventException(Exception):
    """An exception raised when an _event handler could not be attached.
    """
    pass


class EventDispatcher:
    """Generic _event dispatcher interface.

    See the module docstring for usage.
    """
    # Placeholder empty stack; real stack is created only if needed
    _event_stack = ()

    @classmethod
    def register_event_type(cls, name):
        """Register an _event type with the dispatcher.

        Registering _event types allows the dispatcher to validate _event
        handler names as they are attached, and to search attached objects for
        suitable handlers.

        :Parameters:
            `name` : str
                Name of the _event to register.

        """
        if not hasattr(cls, '_event_types'):
            cls._event_types = []
        cls._event_types.append(name)
        return name

    def push_handlers(self, *args, **kwargs):
        """Push a level onto the top of the handler stack, then attach zero or
        more _event handlers.

        If keyword arguments are given, they name the _event type to attach.
        Otherwise, a callable's `__name__` attribute will be used.  Any other
        object may also be specified, in which case it will be searched for
        callables with _event names.
        """
        # Create _event stack if necessary
        if type(self._event_stack) is tuple:
            self._event_stack = []

        # Place dict full of new handlers at beginning of stack
        self._event_stack.insert(0, {})
        self._set_handlers(*args, **kwargs)

    def _get_handlers(self, args, kwargs):
        """Implement handler matching on arguments for _set_handlers and
        _remove_handlers.
        """
        for obj in args:
            if _inspect.isroutine(obj):
                # Single magically named function
                name = obj.__name__
                if name not in self._event_types:
                    raise _EventException('Unknown _event "%s"' % name)
                if _inspect.ismethod(obj):
                    yield name, _WeakMethod(obj, _partial(self._remove_handler, name))
                else:
                    yield name, obj
            else:
                # Single instance with magically named methods
                for name in dir(obj):
                    if name in self._event_types:
                        meth = getattr(obj, name)
                        yield name, _WeakMethod(meth, _partial(self._remove_handler, name))

        for name, handler in kwargs.items():
            # Function for handling given _event (no magic)
            if name not in self._event_types:
                raise _EventException('Unknown _event "%s"' % name)
            if _inspect.ismethod(handler):
                yield name, _WeakMethod(handler, _partial(self._remove_handler, name))
            else:
                yield name, handler

    def _set_handlers(self, *args, **kwargs):
        """Attach one or more _event handlers to the top level of the handler
        stack.

        See :py:meth:`~pyglet._event._EventDispatcher._push_handlers` for the accepted argument types.
        """
        # Create _event stack if necessary
        if type(self._event_stack) is tuple:
            self._event_stack = [{}]

        for name, handler in self._get_handlers(args, kwargs):
            self._set_handler(name, handler)

    def _set_handler(self, name, handler):
        """Attach a single _event handler.

        :Parameters:
            `name` : str
                Name of the _event type to attach to.
            `handler` : callable
                Event handler to attach.

        """
        # Create _event stack if necessary
        if type(self._event_stack) is tuple:
            self._event_stack = [{}]

        self._event_stack[0][name] = handler

    def _pop_handlers(self):
        """Pop the top level of _event handlers off the stack.
        """
        assert self._event_stack and 'No handlers pushed'

        del self._event_stack[0]

    def remove_handlers(self, *args, **kwargs):
        """Remove _event handlers from the _event stack.

        See :py:meth:`~pyglet._event._EventDispatcher._push_handlers` for the
        accepted argument types. All handlers are removed from the first stack
        frame that contains any of the given handlers. No error is raised if
        any handler does not appear in that frame, or if no stack frame
        contains any of the given handlers.

        If the stack frame is empty after removing the handlers, it is
        removed from the stack.  Note that this interferes with the expected
        symmetry of :py:meth:`~pyglet._event._EventDispatcher._push_handlers` and
        :py:meth:`~pyglet._event._EventDispatcher._pop_handlers`.
        """
        handlers = list(self._get_handlers(args, kwargs))

        # Find the first stack frame containing any of the handlers
        def find_frame():
            for frame in self._event_stack:
                for name, handler in handlers:
                    try:
                        if frame[name] == handler:
                            return frame
                    except KeyError:
                        pass

        frame = find_frame()

        # No frame matched; no error.
        if not frame:
            return

        # Remove each handler from the frame.
        for name, handler in handlers:
            try:
                if frame[name] == handler:
                    del frame[name]
            except KeyError:
                pass

        # Remove the frame if it's empty.
        if not frame:
            self._event_stack.remove(frame)

    def _remove_handler(self, name, handler):
        """Remove a single _event handler.

        The given _event handler is removed from the first handler stack frame
        it appears in.  The handler must be the exact same callable as passed
        to `_set_handler`, `_set_handlers` or
        :py:meth:`~pyglet._event._EventDispatcher._push_handlers`; and the name
        must match the _event type it is bound to.

        No error is raised if the _event handler is not set.

        :Parameters:
            `name` : str
                Name of the _event type to remove.
            `handler` : callable
                Event handler to remove.
        """
        for frame in self._event_stack:
            try:
                if frame[name] == handler:
                    del frame[name]
                    break
            except KeyError:
                pass

    def _remove_handler(self, name, handler):
        """Used internally to remove all handler instances for the given _event name.

        This is normally called from a dead ``_WeakMethod`` to remove itself from the
        _event stack.
        """

        # Iterate over a copy as we might mutate the list
        for frame in list(self._event_stack):

            if name in frame:
                try:
                    if frame[name] == handler:
                        del frame[name]
                        if not frame:
                            self._event_stack.remove(frame)
                except TypeError:
                    # weakref is already dead
                    pass

    def dispatch_event(self, event_type, *args):
        """Dispatch a single _event to the attached handlers.

        The _event is propagated to all handlers from from the top of the stack
        until one returns `_EVENT_HANDLED`.  This method should be used only by
        :py:class:`~pyglet._event._EventDispatcher` implementors; applications should call
        the ``dispatch_events`` method.

        Since pyglet 1.2, the method returns `_EVENT_HANDLED` if an _event
        handler returned `_EVENT_HANDLED` or `_EVENT_UNHANDLED` if all events
        returned `_EVENT_UNHANDLED`.  If no matching _event handlers are in the
        stack, ``False`` is returned.

        :Parameters:
            `event_type` : str
                Name of the _event.
            `args` : sequence
                Arguments to pass to the _event handler.

        :rtype: bool or None
        :return: (Since pyglet 1.2) `_EVENT_HANDLED` if an _event handler
            returned `_EVENT_HANDLED`; `_EVENT_UNHANDLED` if one or more _event
            handlers were invoked but returned only `_EVENT_UNHANDLED`;
            otherwise ``False``.  In pyglet 1.1 and earlier, the return value
            is always ``None``.

        """
        assert hasattr(self, '_event_types'), (
            "No events registered on this _EventDispatcher. "
            "You need to register events with the class method "
            "_EventDispatcher._register_event_type('event_name')."
        )
        assert event_type in self._event_types, \
            "%r not found in %r._event_types == %r" % (event_type, self, self._event_types)

        invoked = False

        # Search handler stack for matching _event handlers
        for frame in list(self._event_stack):
            handler = frame.get(event_type, None)
            if not handler:
                continue
            if isinstance(handler, _WeakMethod):
                handler = handler()
                assert handler is not None
            try:
                invoked = True
                if handler(*args):
                    return _EVENT_HANDLED
            except TypeError as exception:
                self._raise_dispatch_exception(event_type, args, handler, exception)

        # Check instance for an _event handler
        try:
            if getattr(self, event_type)(*args):
                return _EVENT_HANDLED
        except AttributeError as e:
            event_op = getattr(self, event_type, None)
            if callable(event_op):
                raise e
        except TypeError as exception:
            self._raise_dispatch_exception(event_type, args, getattr(self, event_type), exception)
        else:
            invoked = True

        if invoked:
            return _EVENT_UNHANDLED

        return False

    @staticmethod
    def _raise_dispatch_exception(event_type, args, handler, exception):
        # A common problem in applications is having the wrong number of
        # arguments in an _event handler.  This is caught as a TypeError in
        # _dispatch_event but the error message is obfuscated.
        #
        # Here we check if there is indeed a mismatch in argument count,
        # and construct a more useful exception message if so.  If this method
        # doesn't find a problem with the number of arguments, the error
        # is re-raised as if we weren't here.

        n_args = len(args)

        # Inspect the handler
        argspecs = _inspect.getfullargspec(handler)
        handler_args = argspecs.args
        handler_varargs = argspecs.varargs
        handler_defaults = argspecs.defaults

        n_handler_args = len(handler_args)

        # Remove "self" arg from handler if it's a bound method
        if _inspect.ismethod(handler) and handler.__self__:
            n_handler_args -= 1

        # Allow *args varargs to overspecify arguments
        if handler_varargs:
            n_handler_args = max(n_handler_args, n_args)

        # Allow default values to overspecify arguments
        if n_handler_args > n_args >= n_handler_args - len(handler_defaults) and handler_defaults:
            n_handler_args = n_args

        if n_handler_args != n_args:
            if _inspect.isfunction(handler) or _inspect.ismethod(handler):
                descr = f"'{handler.__name__}' at {handler.__code__.co_filename}:{handler.__code__.co_firstlineno}"
            else:
                descr = repr(handler)

            raise TypeError(f"The '{event_type}' _event was dispatched with {len(args)} arguments,\n"
                            f"but your handler {descr} accepts only {n_handler_args} arguments.")

        else:
            raise exception

    def _event(self, *args):
        """Function decorator for an _event handler.

        Usage::

            win = window.Window()

            @win._event
            def on_resize(self, width, height):
                # ...

        or::

            @win._event('on_resize')
            def foo(self, width, height):
                # ...

        """
        if len(args) == 0:  # @window._event()
            def decorator(func):
                func_name = func.__name__
                self._set_handler(func_name, func)
                return func

            return decorator
        elif _inspect.isroutine(args[0]):  # @window._event
            func = args[0]
            name = func.__name__
            self._set_handler(name, func)
            return args[0]
        elif isinstance(args[0], str):  # @window._event('on_resize')
            name = args[0]

            def decorator(func):
                self._set_handler(name, func)
                return func

            return decorator