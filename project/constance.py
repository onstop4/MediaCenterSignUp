from datetime import time
from json import dumps, loads

import redis
from constance import config, settings, signals, utils
from constance.backends import Backend


class ImprovedRedisBackend(Backend):
    valid_types = ("str", "int", "bool", "time")
    valid_types_to_convert = ("time",)

    def __init__(self):
        super().__init__()
        self._prefix = settings.REDIS_PREFIX
        connection_cls = settings.REDIS_CONNECTION_CLASS
        if connection_cls is not None:
            self._rd = utils.import_module_attr(connection_cls)()
        else:
            if isinstance(settings.REDIS_CONNECTION, str):
                self._rd = redis.from_url(settings.REDIS_CONNECTION)
            else:
                self._rd = redis.Redis(**settings.REDIS_CONNECTION)

    def add_prefix(self, key):
        return str(self._prefix) + str(key)

    def get(self, key):
        value = self._rd.get(self.add_prefix(key))
        if value:
            return self.convert_from_dict(loads(value))

        return None

    def mget(self, keys):
        if not keys:
            return
        prefixed_keys = [self.add_prefix(key) for key in keys]
        for key, value in zip(keys, self._rd.mget(prefixed_keys)):
            if value:
                yield key, self.convert_from_dict(loads(value))

    def set(self, key, value):
        old_value = self.get(key)
        self._rd.set(self.add_prefix(key), dumps(self.convert_to_dict(value)))
        signals.config_updated.send(
            sender=config, key=key, old_value=old_value, new_value=value
        )

    def convert_to_dict(self, value):
        type_str = type(value).__name__
        if type_str in self.valid_types:
            if type_str in self.valid_types_to_convert:
                value = str(value)
            return {"type": type_str, "value": value}
        raise TypeError(f"Unsupported type '{type(value)}'")

    def convert_from_dict(self, dictionary):
        type_str = dictionary["type"]
        value = dictionary["value"]
        if type_str in self.valid_types:
            if type_str == "time":
                value = time(*(int(i) for i in value.split(":")))
            return value
        raise ValueError(f"Unrecognized type '{type_str}'")
