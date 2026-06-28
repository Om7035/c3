from rir.graph import ReasoningGraph

class GraphVisualizer:
    def to_mermaid(self, graph: ReasoningGraph) -> str:
        lines = ["graph TD"]
        for node in graph.nodes:
            lines.append(f'    {node.id}["{node.operator}"]')
        for edge in graph.edges:
            lines.append(f"    {edge.source} --> {edge.target}")
        return "\n".join(lines)
