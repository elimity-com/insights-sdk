# Elimity Insights SDK

This repository contains a Go and NodeJS package to simplify the implementation of various interactions with Elimity
Insights servers.

## Usage

The following snippets shows how to implement a custom gateway that simply logs a message and streams an entity for each
file in the requested directory.

### Go

```go
package main

import (
	"encoding/json"
	"fmt"
	commonv1alpha1 "github.com/elimity-com/insights-sdk/gen/elimity/insights/common/v1alpha1"
	customgatewayv1alpha1 "github.com/elimity-com/insights-sdk/gen/elimity/insights/customgateway/v1alpha1"
	"iter"
	"os"
)

func generateResponses(bytes []byte) iter.Seq2[*customgatewayv1alpha1.PerformImportResponse, error] {
	return responseGenerator{bytes: bytes}.generate
}

func main() {
	insightssdk.ServeGateway(generateResponses)
}

type responseGenerator struct {
	bytes []byte
}

func (g responseGenerator) generate(yield func(*customgatewayv1alpha1.PerformImportResponse, error) bool) {
	var request request
	if err := json.Unmarshal(g.bytes, &request); err != nil {
		err := fmt.Errorf("failed unmarshalling request: %v", err)
		yield(nil, err)
		return
	}
	info := &customgatewayv1alpha1.Level_Info{}
	level := &customgatewayv1alpha1.Level{Value: info}
	log := &customgatewayv1alpha1.Log{
		Level:   level,
		Message: "Reading directory contents",
	}
	lo := &customgatewayv1alpha1.PerformImportResponse_Log{Log: log}
	response := &customgatewayv1alpha1.PerformImportResponse{Value: lo}
	if !yield(response, nil) {
		return
	}
	files, err := os.ReadDir(request.Path)
	if err != nil {
		err := fmt.Errorf("failed reading directory: %v", err)
		yield(nil, err)
		return
	}
	for _, file := range files {
		entity := &commonv1alpha1.Entity{
			Id:          item.ID,
			Name:        item.Name,
			Type:        item.Type,
		}
		ent := &customgatewayv1alpha1.PerformImportResponse_Entity{Entity: entity}
		response := &customgatewayv1alpha1.PerformImportResponse{Value: ent}
		if !yield(response, nil) {
			return
		}
	}
}

type request struct {
	Path string
}
```

### NodeJS

```typescript
import {
  Item,
  ItemKind,
  Level,
  Value,
  serveGateway,
} from "@elimity/insights-sdk";
import { JsonValue } from "@bufbuild/protobuf";
import { readdir } from "node:fs/promises";

async function* generateItems(
  fields: Record<string, JsonValue>,
): AsyncGenerator<Item> {
  const path = fields["path"];
  if (typeof path != "string") throw new Error("got invalid request");
  yield {
    kind: ItemKind.Log,
    level: Level.Info,
    message: "Reading directory contents",
  };
  const files = await readdir(path);
  for (const file of files) {
    const assignments: Record<string, Value> = {};
    yield {
      attributeAssignments: assignments,
      id: file,
      kind: ItemKind.Entity,
      name: file,
      type: "file",
    };
  }
}

serveGateway(generateItems);
```

## Installation

### Go

```sh
$ go get github.com/elimity-com/insights-sdk
```

### NodeJS

```sh
$ npm i @elimity/insights-sdk
```

## Compatibility

| Client version | Insights version |
| -------------- | ---------------- |
| 1              | >=3.42           |
