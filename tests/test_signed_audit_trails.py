import json
import yaml
import pytest

from promptops.engine import (
    requires_signed_audit,
    redact_sensitive_data,
    run_workflow,
    verify_audit_trail
)

def test_requires_signed_audit():
    # 1. Matches clinical domain
    wf_clinical = {
        "name": "Normal workflow name",
        "metadata": {
            "domain": "clinical"
        }
    }
    assert requires_signed_audit(wf_clinical) is True

    # 2. Matches tags containing compliance standards
    wf_cfr11 = {
        "name": "Standard workflow name",
        "metadata": {
            "domain": "general",
            "tags": ["21 CFR Part 11"]
        }
    }
    assert requires_signed_audit(wf_cfr11) is True

    # 3. Matches standard in title (case insensitive)
    wf_iso = {
        "name": "ISO 14971 Risk Analysis",
        "metadata": {
            "domain": "general"
        }
    }
    assert requires_signed_audit(wf_iso) is True

    # 4. Does not match general non-clinical workflow
    wf_general = {
        "name": "Recipe Generator",
        "metadata": {
            "domain": "culinary"
        }
    }
    assert requires_signed_audit(wf_general) is False


def test_redact_sensitive_data():
    raw_data = {
        "user_email": "john.doe@example.com",
        "nested_dict": {
            "ssn": "123-45-6789",
            "unrelated": "safe text"
        },
        "phone_numbers": ["+1-555-555-5555", "555-123-4567"],
        "dates_list": ["2026-08-05", "08/05/2026"]
    }

    redacted = redact_sensitive_data(raw_data)

    assert redacted["user_email"] == "[REDACTED_EMAIL]"
    assert redacted["nested_dict"]["ssn"] == "[REDACTED_SSN]"
    assert redacted["nested_dict"]["unrelated"] == "safe text"
    assert redacted["phone_numbers"][0] == "[REDACTED_PHONE]"
    assert redacted["phone_numbers"][1] == "[REDACTED_PHONE]"
    assert redacted["dates_list"][0] == "[REDACTED_DATE]"
    assert redacted["dates_list"][1] == "[REDACTED_DATE]"


def test_signed_audit_trail_generation_and_verification(tmp_path, monkeypatch):
    # Set up dynamic test directory for audit logs
    monkeypatch.setenv("PROMPTOPS_WORKSPACE_AUDIT", str(tmp_path / "test_workspace_audit"))

    # Create dynamic dummy prompt file and workflow file
    prompt_file = tmp_path / "test_step.prompt.yaml"
    prompt_data = {
        "name": "Test Step Prompt",
        "version": "1.0.0",
        "description": "Test Step Prompt",
        "metadata": {
            "domain": "clinical",
            "complexity": "low"
        },
        "variables": [
            {"name": "patient_id", "description": "ID", "required": True}
        ],
        "model": "default",
        "modelParameters": {"temperature": 0.0},
        "messages": [
            {"role": "system", "content": "You are a clinical assistant."},
            {"role": "user", "content": "Patient details for: {{patient_id}}"}
        ],
        "testData": [
            {
                "inputs": {"patient_id": "PT-99"},
                "expected": "Patient details for: PT-99"
            }
        ],
        "evaluators": []
    }
    with open(prompt_file, 'w', encoding='utf-8') as f:
        yaml.dump(prompt_data, f)

    workflow_file = tmp_path / "clinical_trial.workflow.yaml"
    workflow_data = {
        "name": "Clinical Trial Setup",
        "description": "A workflow matched against clinical compliance",
        "metadata": {
            "domain": "clinical"
        },
        "inputs": [
            {"name": "patient_id", "description": "Patient ID"}
        ],
        "steps": [
            {
                "step_id": "setup_patient",
                "prompt_file": str(prompt_file),
                "map_inputs": {
                    "patient_id": "{{inputs.patient_id}}"
                }
            }
        ],
        "testData": [
            {
                "inputs": {"patient_id": "PT-99"}
            }
        ]
    }
    with open(workflow_file, 'w', encoding='utf-8') as f:
        yaml.dump(workflow_data, f)

    # Run the workflow
    state = run_workflow(str(workflow_file), {"patient_id": "PT-99"}, verbose=False)
    assert state is not None

    # Retrieve generated run ID folder in test workspace audit
    audit_base = tmp_path / "test_workspace_audit"
    run_folders = [d for d in audit_base.glob("*") if d.is_dir()]
    assert len(run_folders) == 1

    run_dir = run_folders[0]
    
    # Check that companion signature files were generated
    state_files = list(run_dir.glob("checkpoint_setup_patient_1.json"))
    sig_files = list(run_dir.glob("checkpoint_setup_patient_1.sig"))
    assert len(state_files) == 1
    assert len(sig_files) == 1

    # Verify that the audit logs validate successfully (GREEN)
    assert verify_audit_trail(str(audit_base)) is True


def test_signature_mismatch_detection(tmp_path, monkeypatch):
    monkeypatch.setenv("PROMPTOPS_WORKSPACE_AUDIT", str(tmp_path / "test_workspace_audit"))

    # Create dummy prompt and workflow
    prompt_file = tmp_path / "step.prompt.yaml"
    prompt_data = {
        "name": "Prompt",
        "version": "1.0.0",
        "description": "Prompt",
        "metadata": {"domain": "clinical", "complexity": "low"},
        "variables": [{"name": "inp", "description": "i", "required": True}],
        "model": "default",
        "modelParameters": {"temperature": 0.0},
        "messages": [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "{{inp}}"}
        ],
        "testData": [{"inputs": {"inp": "ok"}, "expected": "out"}],
        "evaluators": []
    }
    with open(prompt_file, 'w', encoding='utf-8') as f:
        yaml.dump(prompt_data, f)

    workflow_file = tmp_path / "clinical.workflow.yaml"
    workflow_data = {
        "name": "Clinical",
        "metadata": {"domain": "clinical"},
        "inputs": [{"name": "inp"}],
        "steps": [
            {
                "step_id": "step1",
                "prompt_file": str(prompt_file),
                "map_inputs": {"inp": "{{inputs.inp}}"}
            }
        ]
    }
    with open(workflow_file, 'w', encoding='utf-8') as f:
        yaml.dump(workflow_data, f)

    run_workflow(str(workflow_file), {"inp": "ok"}, verbose=False)

    audit_base = tmp_path / "test_workspace_audit"
    run_folders = [d for d in audit_base.glob("*") if d.is_dir()]
    run_dir = run_folders[0]

    state_file = run_dir / "checkpoint_step1_1.json"
    
    # Verify passes initially
    assert verify_audit_trail(str(audit_base)) is True

    # 1. Modify the state file manually -> verification should fail (RED)
    with open(state_file, 'r', encoding='utf-8') as f:
        state_data = json.load(f)
    
    state_data["workflow_state"]["steps"]["step1"]["output"] = "tampered_output"
    
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state_data, f)

    assert verify_audit_trail(str(audit_base)) is False


def test_missing_signature_detection(tmp_path, monkeypatch):
    monkeypatch.setenv("PROMPTOPS_WORKSPACE_AUDIT", str(tmp_path / "test_workspace_audit"))

    # Create dummy prompt and workflow
    prompt_file = tmp_path / "step.prompt.yaml"
    prompt_data = {
        "name": "Prompt",
        "version": "1.0.0",
        "description": "Prompt",
        "metadata": {"domain": "clinical", "complexity": "low"},
        "variables": [{"name": "inp", "description": "i", "required": True}],
        "model": "default",
        "modelParameters": {"temperature": 0.0},
        "messages": [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "{{inp}}"}
        ],
        "testData": [{"inputs": {"inp": "ok"}, "expected": "out"}],
        "evaluators": []
    }
    with open(prompt_file, 'w', encoding='utf-8') as f:
        yaml.dump(prompt_data, f)

    workflow_file = tmp_path / "clinical.workflow.yaml"
    workflow_data = {
        "name": "Clinical",
        "metadata": {"domain": "clinical"},
        "inputs": [{"name": "inp"}],
        "steps": [
            {
                "step_id": "step1",
                "prompt_file": str(prompt_file),
                "map_inputs": {"inp": "{{inputs.inp}}"}
            }
        ]
    }
    with open(workflow_file, 'w', encoding='utf-8') as f:
        yaml.dump(workflow_data, f)

    run_workflow(str(workflow_file), {"inp": "ok"}, verbose=False)

    audit_base = tmp_path / "test_workspace_audit"
    run_folders = [d for d in audit_base.glob("*") if d.is_dir()]
    run_dir = run_folders[0]

    sig_file = run_dir / "checkpoint_step1_1.sig"
    assert sig_file.exists()

    # Delete signature file
    sig_file.unlink()

    # Verification should fail
    assert verify_audit_trail(str(audit_base)) is False


def test_failed_loop_exceeded_captured_and_signed(tmp_path, monkeypatch):
    monkeypatch.setenv("PROMPTOPS_WORKSPACE_AUDIT", str(tmp_path / "test_workspace_audit"))

    # Create dummy prompt and workflow with a loop limit exceeding pattern
    prompt_file = tmp_path / "loop_step.prompt.yaml"
    prompt_data = {
        "name": "Loop Step Prompt",
        "version": "1.0.0",
        "description": "Prompt",
        "metadata": {"domain": "clinical", "complexity": "low"},
        "variables": [{"name": "inp", "description": "i", "required": True}],
        "model": "default",
        "modelParameters": {"temperature": 0.0},
        "messages": [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "{{inp}}"}
        ],
        "testData": [{"inputs": {"inp": "ok"}, "expected": "out"}],
        "evaluators": []
    }
    with open(prompt_file, 'w', encoding='utf-8') as f:
        yaml.dump(prompt_data, f)

    # Define a workflow that self-loops to step1 always
    workflow_file = tmp_path / "looping.workflow.yaml"
    workflow_data = {
        "name": "Looping Clinical Workflow",
        "metadata": {"domain": "clinical"},
        "inputs": [{"name": "inp"}],
        "max_iterations": 2,
        "steps": [
            {
                "step_id": "step1",
                "prompt_file": str(prompt_file),
                "map_inputs": {"inp": "{{inputs.inp}}"},
                "next": "step1" # Infinite loop
            }
        ]
    }
    with open(workflow_file, 'w', encoding='utf-8') as f:
        yaml.dump(workflow_data, f)

    # Running it should raise exception for loop limit exceeded
    with pytest.raises(Exception, match="Loop Limit Exceeded"):
        run_workflow(str(workflow_file), {"inp": "ok"}, verbose=False)

    # Assert that a failed/loop exceeded state JSON and sig were generated and signed
    audit_base = tmp_path / "test_workspace_audit"
    run_folders = [d for d in audit_base.glob("*") if d.is_dir()]
    assert len(run_folders) == 1
    run_dir = run_folders[0]

    loop_state_files = list(run_dir.glob("checkpoint_loop_exceeded_step1_2.json"))
    loop_sig_files = list(run_dir.glob("checkpoint_loop_exceeded_step1_2.sig"))
    assert len(loop_state_files) == 1
    assert len(loop_sig_files) == 1

    # Check contents for loop warning flag
    with open(loop_state_files[0], 'r', encoding='utf-8') as f:
        failed_state = json.load(f)
    
    assert "Loop Limit Exceeded" in failed_state["errors"]
    assert any("Loop Limit Exceeded" in w for w in failed_state["warnings"])

    # Ensure validation detects the failed loop signature is correct and valid
    assert verify_audit_trail(str(audit_base)) is True
