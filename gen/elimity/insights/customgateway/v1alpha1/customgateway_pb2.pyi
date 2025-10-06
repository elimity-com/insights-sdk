from elimity.insights.common.v1alpha1 import common_pb2 as _common_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Level(_message.Message):
    __slots__ = ("alert", "info")
    ALERT_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    alert: _empty_pb2.Empty
    info: _empty_pb2.Empty
    def __init__(self, alert: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., info: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class Log(_message.Message):
    __slots__ = ("level", "message")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    level: Level
    message: str
    def __init__(self, level: _Optional[_Union[Level, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class PerformImportRequest(_message.Message):
    __slots__ = ("fields",)
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _struct_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    fields: _containers.MessageMap[str, _struct_pb2.Value]
    def __init__(self, fields: _Optional[_Mapping[str, _struct_pb2.Value]] = ...) -> None: ...

class PerformImportResponse(_message.Message):
    __slots__ = ("entity", "log", "relationship")
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    RELATIONSHIP_FIELD_NUMBER: _ClassVar[int]
    entity: _common_pb2.Entity
    log: Log
    relationship: _common_pb2.Relationship
    def __init__(self, entity: _Optional[_Union[_common_pb2.Entity, _Mapping]] = ..., log: _Optional[_Union[Log, _Mapping]] = ..., relationship: _Optional[_Union[_common_pb2.Relationship, _Mapping]] = ...) -> None: ...
