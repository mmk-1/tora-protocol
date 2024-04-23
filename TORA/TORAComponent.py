import time
from enum import Enum
from typing import Dict, Tuple, List

from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import ConnectorTypes, Event, EventTypes
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.NetworkLayer.GenericNetworkLayer import GenericNetworkLayer

# Types
from adhoccomputing.Generics import GenericMessage, GenericMessageHeader, GenericMessagePayload

class TORAPacketTypes(Enum):
    QRY = "QUERY"
    UPD = "UPDATE"
    CLR = "CLEAR"

class TORAHeight:
    def __init__(self, tau: float, oid: int, r: int, delta: int, i: int):
        # (tau, oid, r, delta, i)
        self.tau = tau # Time of link failure
        self.oid = oid # Originator ID (ID of node that defined new reference level)
        self.r = r # Reflection bit
        self.delta = delta # Number used for ordering
        self.i = i # Unique ID of the node itself

# Packet Structures
class TORAPacketHeader(GenericMessageHeader):
    pass


# define your own message payload structure
class TORAPacketPayload(GenericMessagePayload):
    pass


class TORAPacketQRYPayload(GenericMessagePayload):
    def __init__(self, destination_id: int):
        self.destination_id: int = destination_id


class TORAPacketCLRPayload(GenericMessagePayload):
    def __init__(self, destination_id: int, reference_level: Tuple[int, int, int]):
        self.destination_id = destination_id
        # TODO: Create a ReferenceLevel class
        self.reference_level: Tuple[int, int, int] = reference_level


class TORAPacketUPDPayload(GenericMessagePayload):
    def __init__(self, destination_id: int, height: TORAHeight, link_reversal: bool):
        self.destination_id: int = destination_id
        self.height: TORAHeight = height
        self.link_reversal: bool = link_reversal


# class ApplicationLayerMessageMessagePayload(GenericMessagePayload):
#     did: int
#     message: str
#
#     def __init__(self, did: int, message: str):
#         self.did = did
#         self.message = message

class TORAComponent(GenericModel):
    def __init__(self, component_id, component_name, topology: Topology):
        '''
        Each node i requires:
        - Height
        - Route-required flag
        - Time of the last update (last time UPD was broadcast)
        - Time when each link (i, j) became active
        '''
        super().__init__(component_name, component_id, topology=topology)

        self.neighbors = topology.get_neighbors(component_id)
        self.height = TORAHeight(None, None, None, None, self.componentinstancenumber)
        # Keep neighbor's heights
        self.N: Dict[int, Tuple[TORAHeight, int]] = {}
        self.last_upd: int = 0
        self.route_required: bool = False

    def on_init(self, eventobj: Event):
        pass

    # When we receive a message
    def on_message_from_bottom(self, eventobj: Event):
        message: GenericMessage = eventobj.eventcontent
        header: GenericMessageHeader = message.header
        # payload: GenericMessagePayload = message.payload

        # Check type of message and handle it!
        if header.messagetype == TORAPacketTypes.QRY:
            self.handle_query(message)
        elif header.messagetype == TORAPacketTypes.CLR:
            pass
        elif header.messagetype == TORAPacketTypes.UPD:
            pass
        else:
            raise Exception("UNKNOWN MESSAGE TYPE!")

    '''
    Functions to handle the messages based on TORAMessageType
    '''
    def handle_query(self, message: GenericMessage):
        # TODO: Make it return a boolean?
        '''
        QRY has a destination id (did)
        '''
        destination_id: int = message.payload.destination_id
        source_id: int = message.header.messagefrom
        downstream_links = self.get_downstream_links()

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
        if len(downstream_links) == 0:
            if self.route_required == 0:
                self.broadcast_query_packet(destination_id)
            return
        elif self.height.delta is None:
            min_height = self.get_minimum_height_between_neighbours()
            self.height = TORAHeight(
                min_height.tau,
                min_height.oid,
                min_height.r,
                min_height.delta + 1,
                self.componentinstancenumber,
            )
            self.broadcast_upd_packet(destination_id, False)
            return
        elif source_id not in self.N or (
            source_id in self.N and self.N[source_id][1] > self.last_upd
        ):
            self.broadcast_upd_packet(destination_id, False)
            return
        # Discard
        return

    def handle_update(self, message: GenericMessage):
        source_id: int = message.header.messagefrom
        destination_id: int = message.payload.destination_id
        height: TORAHeight = message.payload.height
        link_reversal: bool = message.payload.link_reversal
        downstream_links = self.get_downstream_links()
        self.set_neighbour_height(source_id, height)
        downstream_links = self.get_downstream_links()
        '''Excerpt from paper:
        node i first updates the entry HNi, j in its height array with the height contained in the received UPD packet 
        and then reacts as follows:
        
        (a) If the route-required flag is set (which implies that the height of node i is NULL), node i sets 
            its height to Hi = (τj, oidj, rj, δj + 1, i)—where HNi, j = (τj, oidj, rj, δj, j) is the minimum height 
            of its non-NULL neighbors, updates all the entries in its link-state array LS, un-sets the route-required 
            flag and then broadcasts an UPD packet which contains its new height. 
        
        (b) If the route-required flag is not set, node i simply updates the entry LSi, j in its link-state array.
        
        '''

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
                self.maintenance_case_2(destination_id, reference_level)
            elif reference_level[2] == 0:
                self.maintenance_case_3(destination_id, reference_level)
            elif self.componentinstancenumber == reference_level[1]:
                self.maintenance_case_4(destination_id)
            else:
                self.maintenance_case_5(destination_id)
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
                self.rr = 0
                self.broadcast_upd_packet(destination_id, False)
            else:
                if len(downstream_links) == 0 and self.componentinstancenumber != destination_id:
                    self.maintenance_case_1(destination_id)

    def handle_clear(self, message: GenericMessage):
        destination_id: int = message.payload.destination_id
        reference_level: Tuple[int, int, int] = message.payload.reference_level
        # TODO: Double check the logic of this function
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
            self.height = TORAHeight(
                None, None, None, None, self.componentinstancenumber
            )

        for neighbour in self.N:
            if neighbour == destination_id:
                continue
            if reference_level == (
                self.height.tau,
                self.height.oid,
                self.height.r,
            ) or reference_level == (
                self.N[neighbour][0].tau,
                self.N[neighbour][0].oid,
                self.N[neighbour][0].r,
            ):
                self.N[neighbour] = (None, None, None, None, self.componentinstancenumber)
        if reference_level == (self.height.tau, self.height.oid, self.height.r):
            self.broadcast_clr(destination_id, reference_level)

    '''
    Helper functions for the 5 maintainence cases
    1. Generate
    2. Propagate
    3. Reflect
    4. Detect
    5. Generate
    '''
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

        self.broadcast_upd_packet(did, True)

    def maintenance_case_2(self, did: int, reference: TORAHeight):
        self.height = TORAHeight(
            reference.tau,
            reference.oid,
            reference.r,
            reference.delta - 1,
            self.componentinstancenumber,
        )
        self.broadcast_upd_packet(did, True)

    def maintenance_case_3(self, did: int, reference: TORAHeight):
        self.height = TORAHeight(
            reference.tau, reference.oid, 1, 0, self.componentinstancenumber
        )
        self.broadcast_upd(did, True)

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

        self.broadcast_clr_packet(did, (self.height.tau, self.height.oid, 1))

    def maintenance_case_5(self, did: int):
        self.height = TORAHeight(
            time.time(),
            self.componentinstancenumber,
            0,
            0,
            self.componentinstancenumber,
        )
        self.broadcast_upd_packet(did, True)


    # Helper functions
    def set_neighbour_height(self, j: int, height: TORAHeight):
        self.N[j] = (height, time.time())

    def get_upstream_links(self):
        height_delta = -1 if self.height.delta is None else self.height.delta
        return dict(
            filter(lambda link: link[1][0].delta >= height_delta, list(self.N.items()))
        )

    def get_downstream_links(self):
        height_delta = 100000 if self.height.delta is None else self.height.delta
        return dict(
            filter(lambda link: link[1][0].delta < height_delta, list(self.N.items()))
        )

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

    # Broadcast helpers
    def broadcast_query_packet(self, destination_id: int):
        self.route_required = True
        payload: TORAPacketQRYPayload = TORAPacketQRYPayload(destination_id)
        self.broadcast(TORAPacketTypes.QRY, payload)

    def broadcast_upd_packet(self, destination_id: int, link_reversal: bool):
        self.last_upd = time.time()
        payload: TORAPacketUPDPayload = TORAPacketUPDPayload(destination_id, self.height, link_reversal)
        self.broadcast(TORAPacketTypes.UPD, payload)

    def broadcast_clr_packet(self, destination_id: int, reference_level):
        payload: TORAPacketCLRPayload = TORAPacketCLRPayload(destination_id, reference_level)
        self.broadcast(TORAPacketTypes.CLR, payload)

    def broadcast(self, message_type: TORAPacketTypes, payload: GenericMessagePayload):
        # TODO: Rethink the way packet creation and broadcasting is handled
        for destination in self.neighbors:
            header = TORAPacketHeader(message_type, self.componentinstancenumber, destination)
            message = GenericMessage(header, payload)
            self.send_down(Event(self, EventTypes.MFRT, message))


class TORANode(GenericModel):
    def __init__(self, component_id, component_name, topology):
        super().__init__(component_name, component_id, topology=topology)

        self.app_layer: TORAComponent = TORAComponent(component_id, component_name, topology)
        self.net_layer = GenericNetworkLayer("NetworkLayer", component_id)
        self.link_layer = GenericLinkLayer("LinkLayer", component_id)

        # CONNECTIONS AMONG SUBCOMPONENTS
        self.app_layer.connect_me_to_component(ConnectorTypes.DOWN, self.net_layer)

        self.net_layer.connect_me_to_component(ConnectorTypes.UP, self.app_layer)
        self.net_layer.connect_me_to_component(ConnectorTypes.DOWN, self.link_layer)

        self.link_layer.connect_me_to_component(ConnectorTypes.UP, self.net_layer)

        # Connect the bottom component to the composite component....
        self.link_layer.connect_me_to_component(ConnectorTypes.DOWN, self)
        self.connect_me_to_component(ConnectorTypes.UP, self.link_layer)