.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We have implemented the Temporally-Ordered Routing Algorithm in Python as is available as an open-source repository on Github. The implementation is based on the algorithm described in the paper in section 1.3 and follows the structure of AHCv2 and utilizes its components (e.g. channels, generic messages, etc.). For the evaluation phase, this algorithm is benchmarked with different topologies structures and sizes. The results along with the discussion are presented in the next section. Additionally you can view the TORA component module in the Python Module Index of this document.

The setup included the usage of Python and a Docker container which is included in the repository of this project.

Results
~~~~~~~~

For the evaluation phase, the implementation was benchmarked within four topological structures. These four were: complete graph, ring graph, star graph, and tree. For each topology, we tested it with different topology sizes ranging from 5-75 nodes. Each run included the generation of a random topology with by using the "networkx" library for Python. Moreover, for each topology, a random source and destination was generated and the routing algorithm was run afterwards. However, to minimize the effect of randomness, the routing algorithm was run 3 times for each topology and the average of the results was taken. 

Although higher number of topology was attempted to be tested, due to the limitation of the computer that this algorithm was tested on and the multi-threaded nature of AHCv2, the number of nodes couldn't go higher than 75. The results are shown in the following figure.




.. image:: figures/benchmark_chart.png
  :width: 800
  :alt: TORA benchmark


Discussion
~~~~~~~~~~

In the figure, we observe that the routing performance of TORA (Temporally Ordered Routing Algorithm) is comparable for tree, cyclic graph, and star graph topologies. However, when applied to a complete graph, TORA experiences a significant increase in routing time. This outcome is not surprising, considering that complete graphs have a larger number of edges and nodes compared to other topologies. Consequently, the higher message exchange rate in complete graphs contributes to the longer routing time.

The main takeaway from this evaluation is that TORA is a scalable routing algorithm that performs well in various topological structures. However, the routing time increases with the complexity of the topology, as seen in the complete graph scenario. This result highlights the importance of considering the network topology when selecting a routing algorithm. TORA is particularly suitable for tree, cyclic, and star graph topologies, where it demonstrates efficient routing performance.



