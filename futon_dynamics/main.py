import argparse
import sys

import flask
import kubernetes
import waitress

import futon_dynamics.clusters


def main(argv):
    parser = argparse.ArgumentParser(
        description='k8s / Envoy Cluster Discovery Service',
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8888,
    )
    args = parser.parse_args(argv)

    kubernetes.config.load_incluster_config()
    k8s_client = kubernetes.client.CoreV1Api()

    app = flask.Flask(__name__)
    app.register_blueprint(futon_dynamics.clusters.blueprint(k8s_client))
    waitress.serve(app, host='0.0.0.0', port=args.port)


if __name__ == "__main__":
    main(sys.argv[1:])
