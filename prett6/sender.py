from PySide6.QtCore import QObject, Signal

__all__ = ('SignalSender', 'connect_with')


class SignalWrapper(QObject):
    signal = Signal(object)


class SignalSender:
    def __init__(self):
        self.signal = SignalWrapper()
        self.last_emit = None
        self.last_error = []

    def emit(self, *args, **kwargs):
        self.last_emit = args, kwargs
        self.last_error.clear()

        # 添加检查以避免访问已删除的信号实例
        try:
            self.signal.signal.emit((args, kwargs))
        except RuntimeError as e:
            if "was already deleted" in str(e):
                # 信号实例已被删除，记录警告并返回
                import logging
                logging.warning("Attempted to emit deleted signal: %s", str(e))
                return
            else:
                # 其他运行时错误，重新抛出
                raise

        if self.last_error:
            raise self.last_error[0]

    def connect(self, func, *args, **kwargs):
        last_error = self.last_error

        def slot_func(data, *_):
            try:

                if len(kwargs):
                    k = data[1].copy()
                    k.updata(kwargs)
                else:
                    k = data[1]

                return func(*(args + data[0]), **k)
            except BaseException as e:
                last_error.append(e)

        slot_func.__name__ = getattr(func, '__name__', '<Lambda>')

        self.signal.signal.connect(slot_func)

    def emit_if_changed(self, *args, **kwargs):
        emit_value = (args, kwargs)
        if self.last_emit != emit_value:
            self.emit(*args, **kwargs)

    @property
    def has_emitted(self):
        return self.last_emit is not None

    @property
    def last_value(self):
        if self.last_emit is None:
            return None
        else:
            args, kwargs = self.last_emit

            if len(kwargs) == 0:
                if len(args) == 0:
                    return None
                elif len(args) == 1:
                    return args[0]
                else:
                    return args
            else:
                return self.last_emit


def connect_with(signal: SignalSender, *args, **kwargs):
    def pack_func(func):
        signal.connect(func, *args, **kwargs)
        return func

    return pack_func
