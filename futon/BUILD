load("@requirements_txt//:requirements.bzl", "all_requirements")
load("@io_bazel_rules_docker//python3:image.bzl", "py3_image")

py3_image(
    name = "futon",
    visibility = ["//visibility:public"],
    srcs = [
        "clusters.py",
        "main.py",
    ],
    deps = ["@envoy_api//envoy/api/v2:pkg_py_proto"] + all_requirements,
    main = "main.py",
)
