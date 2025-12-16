"""
Knowledge Graph Service

Responsible for building and visualizing knowledge graphs from summaries.
Creates a comprehensive diagram showing relationships between concepts.
"""

from typing import List, Dict, Set, Tuple
from pathlib import Path
import json

from ..models import Summary, KnowledgeNode, KnowledgeEdge
from ..utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeGraphService:
    """Service for building and visualizing knowledge graphs."""

    def __init__(self, output_dir: Path):
        """
        Initialize knowledge graph service.

        Args:
            output_dir: Directory to save graph visualizations
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_graph(self, summaries: List[Summary]) -> Tuple[List[KnowledgeNode], List[KnowledgeEdge]]:
        """
        Build knowledge graph from summaries.

        Args:
            summaries: List of Summary objects

        Returns:
            Tuple of (nodes, edges)
        """
        logger.info(f"Building knowledge graph from {len(summaries)} summaries")

        nodes = {}
        edges = []

        # Extract nodes and edges from each summary
        for summary in summaries:
            # Add file as a node
            file_node_id = f"file_{hash(str(summary.source_file.file_path))}"
            if file_node_id not in nodes:
                nodes[file_node_id] = KnowledgeNode(
                    node_id=file_node_id,
                    label=summary.source_file.file_name,
                    node_type="document",
                    source_files=[str(summary.source_file.file_path)],
                    attributes={
                        "file_type": summary.source_file.file_type.value,
                        "path": summary.source_file.relative_path
                    }
                )

            # Add entities as nodes
            for entity in summary.entities:
                entity_id = f"entity_{self._normalize_name(entity)}"
                if entity_id not in nodes:
                    nodes[entity_id] = KnowledgeNode(
                        node_id=entity_id,
                        label=entity,
                        node_type="component",
                        source_files=[str(summary.source_file.file_path)]
                    )
                else:
                    # Add source file if not already present
                    if str(summary.source_file.file_path) not in nodes[entity_id].source_files:
                        nodes[entity_id].source_files.append(str(summary.source_file.file_path))

                # Connect entity to file
                edges.append(KnowledgeEdge(
                    source_node_id=file_node_id,
                    target_node_id=entity_id,
                    relationship_type="contains",
                    attributes={"source_file": summary.source_file.file_name}
                ))

            # Add key concepts as nodes
            for concept in summary.key_concepts:
                concept_id = f"concept_{self._normalize_name(concept)}"
                if concept_id not in nodes:
                    nodes[concept_id] = KnowledgeNode(
                        node_id=concept_id,
                        label=concept,
                        node_type="concept",
                        source_files=[str(summary.source_file.file_path)]
                    )
                else:
                    if str(summary.source_file.file_path) not in nodes[concept_id].source_files:
                        nodes[concept_id].source_files.append(str(summary.source_file.file_path))

                # Connect concept to file
                edges.append(KnowledgeEdge(
                    source_node_id=file_node_id,
                    target_node_id=concept_id,
                    relationship_type="discusses",
                    attributes={"source_file": summary.source_file.file_name}
                ))

            # Add explicit relationships
            for rel in summary.relationships:
                source_entity = rel.get('source', '')
                target_entity = rel.get('target', '')
                rel_type = rel.get('type', 'relates_to')

                if source_entity and target_entity:
                    source_id = f"entity_{self._normalize_name(source_entity)}"
                    target_id = f"entity_{self._normalize_name(target_entity)}"

                    # Ensure nodes exist
                    if source_id not in nodes:
                        nodes[source_id] = KnowledgeNode(
                            node_id=source_id,
                            label=source_entity,
                            node_type="component",
                            source_files=[str(summary.source_file.file_path)]
                        )

                    if target_id not in nodes:
                        nodes[target_id] = KnowledgeNode(
                            node_id=target_id,
                            label=target_entity,
                            node_type="component",
                            source_files=[str(summary.source_file.file_path)]
                        )

                    edges.append(KnowledgeEdge(
                        source_node_id=source_id,
                        target_node_id=target_id,
                        relationship_type=rel_type,
                        weight=2.0,  # Higher weight for explicit relationships
                        attributes={"source_file": summary.source_file.file_name}
                    ))

        logger.info(f"✓ Built graph with {len(nodes)} nodes and {len(edges)} edges")
        return list(nodes.values()), edges

    def visualize_graph(self, nodes: List[KnowledgeNode], edges: List[KnowledgeEdge],
                       output_filename: str = "knowledge_graph") -> Dict[str, Path]:
        """
        Create visualizations of the knowledge graph.

        Args:
            nodes: List of KnowledgeNode objects
            edges: List of KnowledgeEdge objects
            output_filename: Base filename for output files

        Returns:
            Dictionary with paths to generated files
        """
        logger.info("Creating knowledge graph visualizations")

        outputs = {}

        # Create NetworkX visualization
        try:
            outputs['networkx'] = self._create_networkx_viz(nodes, edges, output_filename)
        except Exception as e:
            logger.error(f"Failed to create NetworkX visualization: {e}")

        # Create Graphviz visualization
        try:
            outputs['graphviz'] = self._create_graphviz_viz(nodes, edges, output_filename)
        except Exception as e:
            logger.error(f"Failed to create Graphviz visualization: {e}")

        # Create Mermaid diagram
        try:
            outputs['mermaid'] = self._create_mermaid_diagram(nodes, edges, output_filename)
        except Exception as e:
            logger.error(f"Failed to create Mermaid diagram: {e}")

        # Save graph data as JSON
        try:
            outputs['json'] = self._save_graph_json(nodes, edges, output_filename)
        except Exception as e:
            logger.error(f"Failed to save graph JSON: {e}")

        logger.info(f"✓ Created {len(outputs)} visualization files")
        return outputs

    def _create_networkx_viz(self, nodes: List[KnowledgeNode], edges: List[KnowledgeEdge],
                            filename: str) -> Path:
        """Create visualization using NetworkX and Matplotlib."""
        import networkx as nx
        import matplotlib.pyplot as plt

        G = nx.DiGraph()

        # Add nodes
        for node in nodes:
            G.add_node(node.node_id, label=node.label, type=node.node_type)

        # Add edges
        for edge in edges:
            G.add_edge(edge.source_node_id, edge.target_node_id,
                      type=edge.relationship_type, weight=edge.weight)

        # Create layout
        pos = nx.spring_layout(G, k=2, iterations=50)

        # Set up colors by node type
        color_map = {
            'document': '#87CEEB',
            'component': '#98FB98',
            'concept': '#FFB6C1'
        }

        node_colors = [color_map.get(G.nodes[node].get('type', 'concept'), '#D3D3D3')
                      for node in G.nodes()]

        # Draw graph
        plt.figure(figsize=(20, 16))

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=3000, alpha=0.9)

        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True,
                              arrowsize=20, width=2, alpha=0.6)

        # Draw labels
        labels = {node: G.nodes[node]['label'][:30] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')

        plt.title("Choreo Architecture Knowledge Graph", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()

        output_path = self.output_dir / f"{filename}_networkx.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"  ✓ NetworkX visualization: {output_path}")
        return output_path

    def _create_graphviz_viz(self, nodes: List[KnowledgeNode], edges: List[KnowledgeEdge],
                            filename: str) -> Path:
        """Create visualization using Graphviz."""
        import graphviz

        dot = graphviz.Digraph(comment='Knowledge Graph', format='png')
        dot.attr(rankdir='TB', size='20,20')
        dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')

        # Color scheme by node type
        type_colors = {
            'document': '#87CEEB',
            'component': '#98FB98',
            'concept': '#FFB6C1'
        }

        # Add nodes
        for node in nodes:
            color = type_colors.get(node.node_type, '#D3D3D3')
            dot.node(node.node_id, node.label, fillcolor=color)

        # Add edges
        for edge in edges:
            label = edge.relationship_type.replace('_', ' ')
            dot.edge(edge.source_node_id, edge.target_node_id, label=label)

        output_path = self.output_dir / f"{filename}_graphviz"
        dot.render(output_path, cleanup=True)

        final_path = Path(str(output_path) + '.png')
        logger.info(f"  ✓ Graphviz visualization: {final_path}")
        return final_path

    def _create_mermaid_diagram(self, nodes: List[KnowledgeNode], edges: List[KnowledgeEdge],
                               filename: str) -> Path:
        """Create Mermaid diagram syntax."""
        lines = ["graph TB"]

        # Add node definitions
        node_map = {}
        for i, node in enumerate(nodes):
            node_var = f"N{i}"
            node_map[node.node_id] = node_var

            # Style based on type
            if node.node_type == 'document':
                lines.append(f"    {node_var}[[\"{node.label}\"]]")
            elif node.node_type == 'component':
                lines.append(f"    {node_var}[\"{node.label}\"]")
            else:
                lines.append(f"    {node_var}(\"{node.label}\")")

        lines.append("")

        # Add edges
        for edge in edges:
            source_var = node_map.get(edge.source_node_id)
            target_var = node_map.get(edge.target_node_id)
            if source_var and target_var:
                rel_label = edge.relationship_type.replace('_', ' ')
                lines.append(f"    {source_var} -->|{rel_label}| {target_var}")

        # Add styling
        lines.append("")
        lines.append("    classDef document fill:#87CEEB,stroke:#333,stroke-width:2px")
        lines.append("    classDef component fill:#98FB98,stroke:#333,stroke-width:2px")
        lines.append("    classDef concept fill:#FFB6C1,stroke:#333,stroke-width:2px")

        mermaid_content = "\n".join(lines)

        output_path = self.output_dir / f"{filename}_mermaid.md"
        output_path.write_text(mermaid_content)

        logger.info(f"  ✓ Mermaid diagram: {output_path}")
        return output_path

    def _save_graph_json(self, nodes: List[KnowledgeNode], edges: List[KnowledgeEdge],
                        filename: str) -> Path:
        """Save graph data as JSON."""
        graph_data = {
            "nodes": [
                {
                    "id": node.node_id,
                    "label": node.label,
                    "type": node.node_type,
                    "source_files": node.source_files,
                    "attributes": node.attributes
                }
                for node in nodes
            ],
            "edges": [
                {
                    "source": edge.source_node_id,
                    "target": edge.target_node_id,
                    "type": edge.relationship_type,
                    "weight": edge.weight,
                    "attributes": edge.attributes
                }
                for edge in edges
            ],
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "node_types": list(set(n.node_type for n in nodes))
            }
        }

        output_path = self.output_dir / f"{filename}.json"
        with open(output_path, 'w') as f:
            json.dump(graph_data, f, indent=2)

        logger.info(f"  ✓ Graph JSON: {output_path}")
        return output_path

    def _normalize_name(self, name: str) -> str:
        """Normalize name for use as node ID."""
        return name.lower().replace(' ', '_').replace('-', '_').replace('/', '_')

