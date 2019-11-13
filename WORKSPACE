workspace(name = "futon")


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

# Download the rules_docker repository at release v0.12.1
http_archive(
    name = "io_bazel_rules_docker",
    sha256 = "14ac30773fdb393ddec90e158c9ec7ebb3f8a4fd533ec2abbfd8789ad81a284b",
    strip_prefix = "rules_docker-0.12.1",
    urls = ["https://github.com/bazelbuild/rules_docker/releases/download/v0.12.1/rules_docker-v0.12.1.tar.gz"],
)

# OPTIONAL: Call this to override the default docker toolchain configuration.
# This call should be placed BEFORE the call to "container_repositories" below
# to actually override the default toolchain configuration.
# Note this is only required if you actually want to call
# docker_toolchain_configure with a custom attr; please read the toolchains
# docs in /toolchains/docker/ before blindly adding this to your WORKSPACE.
# BEGIN OPTIONAL segment:
load("@io_bazel_rules_docker//toolchains/docker:toolchain.bzl",
    docker_toolchain_configure="toolchain_configure"
)
docker_toolchain_configure(
  name = "docker_config",
  # OPTIONAL: Path to a directory which has a custom docker client config.json.
  # See https://docs.docker.com/engine/reference/commandline/cli/#configuration-files
  # for more details.
  client_config="<enter absolute path to your docker config directory here>",
)
# End of OPTIONAL segment.

load(
    "@io_bazel_rules_docker//repositories:repositories.bzl",
    container_repositories = "repositories",
)
container_repositories()

# This is NOT needed when going through the language lang_image
# "repositories" function(s).
load("@io_bazel_rules_docker//repositories:deps.bzl", container_deps = "deps")

container_deps()

load(
    "@io_bazel_rules_docker//container:container.bzl",
    "container_pull",
)

container_pull(
  name = "java_base",
  registry = "gcr.io",
  repository = "distroless/java",
  # 'tag' is also supported, but digest is encouraged for reproducibility.
  digest = "sha256:deadbeef",
)

load("@io_bazel_rules_docker//python3:image.bzl", "repositories")
repositories()

load("@io_bazel_rules_docker//container:pull.bzl", "container_pull")
container_pull(
    name = "envoy_base",
    registry = "registry.hub.docker.com",
    repository = "envoyproxy/envoy",
    tag = "v1.12.0",
)
