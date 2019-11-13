sh_test(
    name = "acceptance",
    size = "medium",
    srcs = [
        "acceptance-environment.sh",
    ],
    data = [
        "//futon:futon.tar",
        "//acceptance_images/envoy:envoy.tar",
        ":acceptance_files",
    ],
    args = [
        "curl -v localhost:30002",
    ],
)

filegroup(
    name = "acceptance_files",
    srcs = glob([
        "acceptance_files/**/*",
    ]),
)
