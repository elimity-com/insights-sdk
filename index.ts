import { ConnectError, ConnectRouter } from "@connectrpc/connect";
import {
  PerformImportRequest,
  PerformImportResponse,
  Service,
} from "./gen/elimity/insights/customgateway/v1alpha1/customgateway_pb.js";
import { Value } from "@bufbuild/protobuf/wkt";
import { connectNodeAdapter } from "@connectrpc/connect-node";
import { createServer } from "node:http";

export function serveGateway(
  handler: (
    fields: Record<string, Value>,
  ) => AsyncGenerator<PerformImportResponse>,
): void {
  async function* generateResponses(
    request: PerformImportRequest,
  ): AsyncGenerator<PerformImportResponse> {
    try {
      yield* handler(request.fields);
    } catch (error) {
      throw ConnectError.from(error);
    }
  }
  const processRouter = (router: ConnectRouter): void => {
    router.rpc(Service.method.performImport, generateResponses);
  };
  const options = { routes: processRouter };
  const adapter = connectNodeAdapter(options);
  createServer(adapter).listen(80);
}
