from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from enum import Enum, auto
from json import dumps
from typing import Literal, Union

from connectrpc.request import RequestContext
from elimity.insights.common.v1alpha1.common_pb import Entity, Relationship
from elimity.insights.common.v1alpha1.common_pb import Value as CommonValue
from elimity.insights.customgateway.v1alpha2.customgateway_connect import (
    ServiceASGIApplication,
)
from elimity.insights.customgateway.v1alpha2.customgateway_pb import (
    Level as GatewayLevel,
)
from elimity.insights.customgateway.v1alpha2.customgateway_pb import (
    Log,
    MetaRequest,
    MetaResponse,
    PerformImportRequest,
    PerformImportResponse,
)
from protobuf import Oneof
from protobuf.wkt import Empty, Timestamp
from protobuf.wkt import Value as StructValue


@dataclass
class BooleanValue:
    value: bool


@dataclass
class CursorItem:
    cursor: object


@dataclass
class DateTimeValue:
    value: datetime


@dataclass
class DateValue:
    value: date


@dataclass
class EntityItem:
    attribute_assignments: dict[str, "Value"]
    id: str
    name: str
    type: str


@dataclass
class LogItem:
    level: "Level"
    message: str


@dataclass
class RelationshipItem:
    attribute_assignments: dict[str, "Value"]
    from_entity_id: str
    from_entity_type: str
    to_entity_id: str
    to_entity_type: str


Item = Union[CursorItem, EntityItem, LogItem, RelationshipItem]


class Level(Enum):
    ALERT = auto()
    INFO = auto()


@dataclass
class NumberValue:
    value: float


@dataclass
class StringValue:
    value: str


@dataclass
class TimeValue:
    value: time


Value = Union[
    BooleanValue, DateValue, DateTimeValue, NumberValue, StringValue, TimeValue
]


def app(
    fun: Callable[[object, dict[str, object]], AsyncIterator[Item]],
    initial_cursor: object,
    version: str,
) -> ServiceASGIApplication:
    service = _Service(fun, initial_cursor, version)
    return ServiceASGIApplication(service)


class _Service:
    def __init__(
        self,
        fun: Callable[[object, dict[str, object]], AsyncIterator[Item]],
        initial_cursor: object,
        version: str,
    ):
        self._fun = fun
        self._initial_cursor = initial_cursor
        self._version = version

    async def meta(
        self, request: MetaRequest, ctx: RequestContext[MetaRequest, MetaResponse]
    ) -> MetaResponse:
        initial_cursor = _make_struct_value(self._initial_cursor)
        return MetaResponse(initial_cursor=initial_cursor, version=self._version)

    def perform_import(
        self,
        req: PerformImportRequest,
        ctx: RequestContext[PerformImportRequest, PerformImportResponse],
    ) -> AsyncIterator[PerformImportResponse]:
        expected_version = self._version
        actual_version = req.version
        if expected_version != actual_version:
            message = f"expected request to have version {expected_version} instead of {actual_version}"
            raise BaseException(message)
        cursor = req.cursor.to_python() if req.cursor is not None else None
        fields: dict[str, object] = {}
        for key, value in req.fields.items():
            fields[key] = value.to_python()
        items = self._fun(cursor, fields)
        return _generate_responses(items)


async def _generate_responses(
    items: AsyncIterator[Item],
) -> AsyncIterator[PerformImportResponse]:
    async for item in items:
        yield _make_response(item)


def _make_assignments(assignments: dict[str, Value]) -> dict[str, CommonValue]:
    ass: dict[str, CommonValue] = {}
    for key, value in assignments.items():
        ass[key] = _make_common_value(value)
    return ass


def _make_common_value(value: Value) -> CommonValue:
    if isinstance(value, BooleanValue):
        boolean_oneof = Oneof[Literal["boolean"], bool]("boolean", value.value)
        return CommonValue(value=boolean_oneof)

    if isinstance(value, DateTimeValue):
        timestamp = _make_timestamp(value.value)
        date_time_oneof = Oneof[Literal["date_time"], Timestamp]("date_time", timestamp)
        return CommonValue(value=date_time_oneof)

    if isinstance(value, DateValue):
        date = value.value
        dat = datetime(date.year, date.month, date.day)
        timestamp = _make_timestamp(dat)
        date_oneof = Oneof[Literal["date"], Timestamp]("date", timestamp)
        return CommonValue(value=date_oneof)

    if isinstance(value, NumberValue):
        number_oneof = Oneof[Literal["number"], float]("number", value.value)
        return CommonValue(value=number_oneof)

    if isinstance(value, StringValue):
        string_oneof = Oneof[Literal["string"], str]("string", value.value)
        return CommonValue(value=string_oneof)

    if isinstance(value, TimeValue):
        time = value.value
        dat = datetime(1, 1, 1, time.hour, time.minute, time.second)
        timestamp = _make_timestamp(dat)
        time_oneof = Oneof[Literal["time"], Timestamp]("time", timestamp)
        return CommonValue(value=time_oneof)


def _make_level(level: Level) -> GatewayLevel:
    empty = Empty()
    if level is Level.ALERT:
        alert_oneof = Oneof[Literal["alert"], Empty]("alert", empty)
        return GatewayLevel(value=alert_oneof)
    info_oneof = Oneof[Literal["info"], Empty]("info", empty)
    return GatewayLevel(value=info_oneof)


def _make_response(item: Item) -> PerformImportResponse:
    if isinstance(item, CursorItem):
        cursor = _make_struct_value(item.cursor)
        cursor_oneof = Oneof[Literal["cursor"], StructValue]("cursor", cursor)
        return PerformImportResponse(value=cursor_oneof)

    if isinstance(item, EntityItem):
        assignments = _make_assignments(item.attribute_assignments)
        entity = Entity(
            attribute_assignments=assignments,
            id=item.id,
            name=item.name,
            type=item.type,
        )
        entity_oneof = Oneof[Literal["entity"], Entity]("entity", entity)
        return PerformImportResponse(value=entity_oneof)

    if isinstance(item, LogItem):
        level = _make_level(item.level)
        log = Log(level=level, message=item.message)
        log_oneof = Oneof[Literal["log"], Log]("log", log)
        return PerformImportResponse(value=log_oneof)

    if isinstance(item, RelationshipItem):
        assignments = _make_assignments(item.attribute_assignments)
        relationship = Relationship(
            attribute_assignments=assignments,
            from_entity_id=item.from_entity_id,
            from_entity_type=item.from_entity_type,
            to_entity_id=item.to_entity_id,
            to_entity_type=item.to_entity_type,
        )
        relationship_oneof = Oneof[Literal["relationship"], Relationship](
            "relationship", relationship
        )
        return PerformImportResponse(value=relationship_oneof)


def _make_struct_value(value: object) -> StructValue:
    json = dumps(value)
    return StructValue.from_json(json)


def _make_timestamp(dt: datetime) -> Timestamp:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return Timestamp.from_datetime(dt)
