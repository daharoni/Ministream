import React, { useState, useEffect } from 'react';
import ReactFlow, { Background, Controls } from 'reactflow';
import 'reactflow/dist/style.css';
import { fetchSystemTopology } from '../services/api';

const SystemTopology = () => {
  const [elements, setElements] = useState([]);

  useEffect(() => {
    const fetchTopology = async () => {
      const topology = await fetchSystemTopology();
      const flowElements = convertTopologyToFlowElements(topology);
      setElements(flowElements);
    };

    fetchTopology();
    const interval = setInterval(fetchTopology, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const convertTopologyToFlowElements = (topology) => {
    const elements = [];

    // Add network_api node
    elements.push({
      id: 'network_api',
      type: 'default',
      data: { label: 'Network API' },
      position: { x: 250, y: 5 },
    });

    // Add edge nodes
    topology.edgeNodes.forEach((node, index) => {
      elements.push({
        id: node.id,
        type: 'default',
        data: { label: `Edge Node: ${node.id}` },
        position: { x: 100 + index * 200, y: 100 },
      });
      elements.push({
        id: `edge-${node.id}`,
        source: 'network_api',
        target: node.id,
        animated: true,
      });
    });

    // Add clients
    topology.clients.forEach((client, index) => {
      elements.push({
        id: client.id,
        type: 'default',
        data: { label: `Client: ${client.id}` },
        position: { x: 100 + index * 200, y: 200 },
      });
      if (client.connectedTo === 'network_api') {
        elements.push({
          id: `client-edge-${client.id}`,
          source: 'network_api',
          target: client.id,
        });
      } else {
        elements.push({
          id: `client-edge-${client.id}`,
          source: client.connectedTo,
          target: client.id,
        });
      }
    });

    return elements;
  };

  return (
    <div style={{ height: '500px', width: '100%' }}>
      <ReactFlow elements={elements} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default SystemTopology;