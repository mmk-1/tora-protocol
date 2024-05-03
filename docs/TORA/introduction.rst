.. include:: substitutions.rst

Introduction
============


Mobile wireless networks present a unique challenge in routing due to their dynamic and unpredictable nature. The problem at hand is to develop a routing algorithm that can effectively adapt to rapid changes in network topology while maintaining efficiency and scalability. This problem is of significant interest and importance as mobile wireless networks are becoming increasingly prevalent, and reliable routing is essential for seamless communication in such environments. Failure to solve this problem can lead to network congestion, packet loss, and inefficient data transmission. 

The complexity of mobile wireless networks makes traditional routing approaches inadequate, as naive methods struggle to react quickly to topological changes. The challenge lies in designing a routing algorithm that can provide stable and efficient routes in the face of frequent network disruptions. Previous solutions have often been limited by their inability to localize reactions to topological changes, leading to high communication overhead and slow adaptation to network dynamics. The Temporally-Ordered Routing Algorithm (TORA) offers a novel approach by utilizing a “physical or logical clock” to structure reactions, ensuring loop-free routes and rapid route establishment.

Despite the advancements in routing algorithms, the specific requirements of mobile wireless networks have not been fully addressed until the introduction of TORA. This algorithm differs from previous solutions by decoupling control message propagation from the rate of topological changes, leading to localized reactions and minimized communication overhead. The key components of TORA include its source-initiated approach, loop-free route establishment, and adaptivity to dynamic network conditions. Understanding the limitations of TORA is crucial for its successful implementation in real-world mobile wireless networks.
Contributions:
- Implementation of the Temporally-Ordered Routing Algorithm (TORA) for mobile wireless networks. Implementation is detailed in Section 1.3.
- Examination of the performance of this algorithms across diverse topologies and usage scenarios. Results from these investigations are outlined in Section 1.4.