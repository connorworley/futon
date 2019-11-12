import itertools
from functools import partial
from functools import wraps

import flask
from envoy.api.v2.cds_pb2 import Cluster
from envoy.api.v2.core.address_pb2 import Address
from envoy.api.v2.core.address_pb2 import SocketAddress
from envoy.api.v2.core.base_pb2 import Locality
from envoy.api.v2.discovery_pb2 import DiscoveryResponse
from envoy.api.v2.discovery_pb2 import DiscoveryRequest
from envoy.api.v2.eds_pb2 import ClusterLoadAssignment
from envoy.api.v2.endpoint.endpoint_pb2 import Endpoint
from envoy.api.v2.endpoint.endpoint_pb2 import LbEndpoint
from envoy.api.v2.endpoint.endpoint_pb2 import LocalityLbEndpoints
from google.protobuf import json_format
from google.protobuf.any_pb2 import Any
from google.protobuf.duration_pb2 import Duration


def k8s_endpoint_to_envoy_endpoint(endpoint, ports, nodes):
    node_names = set(map(
        lambda node_address: node_address.address.node_name,
        itertools.chain.from_iterable(
            map(
                lambda subset: subset.addresses,
                endpoint.subsets,
            ),
        ),
    ))
    nodes = filter(
        lambda node: node.metadata.name in node_names,
        nodes,
    )
    node_addresses = itertools.chain.from_iterable(
        map(
            lambda node: node.status.node_addresses,
            nodes,
        ),
    )
    node_addresses = filter(
        lambda: node_address.type == "InternalIP",
        node_addresses,
    )
    addresses = map(
        lambda node_address: node_address.address,
        node_addresses,
    )

    envoy_endpoints = [
        LocalityLbEndpoints(
            locality=Locality(), # TODO: determine locality of node
            lb_endpoints=[LbEndpoint(
                endpoint=Endpoint(
                    address=Address(
                        socket_address=SocketAddress(
                            address=address,
                            port_value=port,
                        ),
                    ),
                ),
            )],
        )
        for address, port in itertools.product(addresses, ports)
    ]

    return envoy_addresses



def k8s_service_to_envoy_cluster(service, endpoints, nodes):
    service_ports = map(
        lambda port: port.node_port,
        service.spec.ports,
    )

    endpoints = filter(
        lambda endpoint: endpoint.metadata.labels is not None \
        and all( \
            endpoint.metadata.labels.get(key) == value \
            for key, value in service.spec.selector.items() \
        ),
        endpoints,
    )
    envoy_endpoints = map(
        partial(k8s_endpoint_to_envoy_endpoint, ports=service_ports, nodes=nodes),
        endpoints,
    )

    return Cluster(
        connect_timeout=Duration(seconds=5),
        load_assignment=ClusterLoadAssignment(
            cluster_name=service.metadata.name,
            endpoints=envoy_endpoints,
        ),
        name=service.metadata.name,
        type=Cluster.STATIC,
    )


def clusters(k8s_client):
    discovery_request = json_format.Parse(flask.request.data, DiscoveryRequest())

    services = k8s_client.list_service_for_all_namespaces().items
    endpoints = k8s_client.list_endpoints_for_all_namespaces().items
    nodes = k8s_client.list_node().items

    services = filter(
        lambda service: ( \
            len(discovery_request.resource_names) == 0 \
            or service.metadata.name in discovery_request.resource_names \
        ) and service.spec.type == "NodePort",
        services,
    )
    clusters = map(
        partial(k8s_service_to_envoy_cluster, endpoints=endpoints, nodes=nodes),
        services,
    )

    response = DiscoveryResponse()
    # pack clusters into a `repeatable Any` field
    for cluster in clusters:
        cluster_as_any = Any()
        cluster_as_any.Pack(cluster)
        response.resources.append(cluster_as_any)

    return json_format.MessageToJson(response)


def blueprint(k8s_client):
    blueprint = flask.Blueprint(__name__, __name__)
    blueprint.route("/v2/discovery:clusters", methods=["POST"])(
        wraps(clusters)(
            partial(clusters, k8s_client=k8s_client),
        ),
    )
    return blueprint
