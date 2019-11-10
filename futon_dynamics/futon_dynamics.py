import itertools
import json
import logging
import sys
from functools import lru_cache

import kubernetes
from envoy.api.v2.cds_pb2 import Cluster
from envoy.api.v2.core.address_pb2 import Address
from envoy.api.v2.core.address_pb2 import SocketAddress
from envoy.api.v2.discovery_pb2 import DiscoveryResponse
from envoy.api.v2.discovery_pb2 import DiscoveryRequest
from envoy.api.v2.eds_pb2 import ClusterLoadAssignment
from envoy.api.v2.endpoint.endpoint_pb2 import Endpoint
from envoy.api.v2.endpoint.endpoint_pb2 import LbEndpoint
from envoy.api.v2.endpoint.endpoint_pb2 import LocalityLbEndpoints
from flask import Flask
from flask import request
from flask import Response
from google.protobuf.any_pb2 import Any
from google.protobuf.duration_pb2 import Duration
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from waitress import serve


@lru_cache(maxsize=1)
def k8s_client():
    kubernetes.config.load_kube_config()
    return kubernetes.client.CoreV1Api()


def create_app():
    app = Flask(__name__)

    @app.route("/v2/discovery:clusters", methods=["POST"])
    def get_clusters():
        discovery_request = Parse(request.data, DiscoveryRequest())

        clusters = []

        services = k8s_client().list_service_for_all_namespaces(watch=False)
        endpoints = k8s_client().list_endpoints_for_all_namespaces(watch=False)
        nodes = k8s_client().list_node(watch=False)

        for service in services.items:
            if service.spec.type != "NodePort":
                continue
            if len(discovery_request.resource_names) > 0 and service.metadata.name not in discovery_request.resource_names:
                continue

            node_ports = [port.node_port for port in service.spec.ports]

            lb_endpoints = []
            for endpoint in endpoints.items:
                node_addresses = []
                if endpoint.metadata.labels is None:
                    continue
                if not all(
                    [
                        endpoint.metadata.labels.get(key) == value
                        for key, value in service.spec.selector.items()
                    ]
                ):
                    continue
                for subset in endpoint.subsets:
                    for address in subset.addresses:
                        for node in nodes.items:
                            if node.metadata.name != address.node_name:
                                continue
                            for node_address in node.status.addresses:
                                if node_address.type != "InternalIP":
                                    continue
                                node_addresses.append(node_address.address)
                for address, port in itertools.product(node_addresses, node_ports):
                    lb_endpoints.append(
                        LbEndpoint(
                            endpoint=Endpoint(
                                address=Address(
                                    socket_address=SocketAddress(
                                        address=address, port_value=port,
                                    ),
                                ),
                            ),
                        ),
                    )

            clusters.append(
                Cluster(
                    name=service.metadata.name,
                    connect_timeout=Duration(seconds=5),
                    type=Cluster.STATIC,
                    load_assignment=ClusterLoadAssignment(
                        cluster_name=service.metadata.name,
                        endpoints=[LocalityLbEndpoints(lb_endpoints=lb_endpoints,)],
                    ),
                ),
            )

        response = DiscoveryResponse()
        for cluster in clusters:
            cluster_as_any = Any()
            cluster_as_any.Pack(cluster)
            response.resources.append(cluster_as_any)

        return Response(
            MessageToJson(response),
            mimetype='application/json',
        )

    return app


def main(_argv):
    logger = logging.getLogger("waitress")
    logger.setLevel(logging.DEBUG)
    serve(create_app(), listen="*:8888")


if __name__ == "__main__":
    main(sys.argv)
