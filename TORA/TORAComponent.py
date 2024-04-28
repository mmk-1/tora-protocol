import time
from enum import Enum
from threading import Lock
from typing import Dict, Tuple, List

from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import ConnectorTypes, Event, EventTypes
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.NetworkLayer.GenericNetworkLayer import GenericNetworkLayer

# Types
from adhoccomputing.Generics import GenericMessage, GenericMessageHeader, GenericMessagePayload

INITIAL_TIME = 20000000000
benchmark_time_lock: Lock = Lock()
benchmark_time: float = 20000000000


class ApplicationLayerMessageTypes(Enum):
    UPD = "UPDATE"
    CLR = "CLEAR"
    QRY = "QUERY"


class TORAHeight:
    def __init__(self, tau: float, oid: int, r: int, delta: int, i: int):
        self.tau = tau
        self.oid = oid
        self.r = r
        self.delta = delta
        self.i = i


# define your own message header structure
class ApplicationLayerMessageHeader(GenericMessageHeader):
    pass


# define your own message payload structure
class ApplicationLayerMessagePayload(GenericMessagePayload):
    pass


class ApplicationLayerQueryMessagePayload(GenericMessagePayload):
    did: int

    def __init__(self, did: int):
        self.did = did


class ApplicationLayerClearMessagePayload(GenericMessagePayload):
    did: int
    reference: Tuple[int, int, int]

    def __init__(self, did: int, reference: Tuple[int, int, int]):
        self.did = did
        self.reference = reference


class ApplicationLayerUpdateMessagePayload(GenericMessagePayload):
    did: int
    height: TORAHeight
    link_reversal: bool

    def __init__(self, did: int, height: TORAHeight, link_reversal: bool):
        self.did = did
        self.height = height
        self.link_reversal = link_reversal


class ApplicationLayerMessageMessagePayload(GenericMessagePayload):
    did: int
    message: str

    def __init__(self, did: int, message: str):
        self.did = did
        self.message = message


class ApplicationLayerTORA(GenericModel):
    def __init__(self, componentname, componentinstancenumber, topology: Topology):
        '''
        Each node i requires:
        - Height
        - Route-required flag
        - Time of the last update (last time UPD was broadcast)
        - Time when each link (i, j) became active
        '''
        super().__init__(componentname, componentinstancenumber, topology=topology)
        self.neighbors = topology.get_neighbors(componentinstancenumber)

        self.height: TORAHeight = TORAHeight(
            None, None, None, None, self.componentinstancenumber
        )

        self.last_update: int = 0
        self.route_required: bool = 0
        self.N: Dict[int, Tuple[TORAHeight, int]] = {}
        self.lock: Lock = Lock()

    def on_init(self, eventobj: Event):
        pass
    
    # When node gets message
    def on_message_from_bottom(self, eventobj: Event):
        self.update_time()
        with self.lock:
            try:
                applmessage = eventobj.eventcontent
                hdr = applmessage.header
                payload: GenericMessagePayload = applmessage.payload
                if hdr.messagetype == ApplicationLayerMessageTypes.QRY:
                    print("GOT QRY")
                    # print(payload.)
                    self.process_query_message(payload.did, hdr.messagefrom)
                elif hdr.messagetype == ApplicationLayerMessageTypes.UPD:
                    self.process_update_message(
                        payload.did,
                        hdr.messagefrom,
                        payload.height,
                        payload.link_reversal,
                    )
                elif hdr.messagetype == ApplicationLayerMessageTypes.CLR:
                    self.process_clear_message(payload.did, payload.reference)
                else:
                    raise Exception("Unkown message type")
            except AttributeError:
                print("Attribute Error")
        self.update_time()

    def process_query_message(self, did: int, fromid: int):
        ''' Excerpt from the paper:
        (a) If the receiving node has no downstream links and its router-equired flag is un-set, it re-broadcasts 
            the QRY packet and sets its route-required flag. 
        
        (b) If the receiving node has no downstream links and the route-required flag is set, it discards 
            the QRY packet.
            
        (c) If the receiving node has at least one downstream link and its height is NULL, it sets its height to
            Hi = (τj, oidj, rj, δj + 1, i), where HNi, j = (τj, oidj, rj, δj, j) is the minimum height of its 
            non-NULL neighbors, and broadcasts an UPD packet.
            
        (d) If the receiving node has at least one downstream link and its height is non-NULL, it first compares the 
            time the last UPD packet was broadcast to the time the link over which the QRY packet was received became 
            active. If an UPD packet has been broadcast since the link became active , it discards the QRY packet; 
            otherwise, it broadcasts an UPD packet. If a node has the route-required flag set when a new link is 
            established, it broadcasts a QRY packet.
        '''
        downstream_links = self.get_downstream_links()

        if len(downstream_links) == 0:
            if self.route_required == 0:
                self.broadcast_query_message(did)
            else:
                pass
        elif self.height.delta is None:
            min_height = self.get_minimum_height_between_neighbours()
            self.height = TORAHeight(
                min_height.tau,
                min_height.oid,
                min_height.r,
                min_height.delta + 1,
                self.componentinstancenumber,
            )
            self.broadcast_update_message(did, False)
        elif fromid not in self.N or (
            fromid in self.N and self.N[fromid][1] > self.last_update
        ):
            self.broadcast_update_message(did, False)
        else:
            pass

    def process_update_message(self, did: int, from_id: int, height: TORAHeight, link_reversal: bool):
        self.set_neighbour_height(from_id, height)
        downstream_links = self.get_downstream_links()

        if link_reversal:
            
            if len(downstream_links):
                return

            upstream_links: List[Tuple[TORAHeight, int]] = list(
                self.get_upstream_links().items()
            )
            reference_level: TORAHeight = TORAHeight(-1, None, None, None, None)
            same_reference_level = True

            for t in upstream_links:
                upstream_link = t[0]
                if reference_level == (-1, None, None):
                    reference_level = upstream_link
                elif (
                    upstream_link.tau != reference_level.tau
                    or upstream_link.oid != reference_level.oid
                    or upstream_link.r != reference_level.r
                ):
                    same_reference_level = False

                if (reference_level.tau, reference_level.oid, reference_level.r) >= (
                    upstream_link.tau,
                    upstream_link.oid,
                    upstream_link.r,
                ):
                    reference_level.tau = upstream_link.tau
                    reference_level.oid = upstream_link.oid
                    reference_level.r = upstream_link.r
                    reference_level.delta = min(
                        reference_level.delta, upstream_link.delta
                    )

            if not same_reference_level:
                self.maintenance_case_2(did, reference_level)
            elif reference_level[2] == 0:
                self.maintenance_case_3(did, reference_level)
            elif self.componentinstancenumber == reference_level[1]:
                self.maintenance_case_4(did)
            else:
                self.maintenance_case_5(did)
        else:
            if self.route_required == 1:
                min_height = self.get_minimum_height_between_neighbours()
                self.height = TORAHeight(
                    min_height.tau,
                    min_height.oid,
                    min_height.r,
                    min_height.delta + 1,
                    self.componentinstancenumber,
                )
                self.route_required = 0
                self.broadcast_update_message(did, False)
            else:
                if len(downstream_links) == 0 and self.componentinstancenumber != did:
                    self.maintenance_case_1(did)

    def process_clear_message(self, did: int, reference: Tuple[int, int, int]):
        if reference == (self.height.tau, self.height.oid, self.height.r):
            self.height = TORAHeight(
                None, None, None, None, self.componentinstancenumber
            )

        for neighbour in self.N:
            if neighbour == did:
                continue
            if reference == (
                self.height.tau,
                self.height.oid,
                self.height.r,
            ) or reference == (
                self.N[neighbour][0].tau,
                self.N[neighbour][0].oid,
                self.N[neighbour][0].r,
            ):
                self.N[neighbour] = (
                    None,
                    None,
                    None,
                    None,
                    self.componentinstancenumber,
                )
        if reference == (self.height.tau, self.height.oid, self.height.r):
            self.broadcast_clear_message(did, reference)

    def maintenance_case_1(self, did: int):
        upstream_links = self.get_upstream_links()

        if len(upstream_links) == 0:
            self.height = TORAHeight(
                None, None, None, None, self.componentinstancenumber
            )
        else:
            self.height = TORAHeight(
                time.time(),
                self.componentinstancenumber,
                0,
                0,
                self.componentinstancenumber,
            )

        self.broadcast_update_message(did, True)

    def maintenance_case_2(self, did: int, reference: TORAHeight):
        self.height = TORAHeight(
            reference.tau,
            reference.oid,
            reference.r,
            reference.delta - 1,
            self.componentinstancenumber,
        )
        self.broadcast_update_message(did, True)

    def maintenance_case_3(self, did: int, reference: TORAHeight):
        self.height = TORAHeight(
            reference.tau, reference.oid, 1, 0, self.componentinstancenumber
        )
        self.broadcast_update_message(did, True)

    def maintenance_case_4(self, did: int):
        self.height = TORAHeight(None, None, None, None, self.componentinstancenumber)

        for neighbour in self.N:
            if neighbour == did:
                continue
            self.N[neighbour] = (
                None,
                None,
                None,
                None,
                self.componentinstancenumber,
            )

        self.broadcast_clear_message(did, (self.height.tau, self.height.oid, 1))

    def maintenance_case_5(self, did: int):
        self.height = TORAHeight(
            time.time(),
            self.componentinstancenumber,
            0,
            0,
            self.componentinstancenumber,
        )
        self.broadcast_update_message(did, True)

    def get_minimum_height_between_neighbours(self) -> TORAHeight:
        downstream_links = self.get_downstream_links()
        min_height = downstream_links[list(downstream_links)[0]][0]
        min_height_delta = min_height.delta

        for i in list(downstream_links):
            downstream_link = downstream_links[i]

            if min_height_delta > downstream_link[0].delta + 1:
                min_height = downstream_link[0]
                min_height_delta = downstream_link[0].delta + 1

        return min_height

    def get_downstream_links(self):
        height_delta = 100000 if self.height.delta is None else self.height.delta
        return dict(
            filter(lambda link: link[1][0].delta < height_delta, list(self.N.items()))
        )

    def get_upstream_links(self):
        height_delta = -1 if self.height.delta is None else self.height.delta
        return dict(
            filter(lambda link: link[1][0].delta >= height_delta, list(self.N.items()))
        )

    def broadcast_query_message(self, did: int):
        self.route_required = 1
        self.broadcast(
            ApplicationLayerQueryMessagePayload(did), ApplicationLayerMessageTypes.QRY
        )

    def broadcast_update_message(self, did: int, link_reversal: bool):
        self.last_update = time.time()
        self.broadcast(
            ApplicationLayerUpdateMessagePayload(did, self.height, link_reversal),
            ApplicationLayerMessageTypes.UPD,
        )

    def broadcast_clear_message(self, did: int, reference: Tuple[int, int, int]):
        self.broadcast(
            ApplicationLayerClearMessagePayload(did, reference),
            ApplicationLayerMessageTypes.CLR,
        )

    def broadcast(
        self, payload: GenericMessagePayload, t: ApplicationLayerMessageTypes
    ):
        print(f"Node-{self.componentinstancenumber} is broadcasting a {t} message")
        for destination in self.neighbors:
            hdr = ApplicationLayerMessageHeader(
                t,
                self.componentinstancenumber,
                destination,
            )
            msg = GenericMessage(hdr, payload)
            self.send_down(Event(self, EventTypes.MFRT, msg))

    def set_height(self, height: TORAHeight):
        self.height = height

        for destination_neighbour in self.neighbors:
            Topology().nodes[destination_neighbour].set_neighbour_height(
                self.componentinstancenumber, height
            )

    def set_neighbour_height(self, j: int, height: TORAHeight):
        self.N[j] = (height, time.time())

    def update_time(self):
        global benchmark_time
        with benchmark_time_lock:
            if benchmark_time < time.time() or benchmark_time == INITIAL_TIME:
                benchmark_time = time.time()


class TORANode(GenericModel):
    def __init__(self, componentname, componentid, topology: Topology):
        # SUBCOMPONENTS
        super().__init__(componentname, componentid, topology=topology)
        self.appllayer = ApplicationLayerTORA(
            "ApplicationLayer", componentid, topology
        )
        self.netlayer = GenericNetworkLayer("NetworkLayer", componentid, topology=topology)
        self.linklayer = GenericLinkLayer("LinkLayer", componentid, topology=topology)
        # self.failuredetect = GenericFailureDetector("FailureDetector", componentid)

        # CONNECTIONS AMONG SUBCOMPONENTS
        self.appllayer.connect_me_to_component(ConnectorTypes.DOWN, self.netlayer)
        # self.failuredetect.connectMeToComponent(PortNames.DOWN, self.netlayer)
        self.netlayer.connect_me_to_component(ConnectorTypes.UP, self.appllayer)
        # self.netlayer.connectMeToComponent(PortNames.UP, self.failuredetect)
        self.netlayer.connect_me_to_component(ConnectorTypes.DOWN, self.linklayer)
        self.linklayer.connect_me_to_component(ConnectorTypes.UP, self.netlayer)

        # Connect the bottom component to the composite component....
        self.linklayer.connect_me_to_component(ConnectorTypes.DOWN, self)
        self.connect_me_to_component(ConnectorTypes.UP, self.linklayer)

    def on_init(self, eventobj: Event):
        pass

    def on_message_from_top(self, eventobj: Event):
        self.send_down(Event(self, EventTypes.MFRT, eventobj.eventcontent))

    def on_message_from_bottom(self, eventobj: Event):
        self.send_up(Event(self, EventTypes.MFRB, eventobj.eventcontent))

    def send_message(self, did: int, message: str):
        self.appllayer.handle_msg(did, message)

    def set_neighbour_height(self, j: int, height: TORAHeight):
        self.appllayer.set_neighbour_height(j, height)

# Helper functions for testing
def all_edges(topo: Topology):
    edges = []
    for node in topo.nodes:
        downstream_links = topo.nodes[node].appllayer.get_downstream_links()

        for i in list(downstream_links):
            edges.append((node, i))

    return edges

def heights(topo: Topology):
    heights = []
    for node in topo.nodes:
        heights.append((node, topo.nodes[node].appllayer.height.delta))
    return heights

def wait_for_action_to_complete():
    while time.time() - 0.25 < benchmark_time:
        time.sleep(0.25)
    return benchmark_time


def set_benchmark_time():
    global benchmark_time
    benchmark_time = INITIAL_TIME
