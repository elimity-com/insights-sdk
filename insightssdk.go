package insightssdk

import (
	"connectrpc.com/connect"
	"context"
	"encoding/json"
	"fmt"
	"github.com/elimity-com/insights-client-go/v7"
	commonv1alpha1 "github.com/elimity-com/insights-sdk/gen/elimity/insights/common/v1alpha1"
	customgatewayv1alpha1 "github.com/elimity-com/insights-sdk/gen/elimity/insights/customgateway/v1alpha1"
	"github.com/elimity-com/insights-sdk/gen/elimity/insights/customgateway/v1alpha1/v1alpha1connect"
	"google.golang.org/protobuf/types/known/structpb"
	"google.golang.org/protobuf/types/known/timestamppb"
	"iter"
	"log"
	"maps"
	"net/http"
	"os"
	"time"
)

var errorChannel = make(chan error)

var handler func([]byte) iter.Seq2[any, error]

var server = &http.Server{}

var signalChannel = make(chan os.Signal, 1)

func ServeGateway(han func([]byte) iter.Seq2[any, error]) {
	handler = han
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

func makeAttributeAssignments(assignments []insights.AttributeAssignment) []*commonv1alpha1.AttributeAssignment {
	var ass []*commonv1alpha1.AttributeAssignment
	for _, assignment := range assignments {
		value := makeValue(assignment.Value)
		assignment := &commonv1alpha1.AttributeAssignment{
			AttributeTypeId: assignment.AttributeTypeID,
			Value:           &value,
		}
		ass = append(ass, assignment)
	}
	return ass
}

func makeLevel(level string) customgatewayv1alpha1.Level {
	if level == "alert" {
		alert := &customgatewayv1alpha1.Level_Alert{}
		return customgatewayv1alpha1.Level{Value: alert}
	}
	info := &customgatewayv1alpha1.Level_Info{}
	return customgatewayv1alpha1.Level{Value: info}
}

func makeResponse(item any) customgatewayv1alpha1.PerformImportResponse {
	switch item := item.(type) {
	case insights.ConnectorLog:
		level := makeLevel(item.Level)
		log := &customgatewayv1alpha1.Log{
			Level:   &level,
			Message: item.Message,
		}
		l := &customgatewayv1alpha1.PerformImportResponse_Log{Log: log}
		return customgatewayv1alpha1.PerformImportResponse{Value: l}

	case insights.Entity:
		assignments := makeAttributeAssignments(item.AttributeAssignments)
		entity := &commonv1alpha1.Entity{
			Assignments: assignments,
			Id:          item.ID,
			Name:        item.Name,
			Type:        item.Type,
		}
		ent := &customgatewayv1alpha1.PerformImportResponse_Entity{Entity: entity}
		return customgatewayv1alpha1.PerformImportResponse{Value: ent}
	}
	relationship := item.(insights.Relationship)
	assignments := makeAttributeAssignments(relationship.AttributeAssignments)
	rel := &commonv1alpha1.Relationship{
		Assignments:    assignments,
		FromEntityId:   relationship.FromEntityID,
		FromEntityType: relationship.FromEntityType,
		ToEntityId:     relationship.ToEntityID,
		ToEntityType:   relationship.ToEntityType,
	}
	r := &customgatewayv1alpha1.PerformImportResponse_Relationship{Relationship: rel}
	return customgatewayv1alpha1.PerformImportResponse{Value: r}
}

func makeValue(value insights.Value) commonv1alpha1.Value {
	val := value.Value
	switch value := val.(type) {
	case bool:
		boolean := &commonv1alpha1.Value_Boolean{Boolean: value}
		return commonv1alpha1.Value{Value: boolean}

	case float64:
		number := &commonv1alpha1.Value_Number{Number: value}
		return commonv1alpha1.Value{Value: number}

	case string:
		str := &commonv1alpha1.Value_String_{String_: value}
		return commonv1alpha1.Value{Value: str}
	}
	time := val.(time.Time)
	timestamp := timestamppb.New(time)
	switch value.Type {
	case "date":
		date := &commonv1alpha1.Value_Date{Date: timestamp}
		return commonv1alpha1.Value{Value: date}

	case "dateTime":
		time := &commonv1alpha1.Value_DateTime{DateTime: timestamp}
		return commonv1alpha1.Value{Value: time}
	}
	tim := &commonv1alpha1.Value_Time{Time: timestamp}
	return commonv1alpha1.Value{Value: tim}
}

type serviceHandler struct{}

func (h serviceHandler) PerformImport(
	_ context.Context, request *connect.Request[customgatewayv1alpha1.PerformImportRequest],
	stream *connect.ServerStream[customgatewayv1alpha1.PerformImportResponse],
) error {
	fields := map[string]*structpb.Value{}
	maps.Copy(fields, request.Msg.Fields)
	bytes, _ := json.Marshal(fields)
	for item, err := range handler(bytes) {
		if err != nil {
			return fmt.Errorf("handler failed: %v", err)
		}
		response := makeResponse(item)
		if err := stream.Send(&response); err != nil {
			return fmt.Errorf("failed sending response: %v", err)
		}
	}
	return nil
}
