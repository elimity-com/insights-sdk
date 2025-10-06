from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from datetime import date, datetime, time
from enum import Enum, auto
from typing import Union

from connectrpc.request import RequestContext
from elimity.insights.common.v1alpha1.common_pb2 import Entity, Relationship
from elimity.insights.common.v1alpha1.common_pb2 import Value as CommonValue
from elimity.insights.customgateway.v1alpha1.customgateway_connect import (
    ServiceASGIApplication,
)
from elimity.insights.customgateway.v1alpha1.customgateway_pb2 import (
    Level as GatewayLevel,
)
from elimity.insights.customgateway.v1alpha1.customgateway_pb2 import (
    Log,
    PerformImportRequest,
    PerformImportResponse,
)
from google.protobuf.empty_pb2 import Empty
from google.protobuf.json_format import MessageToDict
from google.protobuf.timestamp_pb2 import Timestamp


@dataclass
class BooleanValue:
    value: bool


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


Item = Union[EntityItem, LogItem, RelationshipItem]


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
    fun: Callable[[dict[str, object]], AsyncIterator[Item]],
) -> ServiceASGIApplication:
    service = _Service(fun)
    return ServiceASGIApplication(service)


class _Service:
    def __init__(self, fun: Callable[[dict[str, object]], AsyncIterator[Item]]):
        self._fun = fun

    def perform_import(
        self, req: PerformImportRequest, ctx: RequestContext[object, object]
    ) -> AsyncIterator[PerformImportResponse]:
        fields: dict[str, object] = {}
        for key, value in req.fields.items():
            fields[key] = MessageToDict(value)
        items = self._fun(fields)
        return _generate_responses(items)


async def _generate_responses(
    items: AsyncIterator[Item],
) -> AsyncIterator[PerformImportResponse]:
    async for item in items:
        yield _make_response(item)


def _make_assignments(assignments: dict[str, Value]) -> dict[str, CommonValue]:
    ass: dict[str, CommonValue] = {}
    for key, value in assignments.items():
        ass[key] = _make_value(value)
    return ass


def _make_response(item: Item) -> PerformImportResponse:
    if isinstance(item, EntityItem):
        assignments = _make_assignments(item.attribute_assignments)
        entity = Entity(
            attribute_assignments=assignments,
            id=item.id,
            name=item.name,
            type=item.type,
        )
        return PerformImportResponse(entity=entity)

    if isinstance(item, LogItem):
        empty = Empty()
        level = (
            GatewayLevel(alert=empty)
            if item.level is Level.ALERT
            else GatewayLevel(info=empty)
        )
        log = Log(level=level, message=item.message)
        return PerformImportResponse(log=log)

    if isinstance(item, RelationshipItem):
        assignments = _make_assignments(item.attribute_assignments)
        relationship = Relationship(
            attribute_assignments=assignments,
            from_entity_id=item.from_entity_id,
            from_entity_type=item.from_entity_type,
            to_entity_id=item.to_entity_id,
            to_entity_type=item.to_entity_type,
        )
        return PerformImportResponse(relationship=relationship)


def _make_timestamp(datetime: datetime) -> Timestamp:
    timestamp = Timestamp()
    timestamp.FromDatetime(datetime)
    return timestamp


def _make_value(value: Value) -> CommonValue:
    if isinstance(value, BooleanValue):
        return CommonValue(boolean=value.value)

    if isinstance(value, DateTimeValue):
        timestamp = _make_timestamp(value.value)
        return CommonValue(date_time=timestamp)

    if isinstance(value, DateValue):
        date = value.value
        dat = datetime(date.year, date.month, date.day)
        timestamp = _make_timestamp(dat)
        return CommonValue(date=timestamp)

    if isinstance(value, NumberValue):
        return CommonValue(number=value.value)

    if isinstance(value, StringValue):
        return CommonValue(string=value.value)

    if isinstance(value, TimeValue):
        time = value.value
        dat = datetime(1, 1, 1, time.hour, time.minute, time.second)
        timestamp = _make_timestamp(dat)
        return CommonValue(time=timestamp)
