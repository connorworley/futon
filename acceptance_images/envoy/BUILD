load("@io_bazel_rules_docker//container:image.bzl", "container_image")
load("@bazel_tools//tools/build_defs/pkg:pkg.bzl", "pkg_tar")

container_image(
    name = "envoy",
    visibility = ["//visibility:public"],
    base = "@envoy_base//image",
    tars = [
        ":envoy_yaml",
    ],
)

pkg_tar(
    name = "envoy_yaml",
    package_dir = "/etc/envoy",
    srcs = [
        "envoy.yaml",
    ],
)