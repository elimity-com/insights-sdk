# Elimity Insights SDK

This repository contains a Go, NodeJS and Python package to simplify the implementation of various interactions with
Elimity Insights servers.

## Usage

The following snippets shows how to implement a custom gateway that first validates Elimity Insights' JWT access token,
then logs a message and finally streams an entity for each file in the requested directory.

### Go

```go
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/auth0/go-jwt-middleware/v2"
	"github.com/auth0/go-jwt-middleware/v2/jwks"
	"github.com/auth0/go-jwt-middleware/v2/validator"
	"github.com/elimity-com/insights-sdk/v2"
	"github.com/elimity-com/insights-sdk/v2/gen/elimity/insights/common/v1alpha1"
	"github.com/elimity-com/insights-sdk/v2/gen/elimity/insights/customgateway/v1alpha2"
	"iter"
	"log"
	"net/http"
	"net/url"
	"os"
)

func generateResponses(bytes []byte, cursor any) iter.Seq2[*v1alpha2.PerformImportResponse, error] {
	generator := responseGenerator{
		bytes:  bytes,
		cursor: cursor,
    }
	return generator.generate
}

func makeClaims() validator.CustomClaims {
	return &claims{}
}

func main() {
	url, _ := url.Parse("https://auth.elimity.com/")
	provider := jwks.NewCachingProvider(url, 0)
	audiences := []string{"gateway"}
	option := validator.WithCustomClaims(makeClaims)
	validator, _ := validator.New(provider.KeyFunc, "RS256", "https://auth.elimity.com/", audiences, option)
	innerHandler := insightssdk.Handler(generateResponses, nil, "v1.0.0")
	outerHandler := jwtmiddleware.New(validator.ValidateToken).CheckJWT(innerHandler)
	err := http.ListenAndServe(":8080", outerHandler)
	log.Fatal(err)
}

type claims struct {
	BaseURL    string `json:"base_url"`
	GatewayURL string `json:"gateway_url"`
	SourceID   string `json:"source_id"`
}

func (c *claims) Validate(context.Context) error {
	comparisons := map[string]string{
		"https://example.elimity.com": c.BaseURL,
		"https://gateway.example.com": c.GatewayURL,
		"42":                          c.SourceID,
	}
	for expected, actual := range comparisons {
		if expected != actual {
			return fmt.Errorf("got invalid claim value: %v", actual)
		}
	}
	return nil
}

type responseGenerator struct {
	bytes  []byte
	cursor any
}

func (g responseGenerator) generate(yield func(*v1alpha2.PerformImportResponse, error) bool) {
	var request request
	if err := json.Unmarshal(g.bytes, &request); err != nil {
		err := fmt.Errorf("failed unmarshalling request: %v", err)
		yield(nil, err)
		return
	}
	info := &v1alpha2.Level_Info{}
	level := &v1alpha2.Level{Value: info}
	log := &v1alpha2.Log{
		Level:   level,
		Message: "Reading directory contents",
	}
	lo := &v1alpha2.PerformImportResponse_Log{Log: log}
	response := &v1alpha2.PerformImportResponse{Value: lo}
	if !yield(response, nil) {
		return
	}
	entries, err := os.ReadDir(request.Path)
	if err != nil {
		err := fmt.Errorf("failed reading directory: %v", err)
		yield(nil, err)
		return
	}
	for _, entry := range entries {
		name := entry.Name()
		entity := &v1alpha1.Entity{
			Id:   name,
			Name: name,
			Type: "file",
		}
		ent := &v1alpha2.PerformImportResponse_Entity{Entity: entity}
		response := &v1alpha2.PerformImportResponse{Value: ent}
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
import { Item, ItemKind, Level, Value, handler } from "@elimity/insights-sdk";
import { JsonValue } from "@bufbuild/protobuf";
import { auth } from "express-oauth2-jwt-bearer";
import express from "express";
import { readdir } from "node:fs/promises";
import { z } from "zod";

async function* generateItems(
  cursor: JsonValue,
  fields: Record<string, JsonValue>,
): AsyncGenerator<Item> {
  const request = z.strictObject({ path: z.string() }).parse(fields);
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

const validators = {
  base_url: "https://example.elimity.com",
  gateway_url: "https://gateway.example.com",
  source_id: "42",
};
const config = {
  audience: "gateway",
  issuerBaseURL: "https://auth.elimity.com/",
  validators,
};
const authHandler = auth(config);
const sdkHandler = handler(generateItems, null, "v1.0.0");
express().use(authHandler, sdkHandler).listen(8080);
```

### Python

```python
from collections.abc import AsyncIterator
from os import listdir
from typing import Literal

from auth0_api_python import ApiClient, ApiClientOptions
from elimity_insights_sdk import EntityItem, Item, Level, LogItem, Value, app
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from uvicorn import run

_options = ApiClientOptions("auth.elimity.com", "gateway")
_client = ApiClient(_options)


class _Claims(BaseModel):
    base_url: Literal["https://example.elimity.com"]
    gateway_url: Literal["https://gateway.example.com"]
    source_id: Literal["42"]


class _Middleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        headers = dict(request.headers)
        claims = await _client.verify_request(headers)
        _Claims.model_validate(claims)
        return await call_next(request)


class _Request(BaseModel):
    path: str


async def _generate_items(cursor: object, fields: dict[str, object]) -> AsyncIterator[Item]:
    request = _Request.model_validate(fields)
    yield LogItem(Level.INFO, "Reading directory contents")
    for file in listdir(request.path):
        assignments: dict[str, Value] = {}
        yield EntityItem(assignments, file, file, "file")


_app = app(_generate_items, None, "v1.0.0")
_middleware = _Middleware(_app)
run(_middleware)
```

## Installation

### Go

```sh
$ go get github.com/elimity-com/insights-sdk/v2
```

### NodeJS

```sh
$ npm i @elimity/insights-sdk
```

### Python

```
$ pip install elimity-insights-sdk
```

## Compatibility

| SDK version | Insights version |
| ----------- | ---------------- |
| 1           | >=3.42           |
| 2           | >=3.46           |
