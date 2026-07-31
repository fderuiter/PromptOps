"""Module docstring."""
import argparse
import sys
import logging
import os
from promptops.validation import validate_prompts
from promptops.simulation import simulate_prompt
from promptops.documentation import generate_docs
from promptops.init import init_project
from promptops.agent import generate_config, discovery_report
from promptops.utils import load_yaml, ROOT, iter_prompt_files
from promptops.engine import run_workflow
from promptops import console

logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False) -> None:
    """Missing docstring."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
    logger.setLevel(level)

def search_prompts_func(query: str, verbose: bool = False):
    """Missing docstring."""
    from promptops.validation import PromptSchema
    
    query = query.lower()
    found = 0
    for path in iter_prompt_files(ROOT):
        content = load_yaml(path)
        
        try:
            PromptSchema(**content)
        except Exception:
            continue
            
        name = content.get('name', '').lower()
        description = content.get('description', '').lower()

        if query in name or query in description:
            found += 1
            print(f"Match: {content.get('name')} ({path.relative_to(ROOT)})")
            if verbose and content.get('description'):
                 print(f"  Description: {content.get('description')}")
            if verbose:
                print()

    if found == 0:
        print(f"No prompts found matching '{query}'.")

def get_parser():
    """Missing docstring."""
    parser = argparse.ArgumentParser(description="PromptOps Toolkit CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Init
    subparsers.add_parser("init", help="Initialize PromptOps in the current repository")

    # Verify
    subparsers.add_parser("verify", help="Run the central verification script locally")

    # Validate
    validate_parser = subparsers.add_parser("validate", help="Validate prompt files")
    validate_parser.add_argument("--dir", help="Directory containing prompts", default=".")
    validate_parser.add_argument("--strict", action="store_true", help="Enable strict validation")
    validate_parser.add_argument("--skip-semantic", action="store_true", help="Skip semantic validation checks")
    validate_parser.add_argument("files", nargs="*", help="Specific files to validate and format (updates last_modified)")

    # Simulate
    simulate_parser = subparsers.add_parser("simulate", help="Simulate a prompt")
    simulate_parser.add_argument("file", nargs="?", help="Path to prompt file")
    simulate_parser.add_argument("-f", "--file", dest="file_flag", help="Path to prompt file (alias)")
    simulate_parser.add_argument("-i", "--data", dest="data", help="Path to JSON/YAML file with mock data", required=True)
    simulate_parser.add_argument("--strict", action="store_true", help="Enable strict validation")
    simulate_parser.add_argument("--chaos", action="store_true", help="Enable chaos mode")
    simulate_parser.add_argument("-v", "--verbose", action="store_true", help="Increase verbosity")
    simulate_parser.add_argument("--json", action="store_true", help="Enable JSON output mode")
    simulate_parser.add_argument("--no-color", action="store_true", help="Disable colored output")

    # Docs
    docs_parser = subparsers.add_parser("docs", help="Generate prompt documentation")
    docs_parser.add_argument("--dir", help="Directory containing prompts", default=".")
    docs_parser.add_argument("--out", help="Output directory for documentation", default="docs")
    docs_parser.add_argument("--repo-url", help="Base URL for source repository", default="")
    docs_parser.add_argument("--branch", help="Branch name for source repository links", default="main")
    docs_parser.add_argument("--check", action="store_true", help="Check for documentation drift without modifying files")

    # Agent
    agent_parser = subparsers.add_parser("agent", help="Agent configuration and discovery")
    agent_subparsers = agent_parser.add_subparsers(dest="agent_command", required=True)
    
    agent_config = agent_subparsers.add_parser("config", help="Generate MCP configuration for agent clients")
    agent_config.add_argument("--dir", help="Directory containing prompts", default="prompts")
    
    agent_discovery = agent_subparsers.add_parser("discovery", help="Show tool discovery and override report")
    agent_discovery.add_argument("--dir", help="Directory containing prompts", default="prompts")

    # Vibe
    vibe_parser = subparsers.add_parser("vibe", help="Run full-fidelity vibe audit")
    vibe_parser.add_argument("--budget-cap", type=float, default=10.0, help="Maximum budget for LLM API calls")
    vibe_parser.add_argument("--coverage", type=str, default="universal", help="Coverage mode")

    # Workflow
    workflow_parser = subparsers.add_parser("workflow", help="Simulate a workflow execution")
    workflow_parser.add_argument("workflow_file", help="Path to the .workflow.yaml file.")
    workflow_parser.add_argument("-i", "--input", action='append', help="Set a workflow input, e.g., -i name='value'")
    workflow_parser.add_argument("-f", "--inputs-file", help="Path to a JSON or YAML file containing workflow inputs")
    workflow_parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    workflow_parser.add_argument("--strict", action="store_true", help="Run in strict mode")
    workflow_parser.add_argument("--chaos", action="store_true", help="Enable Chaos Mode")
    workflow_parser.add_argument("--no-color", action="store_true", help="Disable color output")
    workflow_parser.add_argument("--json", action="store_true", help="Output Fidelity Report as JSON only")

    # Search
    search_parser = subparsers.add_parser("search", help="Search prompts by keyword")
    search_parser.add_argument("query", help="Keyword to search for")
    search_parser.add_argument("-v", "--verbose", action="store_true", help="Show description")
    
    # Export Schemas
    export_parser = subparsers.add_parser("export-schemas", help="Export JSON schemas for core validation models")
    export_parser.add_argument("--out-dir", help="Output directory for JSON schemas", default="docs/schemas")
    
    # Doc-gen (internal/hidden or explicit)
    docgen_parser = subparsers.add_parser("generate-cli-docs", help="Generate CLI documentation markdown")
    docgen_parser.add_argument("--output", help="Output markdown file", default="docs/CLI.md")

    return parser

def main():
    """Missing docstring."""
    parser = get_parser()
    args = parser.parse_args()

    if args.command == "init":
        init_project()
    elif args.command == "verify":
        import subprocess
        
        env = os.environ.copy()
        env["SKIP_SETUP"] = "1"
        script_path = ROOT / "scripts" / "validate_prompts.sh"
        
        try:
            result = subprocess.run([str(script_path)], cwd=ROOT, env=env)
            sys.exit(result.returncode)
        except Exception as e:
            logger.error(f"Failed to execute verification script: {e}")
            sys.exit(1)
    elif args.command == "validate":
        success = validate_prompts(args.dir, strict=args.strict, files=args.files, skip_semantic=args.skip_semantic)
        sys.exit(0 if success else 1)
    elif args.command == "simulate":
        target_file = args.file_flag or args.file
        if not target_file:
            simulate_parser.error("Prompt file must be provided either as a positional argument or via -f/--file")
            
        import logging
        if args.verbose:
            logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
            logging.getLogger().setLevel(logging.WARNING)
            
        from promptops.console import set_json_mode, set_no_color
        set_json_mode(args.json)
        set_no_color(args.no_color)
            
        success = simulate_prompt(target_file, args.data, chaos_mode=args.chaos, strict_mode=args.strict)
        sys.exit(0 if success else 1)
    elif args.command == "docs":
        success = generate_docs(args.dir, args.out, args.repo_url, args.branch, check=args.check)
        if args.check and not success:
            sys.exit(1)
        sys.exit(0)
    elif args.command == "agent":
        if args.agent_command == "config":
            generate_config(args.dir)
        elif args.agent_command == "discovery":
            discovery_report(args.dir)
    elif args.command == "vibe":
        from promptops.vibe import run_vibe_audit
        run_vibe_audit(budget_cap=args.budget_cap, coverage=args.coverage)
        sys.exit(0)
    elif args.command == "search":
        search_prompts_func(args.query, args.verbose)
    elif args.command == "export-schemas":
        from promptops.validation import (
            ToolCall, Message, ModelParameters, InputVariable,
            PromptMetadata, InputSchema, MCPTool, PromptSchema, WorkflowInput,
            WorkflowEdge, WorkflowStep, WorkflowMetadata, WorkflowSchema
        )
        models = {
            "ToolCall": ToolCall, "Message": Message, "ModelParameters": ModelParameters, "InputVariable": InputVariable,
            "PromptMetadata": PromptMetadata, "InputSchema": InputSchema, "MCPTool": MCPTool, "PromptSchema": PromptSchema, "WorkflowInput": WorkflowInput,
            "WorkflowEdge": WorkflowEdge, "WorkflowStep": WorkflowStep, "WorkflowMetadata": WorkflowMetadata, "WorkflowSchema": WorkflowSchema
        }
        
        os.makedirs(args.out_dir, exist_ok=True)
        
        for name, model in models.items():
            filename = f"{name}.schema.json"
            if name == "PromptSchema": filename = "prompt.schema.json"
            elif name == "WorkflowSchema": filename = "workflow.schema.json"
            
            path = os.path.join(args.out_dir, filename)
            schema = model.model_json_schema()
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2)
                f.write('\n')
        
        print(f"Exported {len(models)} schemas to {args.out_dir}")
        sys.exit(0)
    elif args.command == "workflow":
        if args.no_color:
            console.set_no_color(True)
        if args.json:
            console.set_json_mode(True)

        strict_mode = args.strict or os.environ.get('CI') == 'true'
        setup_logging(args.verbose)

        initial_inputs = {}

        if args.inputs_file:
            file_ext = args.inputs_file.split('.')[-1].lower()
            try:
                if file_ext in ['yaml', 'yml']:
                    file_inputs = load_yaml(args.inputs_file)
                    if file_inputs is None:
                        sys.exit(1)
                    initial_inputs.update(file_inputs)
                elif file_ext == 'json':
                    with open(args.inputs_file, 'r', encoding='utf-8') as f:
                        initial_inputs.update(json.load(f))
                else:
                    logger.error(f"Unsupported inputs file extension '{file_ext}'.")
                    sys.exit(1)
            except Exception as e:
                logger.error(f"Failed to load inputs file {args.inputs_file}: {e}")
                sys.exit(1)

        if args.input:
            for item in args.input:
                if '=' in item:
                    key, value = item.split('=', 1)
                    initial_inputs[key] = value
                else:
                    logger.warning(f"Invalid input format: {item}. Expected key=value")

        fidelity_report = {
            'evaluators_mocked': False,
            'rate_limits_simulated': False,
            'latency_simulated': False
        }

        workflow_data = load_yaml(args.workflow_file)
        if not initial_inputs and workflow_data and workflow_data.get('testData'):
            for test_case in workflow_data['testData']:
                inputs = test_case.get('inputs', test_case.get('vars', {}))
                console.step_header(f"Running Workflow Test Scenario with inputs: {inputs}")
                try:
                    final_state = run_workflow(args.workflow_file, inputs, verbose=args.verbose, strict_mode=strict_mode, chaos_mode=args.chaos, fidelity_report=fidelity_report)
                    if final_state:
                        final_output_step_id = workflow_data.get('steps', [{}])[-1].get('step_id')
                        if final_output_step_id:
                            final_output = None
                            if final_output_step_id in final_state['steps']:
                                final_output = final_state['steps'][final_output_step_id]['output']
                            elif final_state['steps']:
                                last_key = list(final_state['steps'].keys())[-1]
                                final_output = final_state['steps'][last_key]['output']
                            if final_output is not None:
                                logger.info(f"Scenario Output:\n{final_output}")
                except Exception as e:
                    logger.error(f"Workflow test scenario failed: {e}")
                    sys.exit(1)
            console.step_header("Simulation Finished (All Scenarios)")
        else:
            try:
                final_state = run_workflow(args.workflow_file, initial_inputs, verbose=args.verbose, strict_mode=strict_mode, chaos_mode=args.chaos, fidelity_report=fidelity_report)
            except Exception as e:
                logger.error(f"Workflow simulation failed: {e}")
                sys.exit(1)

            if final_state:
                console.step_header("Simulation Finished")
                final_output_step_id = workflow_data.get('steps', [{}])[-1].get('step_id')
                if final_output_step_id:
                    final_output = None
                    if final_output_step_id in final_state['steps']:
                        final_output = final_state['steps'][final_output_step_id]['output']
                    elif final_state['steps']:
                        last_key = list(final_state['steps'].keys())[-1]
                        final_output = final_state['steps'][last_key]['output']
                    if final_output is not None:
                        logger.info("Final workflow output:")
                        console.info(final_output)

        if getattr(args, 'json', False):
            console.json_output(fidelity_report)
        else:
            console.info("\n[Simulation Fidelity Report]")
            console.info(f"- Evaluators Mocked: {'Yes' if fidelity_report['evaluators_mocked'] else 'No'}")
            console.info(f"- Rate Limits Simulated: {'Yes' if fidelity_report['rate_limits_simulated'] else 'No'}")
            console.info(f"- Latency Simulated: {'Yes' if fidelity_report['latency_simulated'] else 'No'}")
    elif args.command == "generate-cli-docs":
        # Generate markdown documentation for the parser
        out = []
        out.append("# PromptOps CLI Reference\n")
        out.append("This document is auto-generated from the CLI definition. Do not edit manually.\n")
        
        # Main parser help
        out.append("## `promptops`\n")
        out.append("```text")
        out.append(parser.format_help())
        out.append("```\n")
        
        subparsers_actions = [
            action for action in parser._actions 
            if isinstance(action, argparse._SubParsersAction)
        ]
        
        for subparsers_action in subparsers_actions:
            for choice, subparser in subparsers_action.choices.items():
                if choice == "generate-cli-docs":
                    continue
                out.append(f"### `promptops {choice}`\n")
                out.append("```text")
                out.append(subparser.format_help())
                out.append("```\n")
                
                # Check for sub-subparsers (like agent)
                sub_subparsers_actions = [
                    a for a in subparser._actions 
                    if isinstance(a, argparse._SubParsersAction)
                ]
                for ssa in sub_subparsers_actions:
                    for subchoice, subsubparser in ssa.choices.items():
                        out.append(f"#### `promptops {choice} {subchoice}`\n")
                        out.append("```text")
                        out.append(subsubparser.format_help())
                        out.append("```\n")

        with open(args.output, "w", encoding='utf-8') as f:
            f.write("\n".join(out))
        print(f"Generated CLI docs at {args.output}")

if __name__ == "__main__":
    main()
