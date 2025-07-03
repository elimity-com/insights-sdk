import { ConnectError, ConnectRouter } from "@connectrpc/connect";
import {
  Level as GatewayLevel,
  PerformImportRequest,
  PerformImportResponse,
} from "./gen/elimity/insights/customgateway/v1alpha1/customgateway_pb.js";
import {
  JsonValue,
  PlainMessage,
  Value as ProtobufValue,
  Timestamp,
} from "@bufbuild/protobuf";
import { Value as CommonValue } from "./gen/elimity/insights/common/v1alpha1/common_pb.js";
import { Service } from "./gen/elimity/insights/customgateway/v1alpha1/customgateway_connect.js";
import { connectNodeAdapter } from "@connectrpc/connect-node";
import { createServer } from "node:http";
import { mapValues } from "lodash";

export interface BooleanValue {
  readonly type: ValueType.Boolean;
  readonly value: boolean;
}

export interface DateValue {
  readonly type: ValueType.Date;
  readonly value: Date;
}

export interface DateTimeValue {
  readonly type: ValueType.DateTime;
  readonly value: Date;
}

export interface EntityItem {
  readonly attributeAssignments: Record<string, Value>;
  readonly id: string;
  readonly kind: ItemKind.Entity;
  readonly name: string;
  readonly type: string;
}

export type Item = EntityItem | LogItem | RelationshipItem;

export enum ItemKind {
  Entity,
  Log,
  Relationship,
}

export enum Level {
  Alert,
  Info,
}

export interface LogItem {
  readonly kind: ItemKind.Log;
  readonly level: Level;
  readonly message: string;
}

export interface NumberValue {
  readonly type: ValueType.Number;
  readonly value: number;
}

export interface RelationshipItem {
  readonly attributeAssignments: Record<string, Value>;
  readonly fromEntityId: string;
  readonly fromEntityType: string;
  readonly kind: ItemKind.Relationship;
  readonly toEntityId: string;
  readonly toEntityType: string;
}

export interface StringValue {
  readonly type: ValueType.String;
  readonly value: string;
}

export interface TimeValue {
  readonly type: ValueType.Time;
  readonly value: Date;
}

export type Value =
  | BooleanValue
  | DateValue
  | DateTimeValue
  | NumberValue
  | StringValue
  | TimeValue;

export enum ValueType {
  Boolean,
  Date,
  DateTime,
  Number,
  String,
  Time,
}

export function serveGateway(
  handler: (fields: Record<string, JsonValue>) => AsyncGenerator<Item>,
): void {
  async function* generateResponses(
    request: PerformImportRequest,
  ): AsyncGenerator<PlainMessage<PerformImportResponse>> {
    const fields = mapValues(request.fields, makeJsonValue);
    const generator = handler(fields);
    try {
      for await (const item of generator) {
        const value = makeResponseValue(item);
        yield { value };
      }
    } catch (error) {
      throw ConnectError.from(error);
    }
  }

  const processRouter = (router: ConnectRouter): void => {
    router.rpc(Service, Service.methods.performImport, generateResponses);
  };
  const options = { routes: processRouter };
  const adapter = connectNodeAdapter(options);
  createServer(adapter).listen(80);
}

function makeJsonValue(value: ProtobufValue): JsonValue {
  return value.toJson();
}

function makeAttributeAssignments(
  assignments: Record<string, Value>,
): Record<string, PlainMessage<CommonValue>> {
  return mapValues(assignments, makeCommonValue);
}

function makeCommonValue(value: Value): PlainMessage<CommonValue> {
  const val = makeCommonValueValue(value);
  return { value: val };
}

function makeCommonValueValue(
  value: Value,
): PlainMessage<CommonValue>["value"] {
  switch (value.type) {
    case ValueType.Boolean:
      return {
        case: "boolean",
        value: value.value,
      };

    case ValueType.Date: {
      const timestamp = Timestamp.fromDate(value.value);
      return {
        case: "date",
        value: timestamp,
      };
    }

    case ValueType.DateTime: {
      const timestamp = Timestamp.fromDate(value.value);
      return {
        case: "dateTime",
        value: timestamp,
      };
    }

    case ValueType.Number:
      return {
        case: "number",
        value: value.value,
      };

    case ValueType.String:
      return {
        case: "string",
        value: value.value,
      };

    case ValueType.Time: {
      const timestamp = Timestamp.fromDate(value.value);
      return {
        case: "time",
        value: timestamp,
      };
    }
  }
}

function makeResponseValue(
  item: Item,
): PlainMessage<PerformImportResponse>["value"] {
  switch (item.kind) {
    case ItemKind.Entity: {
      const assignments = makeAttributeAssignments(item.attributeAssignments);
      const entity = {
        attributeAssignments: assignments,
        id: item.id,
        name: item.name,
        type: item.type,
      };
      return {
        case: "entity",
        value: entity,
      };
    }

    case ItemKind.Log: {
      const empty = {};
      const value: PlainMessage<GatewayLevel>["value"] =
        item.level == Level.Alert
          ? {
              case: "alert",
              value: empty,
            }
          : {
              case: "info",
              value: empty,
            };
      const level = { value };
      const log = {
        level,
        message: item.message,
      };
      return {
        case: "log",
        value: log,
      };
    }

    case ItemKind.Relationship: {
      const assignments = makeAttributeAssignments(item.attributeAssignments);
      const relationship = {
        attributeAssignments: assignments,
        fromEntityId: item.fromEntityId,
        fromEntityType: item.fromEntityType,
        toEntityId: item.toEntityId,
        toEntityType: item.toEntityType,
      };
      return {
        case: "relationship",
        value: relationship,
      };
    }
  }
}
