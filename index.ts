import { ConnectError, ConnectRouter } from "@connectrpc/connect";
import { JsonValue, PlainMessage, Value } from "@bufbuild/protobuf";
import {
  PerformImportRequest,
  PerformImportResponse,
} from "./gen/elimity/insights/customgateway/v1alpha1/customgateway_pb.js";
import { Service } from "./gen/elimity/insights/customgateway/v1alpha1/customgateway_connect.js";
import { connectNodeAdapter } from "@connectrpc/connect-node";
import { createServer } from "node:http";
import { mapValues } from "lodash";

export function serveGateway(
  handler: (
    fields: Record<string, JsonValue>,
  ) => AsyncGenerator<PlainMessage<PerformImportResponse>>,
): void {
  async function* generateResponses(
    request: PerformImportRequest,
  ): AsyncGenerator<PlainMessage<PerformImportResponse>> {
    const fields = mapValues(request.fields, makeJsonValue);
    try {
      yield* handler(fields);
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

function makeJsonValue(value: Value): JsonValue {
  return value.toJson();
}
