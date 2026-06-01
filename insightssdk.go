package insightssdk

import (
	"context"
	"encoding/json"
	"fmt"
	"iter"
	"maps"
	"net/http"

	"connectrpc.com/connect"
	"github.com/elimity-com/insights-sdk/v2/gen/elimity/insights/customgateway/v1alpha2"
	"github.com/elimity-com/insights-sdk/v2/gen/elimity/insights/customgateway/v1alpha2/v1alpha2connect"
	"google.golang.org/protobuf/types/known/structpb"
)

func Handler(
	fun func([]byte, any) iter.Seq2[*v1alpha2.PerformImportResponse, error], initialCursor any, version string,
) http.Handler {
	mux := http.NewServeMux()
	serviceHandler := serviceHandler{
		fun:           fun,
		initialCursor: initialCursor,
		version:       version,
	}
	path, httpHandler := v1alpha2connect.NewServiceHandler(serviceHandler)
	mux.Handle(path, httpHandler)
	return mux
}

type serviceHandler struct {
	fun           func([]byte, any) iter.Seq2[*v1alpha2.PerformImportResponse, error]
	initialCursor any
	version       string
}

func (h serviceHandler) Meta(
	context.Context, *connect.Request[v1alpha2.MetaRequest],
) (*connect.Response[v1alpha2.MetaResponse], error) {
	cursor, _ := structpb.NewValue(h.initialCursor)
	response := &v1alpha2.MetaResponse{
		InitialCursor: cursor,
		Version:       h.version,
	}
	return connect.NewResponse(response), nil
}

func (h serviceHandler) PerformImport(
	_ context.Context, request *connect.Request[v1alpha2.PerformImportRequest],
	stream *connect.ServerStream[v1alpha2.PerformImportResponse],
) error {
	expectedVersion := h.version
	req := request.Msg
	if actualVersion := req.Version; expectedVersion != actualVersion {
		return fmt.Errorf("expected request to have version %s instead of %s", expectedVersion, actualVersion)
	}
	fields := map[string]*structpb.Value{}
	maps.Copy(fields, req.Fields)
	bytes, _ := json.Marshal(fields)
	cursor := req.Cursor.AsInterface()
	for response, err := range h.fun(bytes, cursor) {
		if err != nil {
			return fmt.Errorf("handler failed: %v", err)
		}
		if err := stream.Send(response); err != nil {
			return fmt.Errorf("failed sending response: %v", err)
		}
	}
	return nil
}
