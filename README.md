# futon

Envoy xDS service for k8s endpoints

## Building

`bazel build //futon:futor.tar` will produce a tarfile of a Docker image for futon.


## Running

Futon is meant to be run inside a k8s cluster. It needs to be able to list services and pods.

## Testing

`bazel test acceptance --test_output=all`; it might take a while.
