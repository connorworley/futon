#!/bin/bash
set -euxo pipefail

function cleanup {
    unset KUBECONFIG
    kind delete cluster
}

trap cleanup EXIT

kind create cluster --config ./acceptance_files/cluster-config.yaml
export KUBECONFIG="$(kind get kubeconfig-path)"

kind load image-archive ./futon/futon.tar
kind load image-archive ./acceptance_images/envoy/envoy.tar

kubectl apply -f ./acceptance_files/cluster-bootstrap.yaml

kubectl wait --for=condition=available --timeout=600s deployment.apps/hello-world
kubectl wait --for=condition=available --timeout=600s deployment.apps/envoy
kubectl wait --for=condition=available --timeout=600s deployment.apps/futon

$@
