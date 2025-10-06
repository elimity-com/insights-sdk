from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Entity(_message.Message):
    __slots__ = ("attribute_assignments", "id", "name", "type")
    class AttributeAssignmentsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Value, _Mapping]] = ...) -> None: ...
    ATTRIBUTE_ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    attribute_assignments: _containers.MessageMap[str, Value]
    id: str
    name: str
    type: str
    def __init__(self, attribute_assignments: _Optional[_Mapping[str, Value]] = ..., id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class Relationship(_message.Message):
    __slots__ = ("attribute_assignments", "from_entity_id", "from_entity_type", "to_entity_id", "to_entity_type")
    class AttributeAssignmentsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Value, _Mapping]] = ...) -> None: ...
    ATTRIBUTE_ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    FROM_ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_ENTITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    TO_ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    TO_ENTITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    attribute_assignments: _containers.MessageMap[str, Value]
    from_entity_id: str
    from_entity_type: str
    to_entity_id: str
    to_entity_type: str
    def __init__(self, attribute_assignments: _Optional[_Mapping[str, Value]] = ..., from_entity_id: _Optional[str] = ..., from_entity_type: _Optional[str] = ..., to_entity_id: _Optional[str] = ..., to_entity_type: _Optional[str] = ...) -> None: ...

class Value(_message.Message):
    __slots__ = ("boolean", "date", "date_time", "number", "string", "time")
    BOOLEAN_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    DATE_TIME_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    STRING_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    boolean: bool
    date: _timestamp_pb2.Timestamp
    date_time: _timestamp_pb2.Timestamp
    number: float
    string: str
    time: _timestamp_pb2.Timestamp
    def __init__(self, boolean: bool = ..., date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., date_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., number: _Optional[float] = ..., string: _Optional[str] = ..., time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
