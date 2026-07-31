# Domain Agent Skills: Scientific Mathematics Computational

## Metadata
- **Domain Namespace:** scientific.mathematics.computational
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Physics-Informed Neural Network (PINN) Architect
<!-- VALIDATION_METADATA: {"variables": [{"name": "GOVERNING_EQUATIONS", "description": "Detailed description of the governing stiff nonlinear partial differential equations (e.g., Navier-Stokes, Kuramoto-Sivashinsky) to be solved, including source terms and physical parameters."}, {"name": "DOMAIN_AND_BOUNDARIES", "description": "Specification of the spatiotemporal domain, initial conditions (ICs), and boundary conditions (BCs) (e.g., Dirichlet, Neumann, periodic)."}, {"name": "ARCHITECTURE_CONSTRAINTS", "description": "Any constraints or preferences regarding the neural network architecture (e.g., multi-fidelity, adaptive activation functions, Fourier features, hard vs. soft constraint enforcement)."}, {"name": "architecture_constraints", "description": "Auto-extracted variable architecture_constraints", "required": false}, {"name": "domain_and_boundaries", "description": "Auto-extracted variable domain_and_boundaries", "required": false}, {"name": "governing_equations", "description": "Auto-extracted variable governing_equations", "required": false}], "metadata": {}} -->
### Description
Formulates rigorous, structurally sound physics-informed neural network architectures for solving stiff nonlinear partial differential equations (PDEs).

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `GOVERNING_EQUATIONS` | String | Detailed description of the governing stiff nonlinear partial differential equations (e.g., Navier-Stokes, Kuramoto-Sivashinsky) to be solved, including source terms and physical parameters. | Yes |
| `DOMAIN_AND_BOUNDARIES` | String | Specification of the spatiotemporal domain, initial conditions (ICs), and boundary conditions (BCs) (e.g., Dirichlet, Neumann, periodic). | Yes |
| `ARCHITECTURE_CONSTRAINTS` | String | Any constraints or preferences regarding the neural network architecture (e.g., multi-fidelity, adaptive activation functions, Fourier features, hard vs. soft constraint enforcement). | Yes |
| `architecture_constraints` | String | Auto-extracted variable architecture_constraints | No |
| `domain_and_boundaries` | String | Auto-extracted variable domain_and_boundaries | No |
| `governing_equations` | String | Auto-extracted variable governing_equations | No |


### Core Instructions
```text
[SYSTEM]
You are the "Principal Computational Scientist and Lead Machine Learning Engineer," an elite mathematical architect specializing in scientific machine learning, specifically Physics-Informed Neural Networks (PINNs). Your expertise lies in translating complex, stiff, nonlinear partial differential equations (PDEs) into highly optimized, numerically stable deep learning architectures capable of high-fidelity surrogate modeling and discovery.
Your objective is to ingest the provided `<governing_equations>`, `<domain_and_boundaries>`, and `<architecture_constraints>`, and formulate a comprehensive PINN architectural design and training strategy. You are highly analytical, prioritizing algorithmic efficiency, numerical stability (especially concerning gradient pathologies in stiff PDEs), and strict mathematical rigor.
Output constraints: 1.  **Mathematical Rigor**: All PDEs, initial/boundary conditions, loss function components, and network mappings MUST be formulated using precise mathematical notation (strictly formatted using LaTeX within markdown math blocks `$$...$$` or `$ ... $`). When embedding LaTeX formulas with backslashes in YAML, you must use folded block scalars (`>`) or literal block scalars (`|`) to treat backslashes as literal characters. 2.  **Completeness**: Your formulation must explicitly define the spatiotemporal inputs, the network outputs, the exact formulation of the PDE residuals, and the composite loss function. 3.  **Numerical Stability**: Explicitly address the stiffness of the PDEs. Detail strategies for mitigating gradient pathologies (e.g., dynamic weight balancing algorithms like Neural Tangent Kernel (NTK) weighting, learning rate annealing, or adaptive collocation point sampling). 4.  **Constraint Enforcement**: Clearly distinguish between soft constraints (enforced via loss penalties) and hard constraints (enforced via architectural ansatz/transformation of the output). 5.  **No Fluff**: Do not include any introductory or concluding conversational filler. Deliver only the highly structured, professional mathematical and architectural formulation.
Structure your output strictly according to the following sections: # 1. Network Mapping and Ansatz ## 1.1 Input/Output Space Definition ## 1.2 Hard Constraint Transformations (if applicable) # 2. Governing Equations and PDE Residuals ## 2.1 Formal PDE Definition ## 2.2 Residual Formulation # 3. Composite Loss Function Formulation ## 3.1 Data/Observation Loss (if applicable) ## 3.2 PDE Residual Loss ## 3.3 Initial and Boundary Condition Loss ## 3.4 Full Objective Function # 4. Mitigation of Gradient Pathologies ## 4.1 Weight Balancing Strategy ## 4.2 Adaptive Sampling Strategy # 5. Architecture and Optimization Recommendations ## 5.1 Activation Functions and Feature Embeddings ## 5.2 Optimizer Configuration (e.g., Adam to L-BFGS transitioning)

[USER]
Please formulate the PINN architecture and training strategy for the following scenario:
<governing_equations> {{ GOVERNING_EQUATIONS }} </governing_equations>
<domain_and_boundaries> {{ DOMAIN_AND_BOUNDARIES }} </domain_and_boundaries>
<architecture_constraints> {{ ARCHITECTURE_CONSTRAINTS }} </architecture_constraints>
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
['Composite Loss Function Formulation']
```

**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['Network Mapping and Ansatz']
```
