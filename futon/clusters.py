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


def k8s_service_to_envoy_cluster(service, pods):
    ports = map(
        lambda port: port.node_port,
        service.spec.ports,
    )

    pods = filter(
        lambda pod: pod.metadata.labels is not None \
        and all( \
            pod.metadata.labels.get(key) == value \
            for key, value in service.spec.selector.items() \
        ),
        pods,
    )

    addresses = map(
        lambda pod: pod.status.host_ip,
        pods,
    )

    return Cluster(
        connect_timeout=Duration(seconds=5),
        load_assignment=ClusterLoadAssignment(
            cluster_name=service.metadata.name,
            endpoints=[
                LocalityLbEndpoints(
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
            ],
        ),
        name=service.metadata.name,
        type=Cluster.STATIC,
    )


def clusters(k8s_client):
    discovery_request = json_format.Parse(flask.request.data, DiscoveryRequest())

    services = k8s_client.list_service_for_all_namespaces().items
    pods = k8s_client.list_pod_for_all_namespaces().items

    services = filter(
        lambda service: ( \
            len(discovery_request.resource_names) == 0 \
            or service.metadata.name in discovery_request.resource_names \
        ) and service.spec.type == "NodePort",
        services,
    )
    clusters = map(
        partial(k8s_service_to_envoy_cluster, pods=pods),
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
