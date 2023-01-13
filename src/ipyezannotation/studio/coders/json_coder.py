import json
from typing import Any, cast

from ipyezannotation.studio.coders import BaseCoder
from ipyezannotation.studio.sample import Sample


class JsonCoder(BaseCoder):
    def __init__(self, *, indent=None):
        self.indent = indent

    def encode(self, data: Any) -> bytes:
        return json.dumps(data, indent=self.indent, default=self._default_serialize).encode()

    def decode(self, data: bytes) -> Any:
        return json.loads(data.decode(), object_hook=self._default_deserialize)

    def _default_serialize(self, obj: object) -> dict:
        if type(obj) == bytes:
            return {
                "_type": "bytes",
                "_content": cast(bytes, obj).decode()
            }
        elif isinstance(obj, Sample):
            return {
                "_type": "Sample",
                "_content": self.decode(obj.serialize(self))
            }

        raise TypeError(f"Given object {repr(obj)} is not serializable.")

    def _default_deserialize(self, obj: object) -> Any:
        if not isinstance(obj, dict) or "_type" not in obj:
            return obj

        typename = obj["_type"]

        if typename == "bytes":
            return obj["_content"].encode()
        elif typename == "Sample":
            return Sample.deserialize(self.encode(obj["_content"]), self)

        raise TypeError(f"Given object {repr(obj)} is not deserializable.")
