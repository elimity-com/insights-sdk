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
	"log"
	"maps"
	"net/http"
	"os"
)

var errorChannel = make(chan error)

var handler func([]byte) iter.Seq2[*v1alpha1.PerformImportResponse, error]

var server *http.Server

var signalChannel = make(chan os.Signal, 1)

func ServeGateway(address string, han func([]byte) iter.Seq2[*v1alpha1.PerformImportResponse, error]) {
	handler = han
	server = &http.Server{Addr: address}
	go handleSignals()
	var serviceHandler serviceHandler
	path, httpHandler := v1alpha1connect.NewServiceHandler(serviceHandler)
	http.Handle(path, httpHandler)
	if err := server.ListenAndServe(); err != http.ErrServerClosed {
		log.Fatalf("failed serving: %v", err)
	}
	if err := <-errorChannel; err != nil {
		log.Fatalf("failed shutting down server: %v", err)
	}
}

func handleSignals() {
	<-signalChannel
	context := context.Background()
	errorChannel <- server.Shutdown(context)
}

type serviceHandler struct{}

func (h serviceHandler) PerformImport(
	_ context.Context, request *connect.Request[v1alpha1.PerformImportRequest],
	stream *connect.ServerStream[v1alpha1.PerformImportResponse],
) error {
	fields := map[string]*structpb.Value{}
	maps.Copy(fields, request.Msg.Fields)
	bytes, _ := json.Marshal(fields)
	for response, err := range handler(bytes) {
		if err != nil {
			return fmt.Errorf("handler failed: %v", err)
		}
		if err := stream.Send(response); err != nil {
			return fmt.Errorf("failed sending response: %v", err)
		}
	}
	return nil
}
