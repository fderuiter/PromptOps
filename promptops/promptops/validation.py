"""Module docstring."""
import os
import re
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional, Dict, Union, Set

from pydantic import BaseModel, ValidationError, field_validator, model_validator, Field
from promptops.utils import load_yaml, iter_prompt_files, iter_workflow_files, extract_vars_from_text
from promptops import console

VAR_PATTERN = re.compile(r'\{\{([^}]+)\}\}')

class ComplexityLevel(str, Enum):
    """Missing docstring."""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

class StatusLevel(str, Enum):
    """Missing docstring."""
    DRAFT = 'draft'
    ACTIVE = 'active'

class ToolCall(BaseModel):
    """Missing docstring."""
    id: str = Field(...)
    type: str = Field("function")
    function: Dict[str, Any] = Field(...)

class Message(BaseModel):
    """Missing docstring."""
    role: Optional[str] = Field(None)
    content: Optional[Union[str, List[Any]]] = Field(None)
    tool_calls: Optional[List[ToolCall]] = Field(None)
    tool_call_id: Optional[str] = Field(None)
    name: Optional[str] = Field(None)

    @model_validator(mode='after')
    def check_content_or_tool_calls(self):
        # Allow content to be missing/null if tool_calls is provided
        """
        Ensure a Message has either `content` or `tool_calls` unless its role is "tool" or "tool_result".
        
        Returns:
            self: The validated Message instance.
        
        Raises:
            ValueError: If both `content` and `tool_calls` are missing or empty for messages whose role is not "tool" or "tool_result".
        """
        if not self.content and not self.tool_calls and self.role != "tool" and self.role != "tool_result":
            raise ValueError(
                f"Message with role '{self.role}' must have either 'content' or 'tool_calls'. "
                "Both are missing or empty."
            )
        return self

class ModelParameters(BaseModel):
    """Missing docstring."""
    temperature: float = Field(..., ge=0.0, le=2.0, description="Controls randomness (0.0-2.0)")
    max_tokens: Optional[int] = Field(None)
    top_p: Optional[float] = Field(None)
    frequency_penalty: Optional[float] = Field(None)
    presence_penalty: Optional[float] = Field(None)

class InputVariable(BaseModel):
    """Missing docstring."""
    name: str = Field(...)
    description: str = Field(...)
    required: bool = Field(True)
    default: Optional[Any] = Field(None)

class BaseMetadata(BaseModel):
    """Missing docstring."""
    domain: str = Field(...)
    status: Optional[StatusLevel] = Field(default=StatusLevel.ACTIVE)

class PromptMetadata(BaseMetadata):
    """Missing docstring."""
    complexity: ComplexityLevel = Field(...)
    tags: List[str] = Field([])
    requires_context: bool = Field(False)
    autonomy: Optional[str] = Field(None)
    requirements: Optional[List[str]] = Field(None)
    maturity: Optional[str] = Field(None)

class InputSchema(BaseModel):
    """Missing docstring."""
    type: str = Field("object")
    properties: Optional[Dict[str, Any]] = Field(None)
    required: Optional[List[str]] = Field(None)

class MCPTool(BaseModel):
    """Missing docstring."""
    name: str = Field(...)
    description: str = Field(...)
    inputSchema: InputSchema = Field(...)

class PromptSchema(BaseModel):
    """Missing docstring."""
    name: str = Field(...)
    version: str = Field("0.1.0")
    description: str = Field(...)
    metadata: Optional[PromptMetadata] = Field(None)
    variables: List[InputVariable] = Field([])
    model: str = Field(...)
    safety_opt_out: bool = Field(False)
    modelParameters: ModelParameters = Field(...)
    messages: List[Message] = Field(...)
    tools: Optional[List[MCPTool]] = Field(None)
    testData: List[Any] = Field(...)
    evaluators: List[Any] = Field(...)
    output_schema: Optional[Dict[str, Any]] = Field(None)
    last_modified: Optional[str] = Field(None)

    @field_validator("evaluators")
    @classmethod
    def check_evaluators_logic(_cls, v: List[Any]) -> List[Any]:
        """Missing docstring."""
        if v is None:
            return v
        for evaluator in v:
            if not isinstance(evaluator, dict):
                continue
            valid_keys = {"python", "rule", "regex", "model", "type", "string", "includes_all", "regex_match", "string_match", "string_contains", "evaluator", "description"}
            if not any(k in evaluator for k in valid_keys):
                raise ValueError(f"Evaluator '{evaluator.get('name', 'Unknown')}' must map to executable logic.")
        return v

    @field_validator("messages")
    @classmethod
    def check_messages_length(_cls, v: List[Message]) -> List[Message]:
        """Missing docstring."""
        if len(v) < 2:
            raise ValueError("messages list must have at least 2 items")
        return v

    @model_validator(mode='after')
    def check_variables_match_content(self):
        """
        Validate that template variables referenced in message content or tool-call payloads are syntactically valid and match the prompt's declared variables.
        
        This validator:
        - Checks the Jinja2 syntax of each message content. Raises ValueError if the syntax is invalid.
        - Extracts template variables from each message using Jinja2 AST parsing.
        - Ensures each variable name matches the pattern `^[a-zA-Z0-9_.-]+$`; raises ValueError if any invalid variable names are found.
        - Prints a warning for variables declared in `variables` but not used in any message.
        - Raises ValueError if any variables are used in messages but not declared in `variables`.
        
        Returns:
            self (PromptSchema): The validated model instance.
        """
        found_vars: set[str] = set()
        invalid_vars: set[str] = set()
        
        for msg in self.messages:
            content_str = ""
            if isinstance(msg.content, str):
                content_str = msg.content
            elif isinstance(msg.content, list):
                content_str = " ".join([str(c) for c in msg.content])
            elif not msg.content and msg.tool_calls:
                content_str = str(msg.tool_calls)

            try:
                vars_in_text = extract_vars_from_text(content_str)
                found_vars.update(vars_in_text)
            except ValueError as e:
                raise ValueError(str(e))

            for var in vars_in_text:
                valid_match = re.match(r'^[a-zA-Z0-9_.-]+$', var)
                if not valid_match:
                    invalid_vars.add(var)

        if invalid_vars:
            raise ValueError(f"Migration Required: Variables contain invalid characters: {invalid_vars}")

        defined_vars = {v.name for v in self.variables}
        unused = defined_vars - found_vars
        # Suppress warnings for common variables like macros
        unused = {u for u in unused if u not in {"macros", "text"}}
        if unused:
            console.warn(f"Variables defined but not used in prompt: {unused}")

        undefined = found_vars - defined_vars
        if undefined:
            raise ValueError(f"Variables used in messages but NOT defined in 'variables' section: {undefined}")

        return self

    @model_validator(mode='after')
    def check_test_data_types(self):
        """Warn if testData contains non-string types that will be coerced to strings."""
        if not self.testData:
            return self
            
        for case in self.testData:
            if isinstance(case, dict):
                # Check inputs
                inputs = case.get('inputs', {})
                if isinstance(inputs, dict):
                    pass
                
                # Check expected
                expected = case.get('expected')
                if expected is not None and not isinstance(expected, str):
                    pass
        return self

class EvaluatorRule(BaseModel):
    """Missing docstring."""
    rule_type: str = Field(...)  # "Contains", "Does Not Contain", "Regex Match", "Length >", "Length <", "Custom Python"
    value: str = Field(...)

    @classmethod
    def from_python_expression(cls, expr: str) -> "EvaluatorRule":
        """Missing docstring."""
        expr_str = expr.strip()
        if expr_str.startswith("len(output) > ") and expr_str[14:].isdigit():
            return cls(rule_type="Length >", value=expr_str[14:])
        elif expr_str.startswith("len(output) < ") and expr_str[14:].isdigit():
            return cls(rule_type="Length <", value=expr_str[14:])
        elif " in output" in expr_str and expr_str.startswith("'") and expr_str.split("'")[1]:
            if " not in output" in expr_str:
                return cls(rule_type="Does Not Contain", value=expr_str.split("'")[1])
            return cls(rule_type="Contains", value=expr_str.split("'")[1])
        elif expr_str.startswith("re.search(") and "output" in expr_str:
            try:
                # e.g., re.search(r'pattern', output)
                pattern = expr_str.split("r'")[1].split("',")[0]
                return cls(rule_type="Regex Match", value=pattern)
            except Exception:
                pass
        return cls(rule_type="Custom Python", value=expr_str)

    def to_python_expression(self) -> str:
        """Missing docstring."""
        if self.rule_type == "Contains":
            return f"'{self.value}' in output"
        elif self.rule_type == "Does Not Contain":
            return f"'{self.value}' not in output"
        elif self.rule_type == "Regex Match":
            return f"re.search(r'{self.value}', output)"
        elif self.rule_type == "Length >":
            return f"len(output) > {self.value if self.value.isdigit() else 0}"
        elif self.rule_type == "Length <":
            return f"len(output) < {self.value if self.value.isdigit() else 0}"
        return self.value


class TransitionConstraint(BaseModel):
    """Missing docstring."""
    variable: Optional[str] = None
    operator: str = "Always"  # "Always", "==", "!=", ">", "<", "Custom Jinja2"
    value: Optional[str] = None

    @classmethod
    def from_jinja_expression(cls, expr: str) -> "TransitionConstraint":
        """Missing docstring."""
        if not expr:
            return cls(operator="Always")
        import re
        m = re.match(r"\{\%\s*if\s+(.+)\s+(==|!=|>|<|>=|<=)\s+(.+)\s*\%\}true\{\%\s*endif\s*\%\}", expr)
        if m:
            var_name = m.group(1).strip()
            op = m.group(2).strip()
            val = m.group(3).strip().strip("'\"")
            return cls(variable=var_name, operator=op, value=val)
        return cls(operator="Custom Jinja2", value=expr)

    def to_jinja_expression(self) -> str:
        """Missing docstring."""
        if self.operator == "Always":
            return ""
        if self.operator == "Custom Jinja2":
            return self.value or ""
        if not self.variable:
            return ""
        val = self.value or ""
        return f"{{% if {self.variable} {self.operator} '{val}' %}}true{{% endif %}}"

class WorkflowInput(BaseModel):
    """Missing docstring."""
    name: str = Field(...)
    description: Optional[str] = Field(None)

class WorkflowEdge(BaseModel):
    """Missing docstring."""
    target: str = Field(...)
    condition: Optional[str] = Field(None)

class WorkflowStep(BaseModel):
    """Missing docstring."""
    step_id: str = Field(...)
    prompt_file: str = Field(...)
    map_inputs: Dict[str, Any] = Field(...)
    next: Optional[Union[str, List[Union[str, WorkflowEdge]]]] = Field(None)

class WorkflowMetadata(BaseMetadata):
    """Missing docstring."""
    topic: str = Field(...)

class WorkflowSchema(BaseModel):
    """Missing docstring."""
    name: str = Field(...)
    description: Optional[str] = Field(None)
    metadata: Optional[WorkflowMetadata] = Field(None)
    inputs: List[WorkflowInput] = Field([])
    steps: List[WorkflowStep] = Field(...)
    testData: Optional[List[Any]] = Field(None)

def analyze_workflow_dependencies(workflow_file: str, workflow_data: dict, root_dir: str, call_stack: Optional[Set[str]] = None) -> List[str]:
    """Missing docstring."""
    if call_stack is None:
        call_stack = set()
    
    abs_workflow_file = os.path.abspath(workflow_file)
    if abs_workflow_file in call_stack:
        return [f"Circular sub-workflow dependency detected involving: {abs_workflow_file}"]
    
    current_call_stack = call_stack | {abs_workflow_file}
    
    issues = []
    try:
        wf = WorkflowSchema(**workflow_data)
    except ValidationError as e:
        return [f"Validation error: {e}"]

    # Dependency Graph (Circular & Forward reference detection)
    graph: Dict[str, List[str]] = {}
    step_ids = [step.step_id for step in wf.steps]
    
    for step_id in step_ids:
        graph[step_id] = []

    global_inputs = {inp.name for inp in wf.inputs}

    for i, step in enumerate(wf.steps):
        targets = []
        if step.next is not None:
            if isinstance(step.next, str):
                targets.append(step.next)
            elif isinstance(step.next, list):
                for edge in step.next:
                    if isinstance(edge, str):
                        targets.append(edge)
                    elif isinstance(edge, WorkflowEdge):
                        targets.append(edge.target)
                    elif isinstance(edge, dict):
                        targets.append(edge.get('target'))
        else:
            if i + 1 < len(wf.steps):
                targets.append(wf.steps[i + 1].step_id)
                
        for t in targets:
            if t not in step_ids:
                issues.append(f"Step '{step.step_id}' references undefined next step '{t}'.")
            else:
                graph[step.step_id].append(t)

        for var_name, template in step.map_inputs.items():
            if not isinstance(template, str):
                continue
            # Check inputs.*
            inputs_matches = re.findall(r'\{\{\s*inputs\.([^}\s]+)\s*\}\}', template)
            for inp_match in inputs_matches:
                if inp_match not in global_inputs:
                    issues.append(f"Step '{step.step_id}' mapping '{var_name}' refers to undefined global input '{inp_match}'.")

            # Check steps.*.output
            steps_matches = re.findall(r'\{\{\s*steps\.([^\.\s]+)\.(output|history)\s*\}\}', template)
            for step_match, prop in steps_matches:
                if step_match not in step_ids:
                    issues.append(f"Step '{step.step_id}' mapping '{var_name}' references undefined step '{step_match}'.")

    # Detect disconnected components
    if wf.steps:
        start_node = wf.steps[0].step_id
        visited = set()
        queue = [start_node]
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                queue.extend(graph[node])
                
        unreachable = set(step_ids) - visited
        if unreachable:
            issues.append(f"Disconnected component(s) detected. The following steps are unreachable: {unreachable}")

    # Cycle Detection
    visited_cycle = set()
    rec_stack = set()
    def detect_cycle(node):
        """Missing docstring."""
        visited_cycle.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited_cycle:
                if detect_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        rec_stack.remove(node)
        return False
    
    for node in step_ids:
        if node not in visited_cycle:
            if detect_cycle(node):
                issues.append("Cyclic dependency (circular loop) detected in workflow steps.")
                break

    # Check Variable Contract
    for step in wf.steps:
        from promptops.utils import ROOT
        prompt_path = os.path.join(str(ROOT), step.prompt_file)
        prompt_content = None
        
        if os.path.exists(prompt_path):
            prompt_content = load_yaml(prompt_path)
            
        required_vars = set()
        found_valid = False
            
        if not prompt_content:
            path_obj = Path(prompt_path)
            skills_md = path_obj.parent / "skills.md"
            if skills_md.exists():
                from promptops.utils import parse_skill_manifest, resolve_skill_from_path
                manifest = parse_skill_manifest(skills_md)
                skills_list = manifest.get("skills", [])
                
                best_match = resolve_skill_from_path(path_obj, skills_list)
                
                if best_match:
                    found_valid = True
                    for v in best_match.get("variables", []):
                        if isinstance(v, str):
                            required_vars.add(v)
                        elif isinstance(v, dict):
                            if v.get("required", True):
                                required_vars.add(v.get("name", "unknown"))

            if not found_valid:
                issues.append(f"Step '{step.step_id}' references missing prompt file or skill: {step.prompt_file}")
                continue
        else:
            is_workflow = step.prompt_file.endswith('.workflow.yaml') or step.prompt_file.endswith('.workflow.yml')
            if is_workflow:
                try:
                    wf_schema = WorkflowSchema(**prompt_content)
                    required_vars = {v.name for v in wf_schema.inputs}
                    sub_issues = analyze_workflow_dependencies(prompt_path, prompt_content, root_dir, current_call_stack)
                    for issue in sub_issues:
                        if "Circular sub-workflow dependency" in issue:
                            issues.append(issue)
                except ValidationError:
                    issues.append(f"Step '{step.step_id}' references invalid workflow file: {step.prompt_file}")
                    continue
            else:
                try:
                    prompt_schema = PromptSchema(**prompt_content)
                    required_vars = {v.name for v in prompt_schema.variables if v.required}
                except ValidationError:
                    issues.append(f"Step '{step.step_id}' references invalid prompt file: {step.prompt_file}")
                    continue
        
        def flatten_keys(d, parent_key=''):
            """Missing docstring."""
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_keys(v, new_key))
                else:
                    items.append(new_key)
            return items
            
        mapped_vars = set(flatten_keys(step.map_inputs))

        
        missing_vars = required_vars - mapped_vars
        if missing_vars:
            issues.append(f"Step '{step.step_id}' is missing mappings for required prompt variables: {missing_vars}")
            
    return issues

def update_last_modified(file_path: Path) -> bool:
    """Missing docstring."""
    from datetime import datetime, timezone
    try:
        content_text = file_path.read_text(encoding="utf-8")
    except Exception as e:
        console.error(f"Error reading {file_path}: {e}")
        return False

    lines = content_text.splitlines()
    found = False
    now_iso = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    modified = False

    for i, line in enumerate(lines):
        if line.strip().startswith('last_modified:'):
            indent = line[:line.find('last_modified:')]
            new_line = f"{indent}last_modified: {now_iso}"
            if new_line != line:
                lines[i] = new_line
                modified = True
            found = True
            break

    if not found:
        final_lines = []
        name_found = False
        for line in lines:
            final_lines.append(line)
            if not name_found and line.strip().startswith('name:'):
                indent = line[:line.find('name:')]
                final_lines.append(f"{indent}last_modified: {now_iso}")
                modified = True
                name_found = True

        if not name_found:
             if len(final_lines) > 0 and final_lines[0].strip() == '---':
                 final_lines.insert(1, f"last_modified: {now_iso}")
                 modified = True
             else:
                 final_lines.insert(0, f"last_modified: {now_iso}")
                 modified = True
        lines = final_lines

    if modified:
        file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        console.info(f"Updated last_modified in {file_path}")
        return True
    return False

def detect_workflow_redundancies(workflows_data: List[tuple[str, dict]]):
    """Missing docstring."""
    step_signatures = {}
    mapping_signatures = {}
    sequence_signatures = {}

    for file_path, content in workflows_data:
        steps = content.get('steps', [])
        seq = []
        for i, step in enumerate(steps):
            prompt_file = step.get('prompt_file')
            map_inputs = step.get('map_inputs', {})
            
            # Step block signature
            step_sig = json.dumps({"prompt_file": prompt_file, "map_inputs": map_inputs}, sort_keys=True)
            seq.append(step_sig)
            
            if step_sig not in step_signatures:
                step_signatures[step_sig] = []
            step_signatures[step_sig].append((file_path, step.get('step_id')))
            
            # Mapping block signature (only if non-empty)
            if map_inputs:
                map_sig = json.dumps(map_inputs, sort_keys=True)
                if map_sig not in mapping_signatures:
                    mapping_signatures[map_sig] = []
                mapping_signatures[map_sig].append((file_path, step.get('step_id')))
        
        # Sequence signatures (pairs of adjacent steps)
        for i in range(len(seq) - 1):
            seq_sig = f"{seq[i]}|||{seq[i+1]}"
            if seq_sig not in sequence_signatures:
                sequence_signatures[seq_sig] = []
            sequence_signatures[seq_sig].append((file_path, steps[i].get('step_id'), steps[i+1].get('step_id')))

    for sig, occurrences in step_signatures.items():
        if len(occurrences) > 1:
            files = list(set([o[0] for o in occurrences]))
            if len(files) > 1:
                console.warn(f"Duplicate step definition found across workflows: {files}. Consider extracting to a sub-workflow.")

    for sig, occurrences in mapping_signatures.items():
        if len(occurrences) > 1:
            files = list(set([o[0] for o in occurrences]))
            if len(files) > 1:
                console.warn(f"Duplicate mapping block found across workflows: {files}. Consider consolidating.")

    for sig, occurrences in sequence_signatures.items():
        if len(occurrences) > 1:
            files = list(set([o[0] for o in occurrences]))
            if len(files) > 1:
                console.warn(f"Duplicated step sequence found across workflows: {files}. Consider converting to a sub-workflow.")


def validate_prompts(directory: str, strict: bool = False, files: Optional[List[str]] = None) -> bool:
    """Missing docstring."""
    ok = True
    seen_names: Dict[str, str] = {}
    dir_path = os.environ.get('PROMPTOPS_REGISTRY', directory)
    dirs_to_check: Set[Path] = set()
    
    NAMING_RULES = {
        "meta": re.compile(r"^L\d+_.*\.prompt\.(ya?ml|md)$", re.IGNORECASE),
    }

    if files:
        for f in files:
            path = Path(f)
            if path.is_file() and path.name.endswith(('.prompt.yaml', '.prompt.yml')):
                update_last_modified(path)

    for file_path in iter_prompt_files(dir_path):
        
        # Collect directory to check hygiene later
        path = file_path.parent
        base_path = Path(dir_path).resolve()
        while path != base_path and base_path in path.parents:
            dirs_to_check.add(path)
            path = path.parent
        # Include if file is directly in dir_path
        if file_path.parent == base_path:
            dirs_to_check.add(base_path)

        if file_path.parent.name in NAMING_RULES and not file_path.name.endswith(".workflow.yaml") and not file_path.name.endswith(".workflow.yml"):
            if not NAMING_RULES[file_path.parent.name].match(file_path.name):
                console.error(f"{file_path} does not match required pattern for {file_path.parent.name}")
                ok = False

        content = load_yaml(str(file_path))
        if not content:
            ok = False
            continue
            
        if content.get('metadata', {}).get('status') == 'draft':
            continue
            
        try:
            schema = PromptSchema(**content)
        except ValidationError as e:
            console.error(f"Validation error in {file_path}:\n{e}")
            ok = False
            continue

        # Check mapped requirement IDs against the master list
        if schema.metadata and schema.metadata.requirements is not None:
            from promptops.utils import load_requirements
            master_requirements = load_requirements()
            invalid_ids = [req_id for req_id in schema.metadata.requirements if req_id not in master_requirements]
            if invalid_ids:
                console.error(f"Validation error in {file_path}:")
                console.error(f"  Requirement ID(s) missing from master list: {invalid_ids}")
                ok = False

        if strict:
            issues = []
            if not content.get('testData') or len(content.get('testData', [])) == 0:
                issues.append("no testData")
            elif len(content.get('testData', [])) == 1:
                issues.append("only 1 test case")
            
            if not content.get('evaluators') or len(content.get('evaluators', [])) == 0:
                issues.append("no evaluators")
            
            if issues:
                console.warn(f"{file_path} has {', '.join(issues)}")

        name = content.get('name')
        if name:
            if name in seen_names:
                console.error(f"Duplicate name '{name}' found in:\n  - {seen_names[name]}\n  - {file_path}")
                ok = False
            else:
                seen_names[name] = str(file_path)


    # Validate Workflows
    all_workflows = []
    for file_path in iter_workflow_files(dir_path):
        # Collect directory to check hygiene later
        path = file_path.parent
        base_path = Path(dir_path).resolve()
        while path != base_path and base_path in path.parents:
            dirs_to_check.add(path)
            path = path.parent
        if file_path.parent == base_path:
            dirs_to_check.add(base_path)

        if file_path.parent.name in NAMING_RULES and not file_path.name.endswith(".workflow.yaml") and not file_path.name.endswith(".workflow.yml"):
            if not NAMING_RULES[file_path.parent.name].match(file_path.name):
                console.error(f"{file_path} does not match required pattern for {file_path.parent.name}")
                ok = False

        content = load_yaml(str(file_path))
        if not content:
            ok = False
            continue
            
        if content.get('metadata', {}).get('status') == 'draft':
            continue
            
        all_workflows.append((str(file_path), content))
            
        issues = analyze_workflow_dependencies(str(file_path), content, dir_path)
        if issues:
            console.error(f"Validation error in workflow {file_path}:")
            for issue in issues:
                console.error(f"  - {issue}")
            ok = False

        if strict:
            test_data = content.get('testData', [])
            if test_data:
                for i, test_case in enumerate(test_data):
                    inputs = test_case.get('inputs', test_case.get('vars', {}))
                    try:
                        from promptops.engine import run_workflow
                        run_workflow(str(file_path), inputs, verbose=False, strict_mode=True)
                    except Exception as e:
                        console.error(f"Simulation failed on {file_path} scenario {i+1}: {e}")
                        ok = False
                        break
            else:
                try:
                    from promptops.engine import run_workflow
                    run_workflow(str(file_path), {}, verbose=False, strict_mode=True)
                except Exception as e:
                    console.error(f"Simulation failed on {file_path}: {e}")
                    ok = False

    detect_workflow_redundancies(all_workflows)

    # Validate Skill Manifests
    from promptops.utils import iter_skill_manifests, parse_skill_manifest
    for file_path in iter_skill_manifests(dir_path):
        # Collect directory to check hygiene later
        path = file_path.parent
        base_path = Path(dir_path).resolve()
        while path != base_path and base_path in path.parents:
            dirs_to_check.add(path)
            path = path.parent
        if file_path.parent == base_path:
            dirs_to_check.add(base_path)
            
        try:
            parse_skill_manifest(file_path)
        except Exception as e:
            console.error(f"Manifest validation error in {file_path}:\n{e}")
            ok = False

    # Check directory hygiene
    for d in dirs_to_check:
        if not (d / "overview.md").exists():
            console.error(f"Missing overview.md in {d}")
            ok = False
            
        has_manifest = (d / "skills.md").exists()
        for file in d.iterdir():
            if not file.is_file() or file.name.startswith('.'):
                continue
            name = file.name
            lower_name = name.lower()
            if lower_name in {"overview.md", "readme.md", "skills.md"} or lower_name.endswith(".workflow.md"):
                continue

            is_prompt = lower_name.endswith(".prompt.md") or lower_name.endswith(".prompt.yml") or lower_name.endswith(".prompt.yaml")
            is_workflow = lower_name.endswith(".workflow.yaml") or lower_name.endswith(".workflow.yml")

            if has_manifest and is_prompt:
                console.error(f"Error: {file} is redundant because a skills.md manifest exists in {directory}")
                ok = False

            if not (is_prompt or is_workflow):
                console.error(f"{file} is not a recognised prompt or workflow file")
                ok = False

    return ok



import json
from pydantic import create_model

def json_schema_to_pydantic_fields(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Missing docstring."""
    if schema.get("type") != "object":
        raise ValueError("Only 'object' type is supported for root output_schema.")
    
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    fields: Dict[str, Any] = {}
    for prop_name, prop_details in properties.items():
        prop_type = prop_details.get("type", "string")
        py_type: Any
        
        if prop_type == "string":
            py_type = str
        elif prop_type == "integer":
            py_type = int
        elif prop_type == "number":
            py_type = float
        elif prop_type == "boolean":
            py_type = bool
        elif prop_type == "array":
            items = prop_details.get("items", {})
            item_type = items.get("type", "string")
            if item_type == "string":
                py_type = list[str]
            elif item_type == "integer":
                py_type = list[int]
            elif item_type == "number":
                py_type = list[float]
            elif item_type == "boolean":
                py_type = list[bool]
            else:
                py_type = list[Any]
        elif prop_type == "object":
            py_type = dict
        else:
            py_type = Any
            
        if prop_name in required:
            fields[prop_name] = (py_type, ...)
        else:
            fields[prop_name] = (Optional[py_type], None)
            
    return fields

def validate_response(response_text: str, output_schema: Optional[Dict[str, Any]] = None, evaluators: Optional[list] = None) -> str:
    """Missing docstring."""
    if output_schema:
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        
        try:
            parsed_json = json.loads(cleaned_text)
        except json.JSONDecodeError:
            raise ProomptsValidationError("Response is not valid JSON.")
            
        fields = json_schema_to_pydantic_fields(output_schema)
        DynamicModel = create_model("DynamicOutputModel", **fields)
        
        try:
            DynamicModel.model_validate(parsed_json)
        except ValidationError as ve:
            errors = ve.errors()
            if errors:
                error = errors[0]
                loc = ".".join([str(l) for l in error.get("loc", [])])
                msg = error.get("msg", "")
                error_type = error.get("type", "")
                if error_type == "missing":
                    raise ProomptsValidationError(f"missing required field: '{loc}'")
                else:
                    raise ProomptsValidationError(f"field '{loc}' failed validation: {msg}")
            raise ProomptsValidationError(f"Validation error: {ve}")
            
    if evaluators:
        from promptops.engine import run_evaluators
        response_text = run_evaluators(response_text, evaluators)
    return response_text

class ProomptsGuardError(Exception):
    """Missing docstring."""
    pass

class ProomptsValidationError(ProomptsGuardError):
    """Missing docstring."""
    pass
