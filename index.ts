import {
  AttributeAssignment as ClientAttributeAssignment,
  Entity as ClientEntity,
  Relationship as ClientRelationship,
  Value as ClientValue,
  ValueType,
} from "@elimity/insights-client";
import {
  AttributeAssignment as CommonAttributeAssignment,
  Value as CommonValue,
} from "./gen/elimity/insights/common/v1alpha1/common_pb.js";
import { ConnectError, ConnectRouter } from "@connectrpc/connect";
import {
  Level as CustomGatewayLevel,
  PerformImportRequest,
  PerformImportResponse,
} from "./gen/elimity/insights/customgateway/v1alpha1/customgateway_pb.js";
import {
  JsonValue,
  PlainMessage,
  Value as ProtobufValue,
} from "@bufbuild/protobuf";
import { Service } from "./gen/elimity/insights/customgateway/v1alpha1/customgateway_connect.js";
import { connectNodeAdapter } from "@connectrpc/connect-node";
import { createServer } from "node:http";
import { mapValues } from "lodash-es";

export interface EntityItem {
  readonly entity: ClientEntity;
  readonly type: ItemType.Entity;
}

export enum Level {
  Alert,
  Info,
}

export interface LogItem {
  readonly level: Level;
  readonly message: string;
  readonly type: ItemType.Log;
}

export interface RelationshipItem {
  readonly relationship: ClientRelationship;
  readonly type: ItemType.Relationship;
}

export enum ItemType {
  Entity,
  Log,
  Relationship,
}

export type Item = EntityItem | LogItem | RelationshipItem;

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
        const value = makeResponse(item);
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

function makeAssignment(
  assignment: ClientAttributeAssignment,
): PlainMessage<CommonAttributeAssignment> {
  const value = makeValue(assignment.value);
  const val = { value };
  return {
    attributeTypeId: assignment.attributeTypeId,
    value: val,
  };
}

function makeAssignments(
  assignments: readonly ClientAttributeAssignment[],
): PlainMessage<CommonAttributeAssignment>[] {
  return assignments.map(makeAssignment);
}

function makeLevel(level: Level): PlainMessage<CustomGatewayLevel>["value"] {
  const value = {};
  switch (level) {
    case Level.Alert:
      return {
        case: "alert",
        value,
      };

    case Level.Info:
      return {
        case: "info",
        value,
      };
  }
}

function makeJsonValue(value: ProtobufValue): JsonValue {
  return value.toJson();
}

function makeResponse(
  item: Item,
): PlainMessage<PerformImportResponse>["value"] {
  switch (item.type) {
    case ItemType.Entity: {
      const entity = item.entity;
      const assignments = makeAssignments(entity.attributeAssignments);
      const value = {
        assignments,
        id: entity.id,
        name: entity.name,
        type: entity.type,
      };
      return {
        case: "entity",
        value,
      };
    }

    case ItemType.Log: {
      const levelValue = makeLevel(item.level);
      const level = { value: levelValue };
      const logValue = {
        level,
        message: item.message,
      };
      return {
        case: "log",
        value: logValue,
      };
    }

    case ItemType.Relationship: {
      const relationship = item.relationship;
      const assignments = makeAssignments(relationship.attributeAssignments);
      const value = {
        assignments,
        fromEntityId: relationship.fromEntityId,
        fromEntityType: relationship.fromEntityType,
        toEntityId: relationship.toEntityId,
        toEntityType: relationship.toEntityType,
      };
      return {
        case: "relationship",
        value,
      };
    }
  }
}

function makeValue(value: ClientValue): PlainMessage<CommonValue>["value"] {
  switch (value.type) {
    case ValueType.Boolean:
      return {
        case: "boolean",
        value: value.value,
      };

    case ValueType.Date:
      return {
        case: "date",
        value: value.value,
      };

    case ValueType.DateTime:
      return {
        case: "dateTime",
        value: value.value,
      };

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

    case ValueType.Time:
      return {
        case: "time",
        value: value.value,
      };
  }
}
