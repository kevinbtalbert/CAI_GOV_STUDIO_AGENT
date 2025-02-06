#!/bin/bash

# This script can be used to generate the protobuf
# definitions for python that can be used in the `ft`
# package. Note that the protobuf def is placed directly
# in the python package so we don't have to do any 
# manual package path manipulation. If we migrate this
# protobuf to be a first-class microservice, then this 
# workaround isn't necessary. 

# Generate the protobuf
uv run -m grpc_tools.protoc \
    -I=. \
    --python_out=. \
    --grpc_python_out=. \
    --pyi_out=. \
    ./studio/proto/agent_studio.proto


# Run ruff for formatting on the generated proto files.
# the generated proto files don't explicitly use ruff formatting,
# so we want to update this before we push changes. In reality, we
# should be running ruff formatting before every commit.

uv run -m ruff format studio/proto/agent_studio_pb2.py
uv run -m ruff format studio/proto/agent_studio_pb2_grpc.py
uv run -m ruff format studio/proto/agent_studio_pb2.pyi

# compile proto for 
npx protoc \
    --plugin=protoc-gen-ts_proto=./node_modules/.bin/protoc-gen-ts_proto \
    --ts_proto_opt=outputServices=grpc-js \
    --ts_proto_opt=useExactTypes=false \
    --ts_proto_opt=lowerCaseServiceMethods=false \
    --ts_proto_opt=snakeToCamel=false \
    --ts_proto_out=. \
    -I. ./studio/proto/agent_studio.proto
