workspace(name = "futon_dynamics")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "rules_python",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.0.1/rules_python-0.0.1.tar.gz",
    sha256 = "aa96a691d3a8177f3215b14b0edc9641787abaaa30363a080165d06ab65e1161",
)

load("@rules_python//python:repositories.bzl", "py_repositories")
py_repositories()
# Only needed if using the packaging rules.
load("@rules_python//python:pip.bzl", "pip_repositories")
pip_repositories()

http_archive(
    name = "com_google_protobuf",
    strip_prefix = "protobuf-3.10.1",
    urls = [
        "https://github.com/protocolbuffers/protobuf/archive/v3.10.1.tar.gz",
    ],
)

load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")
protobuf_deps()

http_archive(
    name = "io_bazel_rules_go",
    urls = [
        "https://storage.googleapis.com/bazel-mirror/github.com/bazelbuild/rules_go/releases/download/v0.20.2/rules_go-v0.20.2.tar.gz",
        "https://github.com/bazelbuild/rules_go/releases/download/v0.20.2/rules_go-v0.20.2.tar.gz",
    ],
    sha256 = "b9aa86ec08a292b97ec4591cf578e020b35f98e12173bbd4a921f84f583aebd9",
)

load("@io_bazel_rules_go//go:deps.bzl", "go_rules_dependencies", "go_register_toolchains")
go_rules_dependencies()
go_register_toolchains()

http_archive(
    name = "envoy_api",
    strip_prefix = "data-plane-api-51ebfc50b99b8422e53bc8e0352347609f300a69",
    urls = [
        "https://github.com/envoyproxy/data-plane-api/archive/51ebfc50b99b8422e53bc8e0352347609f300a69.tar.gz",
    ],
)

load("@envoy_api//bazel:repositories.bzl", "api_dependencies")
api_dependencies()

http_archive(
    name = "com_github_grpc_grpc",
    urls = [
        "https://github.com/grpc/grpc/archive/c1d176528fd8da9dd4066d16554bcd216d29033f.tar.gz",
    ],
    strip_prefix = "grpc-c1d176528fd8da9dd4066d16554bcd216d29033f",
)

load("@com_github_grpc_grpc//bazel:grpc_deps.bzl", "grpc_deps")
grpc_deps()

load("@com_google_googleapis//:repository_rules.bzl", "switched_rules_by_language")
switched_rules_by_language(
    "com_google_googleapis_imports",
    python = True,
    rules_override = {
        "py_proto_library": "@envoy_api//bazel:api_build_system.bzl",
    },
)
