package insightssdk

import (
	"connectrpc.com/connect"
	"context"
	"encoding/json"
	"fmt"
	"github.com/elimity-com/insights-sdk/gen/elimity/insights/customgateway/v1alpha1"
	"github.com/elimity-com/insights-sdk/gen/elimity/insights/customgateway/v1alpha1/v1alpha1connect"
	"google.golang.org/protobuf/types/known/structpb"
	"iter"
	"maps"
	"net/http"
)

func Handler(fun func([]byte) iter.Seq2[*v1alpha1.PerformImportResponse, error]) http.Handler {
	mux := http.NewServeMux()
	serviceHandler := serviceHandler{fun: fun}
	path, httpHandler := v1alpha1connect.NewServiceHandler(serviceHandler)
	mux.Handle(path, httpHandler)
	return mux
}

type serviceHandler struct {
	fun func([]byte) iter.Seq2[*v1alpha1.PerformImportResponse, error]
}

func (h serviceHandler) PerformImport(
	_ context.Context, request *connect.Request[v1alpha1.PerformImportRequest],
	stream *connect.ServerStream[v1alpha1.PerformImportResponse],
) error {
	fields := map[string]*structpb.Value{}
	maps.Copy(fields, request.Msg.Fields)
	bytes, _ := json.Marshal(fields)
	for response, err := range h.fun(bytes) {
		if err != nil {
			return fmt.Errorf("handler failed: %v", err)
		}
		if err := stream.Send(response); err != nil {
			return fmt.Errorf("failed sending response: %v", err)
		}
	}
	return nil
}
