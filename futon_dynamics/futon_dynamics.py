import json
import sys
from functools import lru_cache

import kubernetes
from envoy.api.v2.cds_pb2 import Cluster
from envoy.api.v2.core.address_pb2 import Address
from envoy.api.v2.core.address_pb2 import SocketAddress
from envoy.api.v2.eds_pb2 import ClusterLoadAssignment
from envoy.api.v2.endpoint.endpoint_pb2 import Endpoint
from envoy.api.v2.endpoint.endpoint_pb2 import LbEndpoint
from envoy.api.v2.endpoint.endpoint_pb2 import LocalityLbEndpoints
from flask import Flask
from google.protobuf.json_format import MessageToDict
from waitress import serve


class ClusterEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Cluster):
            return MessageToDict(obj)
        return json.JSONEncoder.default(sef, obj)


@lru_cache(maxsize=1)
def k8s_client():
    kubernetes.config.load_kube_config()
    return kubernetes.client.CoreV1Api()


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def get_clusters():
        clusters = []

        services = k8s_client().list_service_for_all_namespaces(watch=False)
        endpoints = k8s_client().list_endpoints_for_all_namespaces(watch=False)
        nodes = k8s_client().list_node(watch=False)

        for service in services.items:
            if service.spec.type != 'NodePort':
                continue

            node_ports = [port.node_port for port in service.spec.ports]

            lb_endpoints = []
            for endpoint in endpoints.items:
                node_addresses = []
                if endpoint.metadata.labels is None:
                    continue
                if not all([endpoint.metadata.labels.get(key) == value for key, value in service.spec.selector.items()]):
                    continue
                for subset in endpoint.subsets:
                    for address in subset.addresses:
                        for node in nodes.items:
                            if node.metadata.name != address.node_name:
                                continue
                            for node_address in node.status.addresses:
                                if node_address.type != 'InternalIP':
                                    continue
                                node_addresses.append(node_address.address)
                for address, port in itertools.product(node_addresses, node_ports):
                    lb_endpoints.append(
                        LbEndpoint(
                            endpoint=Endpoint(
                                address=Address(
                                    socket_address=SocketAddress(
                                        address=address,
                                        port_value=port,
                                    ),
                                ),
                            ),
                        ),
                    )

            clusters.append(
                Cluster(
                    name = service.metadata.name,
                    type = Cluster.STATIC,
                    load_assignment = ClusterLoadAssignment(
                        cluster_name=service.metadata.name,
                        endpoints=[LocalityLbEndpoints(
                            lb_endpoints=lb_endpoints,
                        )],
                    ),
                ),
            )

        return json.dumps(clusters, cls=ClusterEncoder, indent=4)

    return app


def main(_argv):
    serve(create_app(), listen='*:8888')


if __name__ == '__main__':
    main(sys.argv)
