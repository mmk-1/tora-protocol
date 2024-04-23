import networkx as nx
from matplotlib import pyplot as plt

from adhoccomputing.GenericModel import Topology
from ..TORA import TORANode, TORAHeight


def main():
    G = nx.Graph()

    G.add_edge(0, 1)
    G.add_edge(0, 7)
    G.add_edge(0, 3)
    G.add_edge(1, 6)
    G.add_edge(6, 5)
    G.add_edge(6, 4)
    G.add_edge(4, 2)

    nx.draw(G, with_labels=True, font_weight="bold")
    plt.draw()
    plt.show()
    
    '''
    # Start TORA
    # 1. Create topology
    # 2. Set source
    # 3. Set destination
    # 3a. Set destination height to 0
    # 4. Create route to destination
    # 5. Start
    topology = Topology()
    topology.construct_from_graph(G, TORANode, Channel)
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

    # Draw final DAG

if __name__ == "__main__":
    main()