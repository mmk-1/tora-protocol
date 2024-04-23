from enum import Enum

from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import ConnectorTypes, Event, EventTypes
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.NetworkLayer.GenericNetworkLayer import GenericNetworkLayer

# Types
from adhoccomputing.Generics import GenericMessage, GenericMessageHeader, GenericMessagePayload

class TORAMessageTypes( Enum):
    QRY = "QUERY"
    UPD = "UPDATE"
    CLR = "CLEAR"

class TORAHeight:
    def __init__(self, tau: float, oid: int, r: int, delta: int, i: int):
        self.tau = tau
        self.oid = oid
        self.r = r
        self.delta = delta
        self.i = i

class TORAComponent(GenericModel):
    def __init__(self, component_id, component_name, topology: Topology):
        super().__init__(component_name, component_id, topology=topology)

        self.neighbors = topology.get_neighbors(component_id)
        self.height = TORAHeight(None, None, None, None, self.componentinstancenumber)

    def on_init(self, eventobj: Event):
        pass

    # When we receive a message
    def on_message_from_bottom(self, eventobj: Event):
        message: GenericMessage = eventobj.eventcontent
        header: GenericMessageHeader = message.header
        payload: GenericMessagePayload = message.payload

        # Check type of message and handle it!
        if header.messagetype == TORAMessageTypes.QRY:
            pass
        elif header.messagetype == TORAMessageTypes.CLR:
            pass
        elif header.messagetype == TORAMessageTypes.UPD:
            pass
        else:
            raise Exception("UNKNOWN MESSAGE TYPE!")

    '''
    Functions to handle the messages based on TORAMessageType
    '''
    def handle_query(self):
        pass

    def handle_update(self):
        pass

    def handle_clear(self):
        pass

    



class TORANode(GenericModel):
    def __init__(self, component_id, component_name, topology):
        self.app_layer = TORAComponent(component_id, component_name, topology)

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

        super().__init__(component_name, component_id)