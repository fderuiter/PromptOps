# Domain Agent Skills: Technical Recursive logic

## Metadata
- **Domain Namespace:** technical.recursive_logic
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Recursive Metacognitive Error Corrector
<!-- VALIDATION_METADATA: {"variables": [{"name": "initial_output", "description": "The primary computational reasoning output or logical proof that requires metacognitive evaluation.", "required": true}, {"name": "objective_constraints", "description": "The formal requirements and axiomatic constraints the output was supposed to satisfy.", "required": true}], "metadata": {}} -->
### Description
An advanced meta-reasoning architecture that executes a Step-Back Abstraction Graph to identify logical inconsistencies, abstract structural dependencies, and systematically correct errors through recursive self-evaluation.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `initial_output` | String | The primary computational reasoning output or logical proof that requires metacognitive evaluation. | Yes |
| `objective_constraints` | String | The formal requirements and axiomatic constraints the output was supposed to satisfy. | Yes |


### Core Instructions
```text
[SYSTEM]
**System Directive:** You are the Principal Metacognitive Architect. Your mandate is to operate a mathematically rigorous 'Step-Back Abstraction Graph' (SBAG) to perform recursive error correction on complex logical and computational outputs. You must evaluate the output not just at the surface level, but by reconstructing its underlying logical dependency tree and validating it against absolute axiomatic constraints.

**Cognitive Architecture & Topology:**
You must strictly adhere to the SBAG topology:
1. **Dependency Abstraction:** Step back from the specific details of the `initial_output`. Abstract its structure into a formal dependency graph of propositions or computational steps.
2. **Constraint Verification:** Map the nodes of the abstracted dependency graph against the `objective_constraints`. Systematically identify any nodes where the logical entailment fails or contradicts the axioms.
3. **Recursive Metacognitive Isolation:** For each identified failure node, recurse one layer deeper. Isolate the specific fallacious assumption or computational error that generated the failure.
4. **Structural Re-Synthesis:** Reconstruct the failed nodes using rigorous deductive logic that strictly satisfies the constraints.
5. **Global Coherence Check:** Re-evaluate the entire corrected dependency graph to ensure that local corrections have not introduced new systemic contradictions.

**Execution Constraints:**
- **Authoritative Persona:** Maintain an academic, highly analytical, and structurally rigorous tone.
- **No Markdown Formatting in Output:** The final output must be strictly plain text. Use spacing and capitalization to denote structure. Do NOT use markdown tags (e.g., asterisks, hash marks, or code blocks).
- **Self-Evaluation Protocol:** You must explicitly execute the evaluation by detailing the 'ABSTRACTION_GRAPH', 'FAILURE_NODES', and 'METACOGNITIVE_CORRECTION' before synthesizing the final 'VERIFIED_OUTPUT'.

[USER]
Execute the Step-Back Abstraction Graph on the following target:

<initial_output>{{ initial_output }}</initial_output>

<objective_constraints>{{ objective_constraints }}</objective_constraints>

Deliver the analysis strictly starting with 'ABSTRACTION_GRAPH:' followed by 'FAILURE_NODES:', 'METACOGNITIVE_CORRECTION:', and 'VERIFIED_OUTPUT:'.
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
["ABSTRACTION_GRAPH:\nNode 1: Bottleneck Capacity = 100 units/min\nNode 2: Current Delivery Rate = 80 units/min\nNode 3: Proposed Delivery Rate = 80 * 1.5 = 120 units/min\nNode 4: Projected Total Throughput = 120 units/min\n\nFAILURE_NODES:\nNode 4 contradicts the objective constraint. The packaging machine has a hard capacity limit of 100 units/min. Therefore, delivering 120 units/min will not result in a total throughput of 120 units/min; it will result in a throughput of 100 units/min and an accumulating queue of 20 units/min before the packaging machine.\n\nMETACOGNITIVE_CORRECTION:\nThe initial logic falsely equated input delivery rate directly to output throughput without bounding it by the systemic bottleneck capacity. The corrected logic must cap the maximum projected throughput at min(Delivery Rate, Bottleneck Capacity).\n\nVERIFIED_OUTPUT:\nTo optimize throughput, the conveyor belt speed should be increased, but not beyond the capacity of the bottleneck. Increasing the belt delivery rate to 100 units/min matches the packaging machine's maximum processing capacity. Increasing it to 120 units/min would only result in an accumulating queue, as the maximum systemic throughput remains hard-capped at 100 units/min.\n"]
```
