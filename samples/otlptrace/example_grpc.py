#!/usr/bin/env python3
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

import google.auth
import google.auth.transport.grpc
import google.auth.transport.requests
import grpc
from google.auth.transport.grpc import AuthMetadataPlugin
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

"""
This is a sample script that exports OTLP traces encoded as protobufs via gRPC. 
"""

credentials, _ = google.auth.default()
request = google.auth.transport.requests.Request()
resource = Resource.create(attributes={SERVICE_NAME: "otlp-gcp-grpc-sample"})

auth_metadata_plugin = AuthMetadataPlugin(credentials=credentials, request=request)
channel_creds = grpc.composite_channel_credentials(
    grpc.ssl_channel_credentials(),
    grpc.metadata_call_credentials(auth_metadata_plugin),
)

trace_provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(
    OTLPSpanExporter(
        credentials=channel_creds,
        endpoint="https://telemetry.googleapis.com:443/v1/traces",
    )
)
trace_provider.add_span_processor(processor)
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer("my.tracer.name")


def do_work():
    with tracer.start_as_current_span("span-grpc") as span:
        # do some work that 'span' will track
        print("doing some work...")
        # When the 'with' block goes out of scope, 'span' is closed for you


def do_work_repeatedly():
    try:
        while True:
            do_work()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt: Stopping work.")


do_work_repeatedly()
