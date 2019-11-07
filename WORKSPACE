workspace(name = "futon_dynamics")


# Python Rules
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


# Envoy
http_archive(
    name = "envoy",
    urls = [
        "https://github.com/envoyproxy/envoy/archive/v1.12.0.tar.gz",
    ],
    strip_prefix = "envoy-1.12.0",
)

load("@envoy//bazel:api_binding.bzl", "envoy_api_binding")
envoy_api_binding()
load("@envoy//bazel:api_repositories.bzl", "envoy_api_dependencies")
envoy_api_dependencies()
load("@envoy//bazel:repositories.bzl", "envoy_dependencies")
envoy_dependencies()
load("@envoy//bazel:dependency_imports.bzl", "envoy_dependency_imports")
envoy_dependency_imports()
