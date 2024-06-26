import codecs
import enum
import json
import os
import time
import typing

from . import AbstractProperty
from . import ChangedInterface
from . import DictItemInterface
from . import DictValueModel
from . import ListItemInterface
from . import StringFloatItemInterface
from . import StringIntItemInterface
from . import StringItemInterface
from . import StringProperty
from . import ValueModel


class SaveInterface(ValueModel):
    def load(self, check_key: str, check_value: str):
        if not os.path.exists(self.filename):
            raise FileNotFoundError('Setting File [{}] Not Found'.format(self.filename))

        try:
            with codecs.open(self.filename, 'r', encoding='utf-8') as f:
                obj = json.load(f)
                assert isinstance(obj, dict)
                assert obj.get(check_key, None) == check_value
                self.value = obj
        except AssertionError as e:
            raise e
        except ValueError as e:
            raise e

    def save(self):
        with codecs.open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.value, f, indent=2, ensure_ascii=False)

    @property
    def path(self) -> typing.Optional[str]:
        return None

    @property
    def name(self) -> typing.Optional[str]:
        return None

    @property
    def filename(self):
        return os.path.join(self.path, self.name)

    @property
    def is_existing(self):
        return os.path.exists(self.filename)


class AbstractProject(DictValueModel, SaveInterface, ChangedInterface):
    def get_value(self) -> dict:
        return self._create(dict)

    def set_value(self, value):
        self.value.clear()
        self.value.update(value)
        self.changed.emit(self.value)

    def get_property(self, name) -> object:
        return self.value.get(name)

    def set_property(self, name, value):
        self.value.update({name: value})
        self.changed.emit(self.value)

    # children property
    @property
    def children(self) -> typing.List['AbstractProjectItem']:
        return self._create(list)

    # name property
    def __setattr__(self, key: str, value):
        if isinstance(value, AbstractProjectItem):
            value.name = key
        super().__setattr__(key, value)


class AbstractProjectItem(StringItemInterface):
    def __init__(self, parent: AbstractProject = None):
        self.parent = parent
        if parent is not None:
            self.parent.children.append(self)
            self.parent.changed.connect(self.check_change)

    def get_value(self):
        if self.parent is not None:
            return self.parent.get_property(self.name)
        else:
            return self.self_storage

    def set_value(self, value):
        if self.parent is not None:
            self.parent.set_property(self.name, value)
        else:
            self.self_storage = value
            self.check_change()

    @property
    def name(self) -> str:
        return self._create(str)

    @name.setter
    def name(self, value):
        self.assign(value)

    @property
    def self_storage(self):
        return self._create(lambda: None)

    @self_storage.setter
    def self_storage(self, value):
        self.assign(value)


class DictProjectItem(AbstractProjectItem, DictItemInterface):
    pass


class ListProjectItem(AbstractProjectItem, ListItemInterface):
    pass


class StringProjectItem(AbstractProjectItem):
    pass


class IntProjectItem(AbstractProjectItem, StringIntItemInterface):
    pass


class FloatProjectItem(AbstractProjectItem, StringFloatItemInterface):
    pass


class TimePointItem(StringProjectItem):

    def __init__(self, parent, t_format='%Y-%m-%d %H:%M:%S'):
        super().__init__(parent)
        self.t_format = t_format

    class TimePointProperty(StringProperty):
        def __init__(self, parent, t_format):
            super().__init__(parent)
            self.t_format = t_format

        def update(self):
            self.value = time.strftime(self.t_format)

    @property
    def time(self):
        return self._create(TimePointItem.TimePointProperty, args=(self, self.t_format))


class Enum(enum.Enum):
    @classmethod
    def get_values_list(cls) -> []:
        res = []
        for s in cls:
            res.append(s.value)
        return res

    @classmethod
    def get_key_by_value(cls, value: str, default_value=None):
        for s in cls:
            if s.value == value:
                return s
        else:
            return default_value

    def __eq__(self, s: str):
        return self.name == s


class EnumValueModel(ValueModel):
    @property
    def value(self):
        return self.get_value()

    @value.setter
    def value(self, value):
        self.set_value(value)


class EnumItem(AbstractProjectItem, StringItemInterface):
    def __init__(self, parent, e=None):
        super().__init__(parent)
        self.enum = e

    class EnumProperty(AbstractProperty, EnumValueModel):
        def __init__(self, parent, e: Enum):
            super().__init__(parent)
            self.enum = e

        def get_value(self):
            text = self.parent.get_string()
            return self.enum.get_key_by_value(text)

        def set_value(self, value: Enum):
            self.parent.set_value(value.value)

    @property
    def type(self):
        return self._create(self.EnumProperty, args=(self, self.enum))
