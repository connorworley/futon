#!/bin/bash
set -euxo pipefail

FUTON_PID=""
ENVOY_PID=""

function cleanup {
    ! kill -9 "$FUTON_PID"
    ! kill -9 "$ENVOY_PID"
    kind delete cluster
}

trap cleanup EXIT

kind create cluster
KUBECONFIG="$(kind get kubeconfig-path)" kubectl create deployment hello-world --image  gcr.io/google-samples/node-hello
KUBECONFIG="$(kind get kubeconfig-path)" kubectl expose deployment.apps/hello-world --type NodePort --port 8080

bazelisk run //futon_dynamics -- --kubeconfig-path "$(kind get kubeconfig-path)" &
FUTON_PID="$!"
docker run --volume "$(pwd)/acceptance/envoy.yaml/:/etc/envoy/envoy.yaml" --expose 12345 envoyproxy/envoy:v1.12.0 &
ENVOY_PID="$!"

sleep 30
curl localhost:12345
