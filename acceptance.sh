#!/bin/bash
set -euxo pipefail

function cleanup {
    unset KUBECONFIG
    kind delete cluster
}

trap cleanup EXIT

cat <<EOF | kind create cluster --config -
kind: Cluster
apiVersion: kind.sigs.k8s.io/v1alpha3
nodes:
  - role: control-plane
  - role: worker
    extraPortMappings:
      - containerPort: 30000
        hostPort: 30000
      - containerPort: 30001
        hostPort: 30001
      - containerPort: 30002
        hostPort: 30002
EOF

export KUBECONFIG="$(kind get kubeconfig-path)"

cat <<EOF | kubectl apply -f -
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
    name: futon-role
rules:
  - apiGroups: [""]
    resources: ["services", "pods"]
    verbs: ["list"]

---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
    name: futon-role
subjects:
  - kind: ServiceAccount
    name: default
    namespace: default
roleRef:
    kind: ClusterRole
    name: futon-role
    apiGroup: rbac.authorization.k8s.io
EOF

kubectl create deployment hello-world --image gcr.io/google-samples/node-hello:1.0
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
    name: hello-world
    labels:
        name: hello-world
spec:
    type: NodePort
    ports:
      - port: 8080
        nodePort: 30000
        name: http
    selector:
        app: hello-world
EOF

docker build -t custom-futon:v0.1.0 -f ./Dockerfile ./bazel-bin/futon_dynamics
kind load docker-image custom-futon:v0.1.0
kubectl create deployment futon --image custom-futon:v0.1.0
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
    name: futon
    labels:
        name: futon
spec:
    type: NodePort
    ports:
      - port: 8888
        nodePort: 30001
        name: http
    selector:
        app: futon
EOF

docker build -t custom-envoy:v1.12.0 ./acceptance/envoy/
kind load docker-image custom-envoy:v1.12.0
kubectl create deployment envoy --image custom-envoy:v1.12.0
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
    name: envoy
    labels:
        name: envoy
spec:
    type: NodePort
    ports:
      - port: 12345
        nodePort: 30002
        name: http
    selector:
        app: envoy
EOF

kubectl wait --for=condition=available --timeout=600s deployment.apps/hello-world
kubectl wait --for=condition=available --timeout=600s deployment.apps/envoy
kubectl wait --for=condition=available --timeout=600s deployment.apps/futon

$SHELL
