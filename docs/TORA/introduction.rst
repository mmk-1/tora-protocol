.. include:: substitutions.rst

Introduction
============


Mobile wireless networks present a unique challenge in routing due to their dynamic and unpredictable nature. The problem at hand is to develop a routing algorithm that can effectively adapt to rapid changes in network topology while maintaining efficiency and scalability. This problem is of significant interest and importance as mobile wireless networks are becoming increasingly prevalent, and reliable routing is essential for seamless communication in such environments. Failure to solve this problem can lead to network congestion, packet loss, and inefficient data transmission. 

While several algorithms exist to address the complexity of mobile wireless networks, such as DSDV and LMR, they each have their own drawbacks. For example, not being quick enough to react to the topological changes in the network or providing a single-path route to the destination. The challenge lies in designing a routing algorithm that can provide stable and efficient routes in the face of frequent network disruptions. Previous solutions have often been limited by their inability to localize reactions to topological changes, leading to high communication overhead and slow adaptation to network dynamics. The Temporally-Ordered Routing Algorithm (TORA) offered a novel approach by providing multi-path routes, ensuring loop-free routes and rapid route establishment.

This report will introduce the Temporally-Ordered Routing Algorithm and its implementation as part of the AHCv2 framework. This algorithm is highly adaptive distributed routing algorithm leading to localized reactions and minimized communication overhead.

In this report we will have the following contributions:

- Algorithm and implementation of the Temporally-Ordered Routing Algorithm (TORA) for mobile wireless networks. Implementation is detailed in Section 1.3.

- Examination of the performance of this algorithms across diverse topologies scenarios. Results from these investigations are outlined in Section 1.4.