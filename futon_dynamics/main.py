import argparse
import sys

import flask
import kubernetes
from cheroot.wsgi import Server

import futon_dynamics.clusters


def main(argv):
    parser = argparse.ArgumentParser(
        description='k8s / Envoy Cluster Discovery Service',
    )
    parser.add_argument(
        '--kubeconfig-path',
        default=None,
        help='kubeconfig path',
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8888,
    )
    args = parser.parse_args(argv)

    kubernetes.config.load_kube_config(config_file=args.kubeconfig_path)
    k8s_client = kubernetes.client.CoreV1Api()

    app = flask.Flask(__name__)
    app.register_blueprint(futon_dynamics.clusters.blueprint(k8s_client))
    print('Starting futon-dynamics server...')
    Server(("0.0.0.0", args.port), app).safe_start()


if __name__ == "__main__":
    main(sys.argv[1:])
