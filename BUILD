load("@requirements_txt//:requirements.bzl", "all_requirements")

py_binary(
    name = "futon_dynamics",
    srcs = ["futon_dynamics.py"],
    deps = ["@envoy_api//envoy/api/v2:pkg_py_proto"] + all_requirements,
)