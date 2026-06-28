# Reasoning Provenance Specification (RPS)

## Purpose
The RPS is the formal "knowledge flow log" for C³. It represents the complete state transitions, latencies, and output confidences of a given Reasoning Graph execution. Where the RIR describes *what* should happen, the RPS records *how knowledge evolved*.

## Schema

```yaml
version: "1.0"
graph_id: "c3_comp_94b2a"
execution:
  start_time: "2026-06-28T20:53:05Z"
  end_time: "2026-06-28T20:53:15Z"
  total_latency_ms: 10000
  success: true
  
registers_final_state:
  reg_search_results: "Wembley capacity is 90,000..."
  reg_final_answer: "90000"

provenance_events:
  - node_id: "node_1"
    opcode: "KNOW.RETRIEVE"
    start_time: "2026-06-28T20:53:05Z"
    end_time: "2026-06-28T20:53:06.5Z"
    latency_ms: 1500
    registers_read: {}
    registers_written:
      reg_search_results: "Wembley capacity is 90,000..."
    confidence: 0.95
    error: null

  - node_id: "node_2"
    opcode: "VERI.VERIFY"
    start_time: "2026-06-28T20:53:06.5Z"
    end_time: "2026-06-28T20:53:07Z"
    latency_ms: 500
    registers_read:
      reg_search_results: "Wembley capacity is 90,000..."
    registers_written: {}
    confidence: 0.90
    error: null
```

## Tooling & Observability
- This log acts as the source of truth for the Visualizer, generating Gantt charts of node execution overlapping with latency windows.
- In Milestone 3+, Optimizers will consume historical ETS logs to determine which nodes frequently fail or have high latency, guiding future RIR generation.
