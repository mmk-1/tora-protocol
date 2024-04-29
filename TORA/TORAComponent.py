import time
from enum import Enum
from threading import Lock
import threading
from typing import Dict, Tuple, List

from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import ConnectorTypes, Event, EventTypes
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.NetworkLayer.GenericNetworkLayer import GenericNetworkLayer

# Types
from adhoccomputing.Generics import GenericMessage, GenericMessageHeader, GenericMessagePayload

INITIAL_TIME = float('inf')
benchmark_time_lock: Lock = Lock()
benchmark_time: float = float('inf')

class TORAHeight:
    def __init__(self, tau: float, oid: int, r: int, delta: int, i: int):
        self.tau = tau
        self.oid = oid
        self.r = r
        self.delta = delta
        self.i = i

class ReferenceLevel:
    def __init__(self, tau: float, oid: int, r: int):
        self.tau = tau
        self.oid = oid
        self.r = r

# TORA message types & payloads
class TORAControlMessageTypes(Enum):
    UPD = "UPDATE"
    CLR = "CLEAR"
    QRY = "QUERY"

class QueryMessagePayload(GenericMessagePayload):
    def __init__(self, did: int):
        self.did = did


class ClearMessagePayload(GenericMessagePayload):
    def __init__(self, did: int, reference: ReferenceLevel):
        self.did = did
        self.reference: ReferenceLevel = reference


class UpdateMessagePayload(GenericMessagePayload):
    def __init__(self, did: int, height: TORAHeight, link_reversal: bool):
        self.did = did
        self.height = height
        self.link_reversal = link_reversal


# The Application Layer for TORA
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
        self.height: TORAHeight = TORAHeight(None, None, None, None, self.componentinstancenumber)
        self.last_update = 0
        self.route_required: bool = False
        self.neighbor_heights: Dict[int, Tuple[TORAHeight, int]] = {}
        self.lock: Lock = Lock()

    def on_init(self, eventobj: Event):
        pass
    
    # When node gets message
    def on_message_from_bottom(self, eventobj: Event):
        self.update_time()
        with self.lock:
            try:
                message = eventobj.eventcontent
                header = message.header
                payload: GenericMessagePayload = message.payload
                if header.messagetype == TORAControlMessageTypes.QRY:
                    # print("GOT QRY")
                    # print(payload.)
                    self.process_query_message(payload.did, header.messagefrom)
                elif header.messagetype == TORAControlMessageTypes.UPD:
                    self.process_update_message(payload.did,header.messagefrom,payload.height,payload.link_reversal)
                elif header.messagetype == TORAControlMessageTypes.CLR:
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
        downstream_links = self.find_downstream_links()

        if len(downstream_links) == 0:
            if self.route_required == False:
                broadcaster = self.Broadcaster(self, TORAControlMessageTypes.QRY, self.componentinstancenumber, did)
                broadcaster.broadcast()
            else:
                pass
        elif self.height.delta is None:
            min_height = self.find_minimum_neighbor_height()
            self.height = TORAHeight(min_height.tau,min_height.oid,min_height.r,min_height.delta + 1,self.componentinstancenumber)
            broadcaster = self.Broadcaster(self, TORAControlMessageTypes.UPD, self.componentinstancenumber, destination_id=did, height=self.height, link_reversal=False)
            broadcaster.broadcast()
        elif fromid not in self.neighbor_heights or (fromid in self.neighbor_heights and self.neighbor_heights[fromid][1] > self.last_update):
            broadcaster = self.Broadcaster(self, TORAControlMessageTypes.UPD, self.componentinstancenumber, destination_id=did, height=self.height, link_reversal=False)
            broadcaster.broadcast()
        else:
            pass

    def process_update_message(self, did: int, from_id: int, height: TORAHeight, link_reversal: bool):
        '''Excerpt from paper:
        node i first updates the entry HNi, j in its height array with the height contained in the received UPD packet 
        and then reacts as follows:
        
        (a) If the route-required flag is set (which implies that the height of node i is NULL), node i sets 
            its height to Hi = (τj, oidj, rj, δj + 1, i)—where HNi, j = (τj, oidj, rj, δj, j) is the minimum height 
            of its non-NULL neighbors, updates all the entries in its link-state array LS, un-sets the route-required 
            flag and then broadcasts an UPD packet which contains its new height. 
        
        (b) If the route-required flag is not set, node i simply updates the entry LSi, j in its link-state array.
        
        '''
        self.update_neighbor_height(from_id, height)
        downstream_links = self.find_downstream_links()

        if link_reversal:
            
            if len(downstream_links):
                return

            upstream_links: List[Tuple[TORAHeight, int]] = list(self.find_upstream_links().items())
            reference_level: TORAHeight = TORAHeight(-1, None, None, None, None)
            same_reference_level = True

            for t in upstream_links:
                upstream_link = t[0]
                if reference_level == (-1, None, None):
                    reference_level = upstream_link
                elif upstream_link.tau != reference_level.tau or upstream_link.oid != reference_level.oid or upstream_link.r != reference_level.r:
                    same_reference_level = False

                if (reference_level.tau, reference_level.oid, reference_level.r) >= (upstream_link.tau, upstream_link.oid, upstream_link.r):
                    reference_level.tau = upstream_link.tau
                    reference_level.oid = upstream_link.oid
                    reference_level.r = upstream_link.r
                    reference_level.delta = min(reference_level.delta, upstream_link.delta)

            if not same_reference_level:
                self.maintenance_case_2(did, reference_level)
            elif reference_level[2] == 0:
                self.maintenance_case_3(did, reference_level)
            elif self.componentinstancenumber == reference_level[1]:
                self.maintenance_case_4(did)
            else:
                self.maintenance_case_5(did)
        else:
            if self.route_required == True:
                min_height = self.find_minimum_neighbor_height()
                self.height = TORAHeight(min_height.tau,min_height.oid,min_height.r,min_height.delta + 1,self.componentinstancenumber)
                self.route_required = False
                broadcaster = self.Broadcaster(self, TORAControlMessageTypes.UPD, self.componentinstancenumber, destination_id=did, height=self.height, link_reversal=False)
                broadcaster.broadcast()
            else:
                if len(downstream_links) == 0 and self.componentinstancenumber != did:
                    self.maintenance_case_1(did)

    def process_clear_message(self, destination_id: int, reference_level: ReferenceLevel):
        '''Excerpt from the paper:
        
        (a) If the reference level in the CLR packet matches the reference level of node i; it sets its height 
            and the height entry for each neighbor j ∈ Ni to NULL (unless the destination is a neighbor, in which 
            case the corresponding height entry is set to ZERO), updates all the entries in its link-state array LS 
            and broadcasts a CLR packet. 
        
        (b) If the reference level in the CLR packet does not match the reference level of node i; it sets the height 
            entry for each neighbor j ∈ Ni (with the same reference level as the CLR packet) to NULL and updates the 
            corresponding link-state array entries. Thus the height of each node in the portion of the network which 
            was partitioned is set to NULL and all invalid routes are erased. 
            If (b) causes node i to lose its last downstream link, it reacts as in case 1 of maintaining routes.
        
        '''
        if reference_level == (self.height.tau, self.height.oid, self.height.r):
            self.height = TORAHeight(None, None, None, None, self.componentinstancenumber)

        for neighbor in self.neighbor_heights:
            if neighbor == destination_id:
                continue
            if reference_level == (self.height.tau,self.height.oid,self.height.r,) or reference_level == (self.neighbor_heights[neighbor][0].tau,self.neighbor_heights[neighbor][0].oid,self.neighbor_heights[neighbor][0].r):
                self.neighbor_heights[neighbor] = (None,None,None,None,self.componentinstancenumber)
        if reference_level == (self.height.tau, self.height.oid, self.height.r):
            broadcaster = self.Broadcaster(self, TORAControlMessageTypes.CLR, self.componentinstancenumber, destination_id=destination_id, reference_level=reference_level)
            broadcaster.broadcast()

    def maintenance_case_1(self, destination_id: int):
        upstream_links = self.find_upstream_links()
        if len(upstream_links) == 0:
            self.height = TORAHeight(None, None, None, None, self.componentinstancenumber)
        else:
            self.height = TORAHeight(time.time(),self.componentinstancenumber,0,0,self.componentinstancenumber)
        broadcaster = self.Broadcaster(self, TORAControlMessageTypes.UPD, self.componentinstancenumber, destination_id=destination_id, height=self.height, link_reversal=True)
        broadcaster.broadcast()

    def maintenance_case_2(self, did: int, reference: TORAHeight):
        self.height = TORAHeight(reference.tau,reference.oid,reference.r,reference.delta - 1,self.componentinstancenumber)
        broadcaster = self.Broadcaster(self, TORAControlMessageTypes.UPD, self.componentinstancenumber, destination_id=did, height=self.height, link_reversal=True)
        broadcaster.broadcast()

    def maintenance_case_3(self, did: int, reference: TORAHeight):
        self.height = TORAHeight(reference.tau, reference.oid, 1, 0, self.componentinstancenumber)
        broadcaster = self.Broadcaster(self, TORAControlMessageTypes.UPD, self.componentinstancenumber, destination_id=did, height=self.height, link_reversal=True)
        broadcaster.broadcast()

    def maintenance_case_4(self, did: int):
        self.height = TORAHeight(None, None, None, None, self.componentinstancenumber)

        for neighbor in self.neighbor_heights:
            if neighbor == did:
                continue
            self.neighbor_heights[neighbor] = (None,None,None,None,self.componentinstancenumber)
        broadcaster = self.Broadcaster(self, TORAControlMessageTypes.CLR, self.componentinstancenumber, destination_id=did, reference_level=(self.height.tau, self.height.oid, 1))
        broadcaster.broadcast()

    def maintenance_case_5(self, did: int):
        self.height = TORAHeight(time.time(),self.componentinstancenumber,0,0,self.componentinstancenumber)
        broadcaster = self.Broadcaster(self, TORAControlMessageTypes.UPD, self.componentinstancenumber, destination_id=did, height=self.height, link_reversal=True)
        broadcaster.broadcast()

    def find_minimum_neighbor_height(self) -> TORAHeight:
        downstream_links = self.find_downstream_links()
        min_height = downstream_links[list(downstream_links)[0]][0]
        min_height_delta = min_height.delta

        for i in list(downstream_links):
            downstream_link = downstream_links[i]
            if min_height_delta > downstream_link[0].delta + 1:
                min_height = downstream_link[0]
                min_height_delta = downstream_link[0].delta + 1

        return min_height

    def find_downstream_links(self):
        height_delta: int = float('inf') if self.height.delta is None else self.height.delta
        return dict(filter(lambda link: link[1][0].delta < height_delta, list(self.neighbor_heights.items())))

    def find_upstream_links(self):
        height_delta = -1 if self.height.delta is None else self.height.delta
        return dict(filter(lambda link: link[1][0].delta >= height_delta, list(self.neighbor_heights.items())))

    def set_height(self, height: TORAHeight):
        self.height = height
        for neighbor in self.neighbors:
            self.topology.nodes[neighbor].app_layer.update_neighbor_height(self.componentinstancenumber, height)

    def update_neighbor_height(self, component_id: int, height: TORAHeight):
        self.neighbor_heights[component_id] = (height, time.time())

    def update_time(self):
        global benchmark_time
        with benchmark_time_lock:
            if benchmark_time < time.time() or benchmark_time == INITIAL_TIME:
                benchmark_time = time.time()

    # Sub component for broadcasting messages
    class Broadcaster:
        def __init__(self, tora_instance, message_type, source_id, destination_id=None, reference_level=None, link_reversal=None, height=None):
            self.tora_instance = tora_instance
            self.message_type = message_type
            self.source_id = source_id
            self.destination_id = destination_id
            self.reference = reference_level
            self.link_reversal = link_reversal
            self.height = height
        
        def broadcast(self):
            if self.message_type == TORAControlMessageTypes.QRY:
                self.tora_instance.route_required = 1
                payload = QueryMessagePayload(self.destination_id)
            elif self.message_type == TORAControlMessageTypes.UPD:
                self.tora_instance.last_update = time.time()
                payload = UpdateMessagePayload(self.destination_id, self.height, self.link_reversal)
            elif self.message_type == TORAControlMessageTypes.CLR:
                payload = ClearMessagePayload(self.destination_id, self.reference)
            else:
                raise Exception("Unknown message type for broadcasting")

            for neighbor in self.tora_instance.neighbors:
                header = GenericMessageHeader(self.message_type, self.source_id, neighbor)
                message = GenericMessage(header, payload)
                self.tora_instance.send_down(Event(self.tora_instance, EventTypes.MFRT, message))


class TORANode(GenericModel):
    def __init__(self, componentname, componentid, topology: Topology):
        super().__init__(componentname, componentid, topology=topology)

        # SUBCOMPONENTS
        self.app_layer = ApplicationLayerTORA("ApplicationLayer", componentid, topology)
        self.net_layer = GenericNetworkLayer("NetworkLayer", componentid, topology=topology)
        self.link_layer = GenericLinkLayer("LinkLayer", componentid, topology=topology)

        # CONNECTIONS AMONG SUBCOMPONENTS
        self.app_layer.connect_me_to_component(ConnectorTypes.DOWN, self.net_layer)
        self.net_layer.connect_me_to_component(ConnectorTypes.UP, self.app_layer)
        self.net_layer.connect_me_to_component(ConnectorTypes.DOWN, self.link_layer)
        self.link_layer.connect_me_to_component(ConnectorTypes.UP, self.net_layer)

        # Connect the bottom component to the composite component....
        self.link_layer.connect_me_to_component(ConnectorTypes.DOWN, self)
        self.connect_me_to_component(ConnectorTypes.UP, self.link_layer)

    def on_init(self, eventobj: Event):
        pass

    def on_message_from_top(self, eventobj: Event):
        self.send_down(Event(self, EventTypes.MFRT, eventobj.eventcontent))

    def on_message_from_bottom(self, eventobj: Event):
        self.send_up(Event(self, EventTypes.MFRB, eventobj.eventcontent))

# Helper functions for testing
def all_edges(topo: Topology):
    edges = []
    for node in topo.nodes:
        downstream_links = topo.nodes[node].app_layer.find_downstream_links()

        for i in list(downstream_links):
            edges.append((node, i))

    return edges

def heights(topo: Topology):
    heights = []
    for node in topo.nodes:
        heights.append((node, topo.nodes[node].app_layer.height.delta))
    return heights

def wait_for_action_to_complete():
    while time.time() - 0.25 < benchmark_time:
        time.sleep(0.25)
    return benchmark_time


def set_benchmark_time():
    global benchmark_time
    benchmark_time = INITIAL_TIME
