load("@requirements_txt//:requirements.bzl", "all_requirements")
load("@subpar//:subpar.bzl", "par_binary")

par_binary(
    name = "futon_dynamics",
    srcs = [
        "clusters.py",
        "main.py",
    ],
    deps = ["@envoy_api//envoy/api/v2:pkg_py_proto"] + all_requirements,
    main = "main.py",
    zip_safe = False,
)
