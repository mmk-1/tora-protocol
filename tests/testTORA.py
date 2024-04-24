import networkx as nx
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from matplotlib import pyplot as plt

from adhoccomputing.GenericModel import Topology

from TORA.TORAComponent import TORANode, TORAHeight


def main():
    graph = nx.Graph()

    graph.add_edge(0, 1)
    graph.add_edge(0, 7)
    graph.add_edge(0, 3)
    graph.add_edge(1, 6)
    graph.add_edge(6, 5)
    graph.add_edge(6, 4)
    graph.add_edge(4, 2)

    nx.draw(graph, with_labels=True, font_weight="bold")
    plt.draw()
    # plt.show()
    plt.savefig("initial_graph.png")
    
    '''
    # Start TORA
    # 1. Create topology
    # 2. Set source
    # 3. Set destination
    # 3a. Set destination height to 0
    # 4. Create route to destination
    # 5. Start
    topology = Topology()
    topology.construct_from_graph(graph, TORANode, Channel)
    source_id = 0
    destination_id = 7
    topology.nodes[destination_id].set_height(TORAHeight(0, 0, 0, 0, destination_id))
    topology.start()
    topology.nodes[source_id].create_route(destination_id)
    
    set destination height!!!!!!!!!
    
    
    def init_route_creation(self, did: int):
        self.appllayer.handle_qry(did, self.componentinstancenumber)
        
    
    
    topology.nodes[source_id].send_message(destination_id, "Hello World!")
    '''
    topology = Topology()
    topology.construct_from_graph(graph, TORANode, GenericChannel)
    print(len(topology.nodes))
    source_id = 0
    destination_id = 7
    destination_height: TORAHeight = TORAHeight(0, 0, 0, 0, destination_id)
    topology.start()
    topology.nodes[destination_id].set_height(destination_height)
    topology.nodes[source_id].app_layer.handle_query(destination_id)

    print("Routing done!")

    # Draw final DAG

if __name__ == "__main__":
    main()
