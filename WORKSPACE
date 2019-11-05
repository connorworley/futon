load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "rules_protobuf",
    strip_prefix = "protobuf-3.10.1",
    urls = ["https://github.com/protocolbuffers/protobuf/archive/v3.10.1.tar.gz"],
)

load("@rules_protobuf//:protobuf_deps.bzl", "protobuf_deps")
protobuf_deps()

load("@rules_protobuf//:protobuf.bzl", "py_proto_library")

#http_archive(
#    name = "envoy_api",
#    strip_prefix = "data-plane-api-51ebfc50b99b8422e53bc8e0352347609f300a69",
#    urls =["https://github.com/envoyproxy/data-plane-api/archive/51ebfc50b99b8422e53bc8e0352347609f300a69.tar.gz"],
#)
