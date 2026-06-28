from typing import Any
from rir.graph import ReasoningGraph
import dateutil.parser

class GraphVisualizer:
    def to_mermaid_dag(self, graph: ReasoningGraph) -> str:
        lines = ["graph TD"]
        for node in graph.nodes:
            lines.append(f'    {node.id}["{node.opcode}"]')
        for edge in graph.edges:
            lines.append(f"    {edge.source} --> {edge.target}")
        return "\n".join(lines)

    def to_mermaid_gantt(self, rps_report: dict[str, Any]) -> str:
        """
        Converts a Reasoning Provenance Specification (RPS) log into a Mermaid Gantt Chart.
        """
        lines = [
            "gantt",
            "    title Reasoning Provenance Timeline",
            "    dateFormat  YYYY-MM-DDTHH:mm:ss.SSSZ",
            "    axisFormat  %H:%M:%S",
        ]
        
        events = rps_report.get("provenance_events", [])
        for event in events:
            node_id = event["node_id"]
            opcode = event["opcode"]
            start = event["start_time"]
            end = event["end_time"]
            # Convert to Mermaid compatible timestamp formatting (usually just the ISO string)
            # We omit the 'Z' parsing issues by keeping the raw iso formats.
            
            lines.append(f"    section {node_id}")
            # Format: Task Name : ID, Start, End
            lines.append(f"    {opcode} : {node_id}, {start}, {end}")
            
        return "\n".join(lines)
