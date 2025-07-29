# Elimity Insights SDK

This repository contains a Go and NodeJS package to simplify the implementation of various interactions with Elimity
Insights servers.

## Usage

The following snippets shows how to implement a custom gateway that first validates a secret token for authentication,
then logs a message and finally streams an entity for each file in the requested directory.

### Go

```go
package main

import (
	"crypto/sha256"
	"crypto/subtle"
	"encoding/json"
	"errors"
	"fmt"
	commonv1alpha1 "github.com/elimity-com/insights-sdk/gen/elimity/insights/common/v1alpha1"
	customgatewayv1alpha1 "github.com/elimity-com/insights-sdk/gen/elimity/insights/customgateway/v1alpha1"
	"github.com/elimity-com/insights-sdk"
	"iter"
	"log"
	"os"
)

var con config

func generateResponses(bytes []byte) iter.Seq2[*customgatewayv1alpha1.PerformImportResponse, error] {
	return responseGenerator{bytes: bytes}.generate
}

func main() {
	bytes, err := os.ReadFile("config/config.json")
	if err != nil {
		log.Fatalf("failed reading config file: %v", err)
	}
	if err := json.Unmarshal(bytes, &con); err != nil {
		log.Fatalf("failed parsing config file: %v", err)
	}
	insightssdk.ServeGateway(":8080", generateResponses)
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
	hash := sha256.Sum256(request.SecretToken)
	if hash := hash[:]; subtle.ConstantTimeCompare(hash, con.SecretTokenHash) == 0 {
		err := errors.New("got invalid secret token")
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
			Id:   item.ID,
			Name: item.Name,
			Type: item.Type,
		}
		ent := &customgatewayv1alpha1.PerformImportResponse_Entity{Entity: entity}
		response := &customgatewayv1alpha1.PerformImportResponse{Value: ent}
		if !yield(response, nil) {
			return
		}
	}
}

type config struct {
	SecretTokenHash []byte
}

type request struct {
	Path        string
	SecretToken []byte
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
import { createHash, timingSafeEqual } from "node:crypto";
import { readFileSync } from "node:fs";
import { readdir } from "node:fs/promises";
import { z } from "zod";

const serializedConfig = readFileSync("config/config.json", "utf8");
const parsedConfig = JSON.parse(serializedConfig);
const validatedConfig = z
  .strictObject({ secretTokenHash: z.base64() })
  .parse(serializedConfig);
const expectedHash = Buffer.from(validatedConfig.secretTokenHash, "base64");

async function* generateItems(
  fields: Record<string, JsonValue>,
): AsyncGenerator<Item> {
  const request = z
    .strictObject({ path: z.string(), secretToken: z.base64() })
    .parse(fields);
  const actualHash = createHash("sha256")
    .update(request.secretToken, "base64")
    .digest();
  const unauthenticated = !timingSafeEqual(actualHash, expectedHash);
  if (unauthenticated) throw new Error("got invalid secret token");
  yield {
    kind: ItemKind.Log,
    level: Level.Info,
    message: "Reading directory contents",
  };
  const files = await readdir(request.path);
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

serveGateway(generateItems, 8080);
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

| SDK version | Insights version |
| ----------- | ---------------- |
| 1           | >=3.42           |
