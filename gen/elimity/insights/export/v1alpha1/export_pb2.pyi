from elimity.insights.common.v1alpha1 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExportRequest(_message.Message):
    __slots__ = ("api_token_id", "api_token_secret", "targets")
    API_TOKEN_ID_FIELD_NUMBER: _ClassVar[int]
    API_TOKEN_SECRET_FIELD_NUMBER: _ClassVar[int]
    TARGETS_FIELD_NUMBER: _ClassVar[int]
    api_token_id: int
    api_token_secret: bytes
    targets: _containers.RepeatedCompositeFieldContainer[Target]
    def __init__(self, api_token_id: _Optional[int] = ..., api_token_secret: _Optional[bytes] = ..., targets: _Optional[_Iterable[_Union[Target, _Mapping]]] = ...) -> None: ...

class ExportResponse(_message.Message):
    __slots__ = ("item", "target_index")
    ITEM_FIELD_NUMBER: _ClassVar[int]
    TARGET_INDEX_FIELD_NUMBER: _ClassVar[int]
    item: Item
    target_index: int
    def __init__(self, item: _Optional[_Union[Item, _Mapping]] = ..., target_index: _Optional[int] = ...) -> None: ...

class Filter(_message.Message):
    __slots__ = ("entity_type", "relationship_type")
    ENTITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    RELATIONSHIP_TYPE_FIELD_NUMBER: _ClassVar[int]
    entity_type: str
    relationship_type: RelationshipType
    def __init__(self, entity_type: _Optional[str] = ..., relationship_type: _Optional[_Union[RelationshipType, _Mapping]] = ...) -> None: ...

class Item(_message.Message):
    __slots__ = ("entity", "relationship")
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    RELATIONSHIP_FIELD_NUMBER: _ClassVar[int]
    entity: _common_pb2.Entity
    relationship: _common_pb2.Relationship
    def __init__(self, entity: _Optional[_Union[_common_pb2.Entity, _Mapping]] = ..., relationship: _Optional[_Union[_common_pb2.Relationship, _Mapping]] = ...) -> None: ...

class RelationshipType(_message.Message):
    __slots__ = ("from_entity_type", "to_entity_type")
    FROM_ENTITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    TO_ENTITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    from_entity_type: str
    to_entity_type: str
    def __init__(self, from_entity_type: _Optional[str] = ..., to_entity_type: _Optional[str] = ...) -> None: ...

class Target(_message.Message):
    __slots__ = ("filter", "source_id")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    filter: Filter
    source_id: int
    def __init__(self, filter: _Optional[_Union[Filter, _Mapping]] = ..., source_id: _Optional[int] = ...) -> None: ...
