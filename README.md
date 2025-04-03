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
	"github.com/elimity-com/insights-client-go/v7"
	"github.com/elimity-com/insights-sdk"
	"iter"
	"os"
)

func generateItems(bytes []byte) iter.Seq2[any, error] {
	return itemGenerator{bytes: bytes}.generate
}

func main() {
	insightssdk.ServeGateway(generateItems)
}

type itemGenerator struct {
	bytes []byte
}

func (g itemGenerator) generate(yield func(any, error) bool) {
	var request request
	if err := json.Unmarshal(g.bytes, &request); err != nil {
		err := fmt.Errorf("failed unmarshalling request: %v", err)
		yield(nil, err)
		return
	}
	log := insights.ConnectorLog{
		Level:   "info",
		Message: "Reading directory contents",
	}
	if !yield(log, nil) {
		return
	}
	files, err := os.ReadDir(request.Path)
	if err != nil {
		err := fmt.Errorf("failed reading directory: %v", err)
		yield(nil, err)
		return
	}
	for _, file := range files {
		entity := insights.Entity{
			ID:   file,
			Name: file,
			Type: "file",
		}
		if !yield(entity, nil) {
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
import { Item, ItemType, Level, serveGateway } from "@elimity/insights-sdk";
import { AttributeAssignment } from "@elimity/insights-client";
import { JsonValue } from "@bufbuild/protobuf";
import { readdir } from "node:fs/promises";

async function* generateItems(
  fields: Record<string, JsonValue>,
): AsyncGenerator<Item> {
  const path = fields["path"];
  if (typeof path != "string") throw new Error("got invalid request");
  yield {
    level: Level.Info,
    message: "Reading directory contents",
    type: ItemType.Log,
  };
  const files = await readdir(path);
  for (const file of files) {
    const assignments: AttributeAssignment[] = [];
    const entity = {
      attributeAssignments: assignments,
      id: file,
      name: file,
      type: "file",
    };
    yield {
      entity,
      type: ItemType.Entity,
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
| 1              | >=3.41           |
