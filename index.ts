import { ConnectError, ConnectRouter } from "@connectrpc/connect";
import {
  Level as GatewayLevel,
  PerformImportRequest,
  PerformImportResponse,
  Service,
} from "./gen/elimity/insights/customgateway/v1alpha1/customgateway_pb.js";
import { JsonValue, toJson } from "@bufbuild/protobuf";
import {
  Value as ProtobufValue,
  ValueSchema,
  timestampFromDate,
} from "@bufbuild/protobuf/wkt";
import { Value as CommonValue } from "./gen/elimity/insights/common/v1alpha1/common_pb.js";
import { Handler } from "express";
import { expressConnectMiddleware } from "@connectrpc/connect-express";
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

export function handler(
  fun: (fields: Record<string, JsonValue>) => AsyncGenerator<Item>,
): Handler {
  async function* generateResponses(
    request: PerformImportRequest,
  ): AsyncGenerator<PerformImportResponse> {
    const fields = mapValues(request.fields, makeJsonValue);
    const generator = fun(fields);
    try {
      for await (const item of generator) {
        const value = makeResponseValue(item);
        yield {
          $typeName:
            "elimity.insights.customgateway.v1alpha1.PerformImportResponse",
          value,
        };
      }
    } catch (error) {
      throw ConnectError.from(error);
    }
  }

  const processRouter = (router: ConnectRouter): void => {
    router.rpc(Service.method.performImport, generateResponses);
  };
  const options = { routes: processRouter };
  return expressConnectMiddleware(options);
}

function makeJsonValue(value: ProtobufValue): JsonValue {
  return toJson(ValueSchema, value);
}

function makeAttributeAssignments(
  assignments: Record<string, Value>,
): Record<string, CommonValue> {
  return mapValues(assignments, makeCommonValue);
}

function makeCommonValue(value: Value): CommonValue {
  const val = makeCommonValueValue(value);
  return {
    $typeName: "elimity.insights.common.v1alpha1.Value",
    value: val,
  };
}

function makeCommonValueValue(value: Value): CommonValue["value"] {
  switch (value.type) {
    case ValueType.Boolean:
      return {
        case: "boolean",
        value: value.value,
      };

    case ValueType.Date: {
      const timestamp = timestampFromDate(value.value);
      return {
        case: "date",
        value: timestamp,
      };
    }

    case ValueType.DateTime: {
      const timestamp = timestampFromDate(value.value);
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
      const timestamp = timestampFromDate(value.value);
      return {
        case: "time",
        value: timestamp,
      };
    }
  }
}

function makeResponseValue(item: Item): PerformImportResponse["value"] {
  switch (item.kind) {
    case ItemKind.Entity: {
      const assignments = makeAttributeAssignments(item.attributeAssignments);
      const entity = {
        $typeName: "elimity.insights.common.v1alpha1.Entity",
        attributeAssignments: assignments,
        id: item.id,
        name: item.name,
        type: item.type,
      } as const;
      return {
        case: "entity",
        value: entity,
      };
    }

    case ItemKind.Log: {
      const empty = { $typeName: "google.protobuf.Empty" } as const;
      const value: GatewayLevel["value"] =
        item.level == Level.Alert
          ? {
              case: "alert",
              value: empty,
            }
          : {
              case: "info",
              value: empty,
            };
      const level = {
        $typeName: "elimity.insights.customgateway.v1alpha1.Level",
        value,
      } as const;
      const log = {
        $typeName: "elimity.insights.customgateway.v1alpha1.Log",
        level,
        message: item.message,
      } as const;
      return {
        case: "log",
        value: log,
      };
    }

    case ItemKind.Relationship: {
      const assignments = makeAttributeAssignments(item.attributeAssignments);
      const relationship = {
        $typeName: "elimity.insights.common.v1alpha1.Relationship",
        attributeAssignments: assignments,
        fromEntityId: item.fromEntityId,
        fromEntityType: item.fromEntityType,
        toEntityId: item.toEntityId,
        toEntityType: item.toEntityType,
      } as const;
      return {
        case: "relationship",
        value: relationship,
      };
    }
  }
}
