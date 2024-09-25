import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, { Controls, Background, useNodesState, useEdgesState, addEdge } from 'reactflow';
import 'reactflow/dist/style.css';
import { fetchSystemTopology } from '../services/api';

const SystemTopology = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [initialRender, setInitialRender] = useState(true);

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  useEffect(() => {
    const fetchTopology = async () => {
      try {
        const topology = await fetchSystemTopology();
        if (initialRender) {
          const { newNodes, newEdges } = convertTopologyToElements(topology);
          setNodes(newNodes);
          setEdges(newEdges);
          setInitialRender(false);
        } else {
          updateNodesAndEdges(topology);
        }
      } catch (error) {
        console.error('Error fetching system topology:', error);
      }
    };

    fetchTopology();
    const interval = setInterval(fetchTopology, 5000);

    return () => clearInterval(interval);
  }, [initialRender, setNodes, setEdges]);

  const convertTopologyToElements = (topology) => {
    const newNodes = [];
    const newEdges = [];

    // Add network_api node
    newNodes.push({
      id: 'network_api',
      type: 'default',
      data: { label: 'Network API' },
      position: { x: 0, y: 0 },
      style: { background: '#6ede87', color: '#333', border: '1px solid #222138', width: 120, height: 40 },
    });

    // Add edge nodes
    topology.edgeNodes.forEach((node, index) => {
      newNodes.push({
        id: node.id,
        type: 'default',
        data: { label: `Edge Node: ${node.id.slice(0, 8)}...` },
        position: { x: index * 150, y: 100 },
        style: { background: '#ff9966', color: '#333', border: '1px solid #222138', width: 120, height: 40 },
      });
      newEdges.push({
        id: `edge-${node.id}`,
        source: 'network_api',
        target: node.id,
        animated: true,
        style: { stroke: '#222' },
      });
    });

    // Add clients
    topology.clients.forEach((client, index) => {
      newNodes.push({
        id: client.id,
        type: 'default',
        data: { label: `Client: ${client.id}` },
        position: { x: index * 150, y: 200 },
        style: { background: '#6495ed', color: '#333', border: '1px solid #222138', width: 120, height: 40 },
      });
      newEdges.push({
        id: `client-edge-${client.id}`,
        source: client.connectedTo,
        target: client.id,
        style: { stroke: '#222' },
      });
    });

    return { newNodes, newEdges };
  };

  const updateNodesAndEdges = (topology) => {
    setNodes((prevNodes) => {
      const updatedNodes = [...prevNodes];

      // Update existing nodes and add new ones
      topology.edgeNodes.forEach((node, index) => {
        const existingNodeIndex = updatedNodes.findIndex(n => n.id === node.id);
        if (existingNodeIndex !== -1) {
          updatedNodes[existingNodeIndex] = {
            ...updatedNodes[existingNodeIndex],
            data: { label: `Edge Node: ${node.id.slice(0, 8)}...` },
          };
        } else {
          updatedNodes.push({
            id: node.id,
            type: 'default',
            data: { label: `Edge Node: ${node.id.slice(0, 8)}...` },
            position: { x: index * 150, y: 100 },
            style: { background: '#ff9966', color: '#333', border: '1px solid #222138', width: 120, height: 40 },
          });
        }
      });

      // Similar logic for clients
      topology.clients.forEach((client, index) => {
        const existingNodeIndex = updatedNodes.findIndex(n => n.id === client.id);
        if (existingNodeIndex !== -1) {
          updatedNodes[existingNodeIndex] = {
            ...updatedNodes[existingNodeIndex],
            data: { label: `Client: ${client.id}` },
          };
        } else {
          updatedNodes.push({
            id: client.id,
            type: 'default',
            data: { label: `Client: ${client.id}` },
            position: { x: index * 150, y: 200 },
            style: { background: '#6495ed', color: '#333', border: '1px solid #222138', width: 120, height: 40 },
          });
        }
      });

      return updatedNodes;
    });

    setEdges((prevEdges) => {
      const updatedEdges = [...prevEdges];

      // Update existing edges and add new ones
      // ... (implement similar logic for edges)

      return updatedEdges;
    });
  };

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <div style={{ position: 'absolute', top: '10px', left: '10px', zIndex: 10, fontSize: '14px', fontWeight: 'bold' }}>
        System Topology
      </div>
      <ReactFlow 
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        style={{ width: '100%', height: '100%' }}
        attributionPosition="bottom-left"
      >
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  );
};

export default SystemTopology;