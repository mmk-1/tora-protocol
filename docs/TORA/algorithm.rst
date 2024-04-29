.. include:: substitutions.rst

|TORA|
=========================================



Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Temporally-Ordered Routing Algorithm was originally proposed in [CITATION] by Vincent D. Park and M. Scott Corson. TORA is a distributed algorithm designed for mobile ad hoc networks to establish and maintain efficient routes in dynamic network environments. The algorithm is based on the concept of link reversal, where nodes maintain a logical link reversal hierarchy to facilitate routing decisions in response to topological changes.

Distributed Algorithm: |TORA|
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the Temporally-Ordered Routing Algorithm (TORA), control packets play a crucial role in facilitating efficient routing in mobile wireless networks. TORA utilizes three main types of control packets: Query (QRY), Clear (CLR), and Update (UPD). When a node needs to establish or update a route to a destination, it broadcasts a Query (QRY) packet to its neighbors. Upon receiving a QRY packet, neighboring nodes determine their relative positions in the network and create a directed acyclic graph (DAG) based on this information. The DAG helps in establishing a logical link reversal hierarchy for routing decisions.

The handling of control packets in TORA is based on the concept of link reversal. When a link failure occurs, the affected node broadcasts a Clear (CLR) packet to inform its neighbors about the failure. Neighboring nodes then propagate the CLR packet, triggering a process of link reversal to re-establish routes around the failed link. Additionally, Update (UPD) packets are used to disseminate information about changes in the network topology, ensuring that all nodes have up-to-date routing information.

In TORA, the creation of a route involves the establishment of a directed acyclic graph (DAG) based on the relative positions of nodes in the network. This DAG helps in determining the logical link reversal hierarchy, which guides the routing decisions in response to topological changes. The algorithm ensures loop-free routes by utilizing the DAG structure and maintaining multiple routes for any given source/destination pair, enhancing the robustness of the routing process.

TORA defines five cases for route maintenance to handle various scenarios in dynamic network environments:

- Case 1 (Generate):
This case occurs when a node loses its last downstream link to the destination.
The node generates a new reference level and broadcasts it to its neighbors.
By creating a new reference level, the node initiates the process of establishing a new route to the destination.

- Case 2 (Propagate):
In this case, a node has no downstream links due to a link reversal following the reception of an Update (UPD) packet.
If the ordered sets of (tau, oid, r) are not equal for all neighbors, the node propagates the reference level of its highest neighbor.
The node selects a height that is lower than all neighbors with that reference level, ensuring the establishment of a new route based on the propagated information.

- Case 3 (Reflect):
When a node has no downstream links due to a link reversal following the reception of an UPD packet and the ordered sets of (tau, oid, r) are equal for all neighbors, with r = 0.
In this scenario, the node reflects back a higher sub-level, maintaining the consistency of the reference levels among neighbors.
This action helps in maintaining the integrity of the routing hierarchy and ensuring efficient route establishment.

- Case 4 (Detect):
This case is triggered when a partition in the network is detected, indicating a significant topological change.
Node i sets its height and the height entry for each neighbor to NULL, except when the destination is a neighbor, in which case the corresponding height entry is set to ZERO.
All entries in the link-state array are updated, and a Clear (CLR) packet is broadcast to erase invalid routes and initiate the route re-establishment process.

- Case 5 (Generate):
Similar to Case 1, this case involves generating a new reference level when a node loses its last downstream link to the destination.
The node creates a new reference level and broadcasts it to neighbors, initiating the process of establishing a new route to the destination.
This action ensures that the routing hierarchy is maintained and that routes are efficiently re-established in response to topological changes.

.. _BlindFloodingAlgorithmLabel:

.. code-block:: RST
    :linenos:
    :caption: Temporally-Ordered Routing Algorithm
    

    bool referenceLevelRecorded, reflectionBitSet[c] for all neighbors c of node i; 
    referenceLevelQueue stateQueue[c] for all neighbors c of node i;

    If node i wants to initiate route maintenance 
        perform procedure InitiateRouteMaintenance(i);

    If node i receives a control message msg through an incoming channel c0
        if referenceLevelRecorded = true and reflectionBitSet[c0] = false then 
            stateQueue[c0] ← append(stateQueue[c0], msg);
        end if

    If node i receives ⟨reflection⟩ through an incoming channel c0
        perform procedure InitiateRouteMaintenance(i);
        reflectionBitSet[c0] ← true;
        if reflectionBitSet[c] = true for all neighbors c of node i then
            terminate; 
        end if

    Procedure InitiateRouteMaintenance(i)
    if referenceLevelRecorded = false then
        referenceLevelRecorded ← true;
        send ⟨reflection⟩ into each outgoing channel of node i; 
        take a local snapshot of the state of node i;
    end if


Example
~~~~~~~~

Provide an example for the distributed algorithm.

Correctness
~~~~~~~~~~~

The correctness of TORA is ensured by its ability to establish loop-free routes, react to topological changes within a finite time, and maintain stable routing in dynamic network environments. Safety is guaranteed by the avoidance of routing loops, while liveness is achieved through timely reactions to link failures and recoveries. Fairness is maintained by treating all nodes equally in updating their routes based on received control packets.


Complexity 
~~~~~~~~~~

1. Time Complexity The Temporally-Ordered Routing Algorithm takes at most O(2D) time units to complete where D is the diameter of the network (maximum number of nodes in the longest path).
2. Space Complexity: The space complexity is O(D_d*A) where D_d is the number of maximum desired destinations and A is the average number of adjacent nodes.

.. [Fokking2013] Wan Fokkink, Distributed Algorithms An Intuitive Approach, The MIT Press Cambridge, Massachusetts London, England, 2013
.. [Tel2001] Gerard Tel, Introduction to Distributed Algorithms, CAMBRIDGE UNIVERSITY PRESS, 2001
.. [Lamport1985] Leslie Lamport, K. Mani Chandy: Distributed Snapshots: Determining Global States of a Distributed System. In: ACM Transactions on Computer Systems 3. Nr. 1, Februar 1985.