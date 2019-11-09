workspace(name = "futon_dynamics")


# Python Rules
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "rules_python",
    urls = [
        "https://github.com/brandjon/rules_python/archive/edba55a7d772e94748d64fb2683ea1419bf167ae.tar.gz",
    ],
    strip_prefix = "rules_python-edba55a7d772e94748d64fb2683ea1419bf167ae",
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


# requirements.txt
load("@rules_python//python:pip.bzl", "pip_import")

pip_import(
    name = "requirements_txt",
    requirements = "//:requirements.txt",
    python_interpreter = "python3",
)

load("@requirements_txt//:requirements.bzl", "pip_install")
pip_install()

# subpar
http_archive(
    name = "subpar",
    urls = [
        "https://github.com/google/subpar/archive/35bb9f0092f71ea56b742a520602da9b3638a24f.tar.gz",
    ],
    strip_prefix = "subpar-35bb9f0092f71ea56b742a520602da9b3638a24f",
)
