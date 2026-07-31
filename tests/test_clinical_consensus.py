from promptops.engine import run_workflow

def test_clinical_consensus_no_conflict():
    workflow_file = "workflows/clinical/clinical_consensus_arbitration.workflow.yaml"
    initial_inputs = {
        "report_content": "Patient oncology report with cardiac risk assessment.",
        "introduce_conflict": "false"
    }
    
    final_state = run_workflow(workflow_file, initial_inputs, verbose=True, strict_mode=False)
    assert final_state is not None
    
    # Check that oncologist, cardiologist, and toxicologist all approved
    assert "Approved" in final_state["steps"]["oncologist_review"]["output"]
    assert "Approved" in final_state["steps"]["cardiologist_review"]["output"]
    assert "Approved" in final_state["steps"]["toxicologist_review"]["output"]
    
    # Check that arbitration output is consensus
    assert final_state["steps"]["arbitration"]["output"] == "consensus"
    
    # Check that the workflow ended at validated_data and did not run manual_audit
    assert "validated_data" in final_state["steps"]
    assert "manual_audit" not in final_state["steps"]

def test_clinical_consensus_with_conflict():
    workflow_file = "workflows/clinical/clinical_consensus_arbitration.workflow.yaml"
    initial_inputs = {
        "report_content": "Patient oncology report with cardiac risk assessment.",
        "introduce_conflict": "true"
    }
    
    final_state = run_workflow(workflow_file, initial_inputs, verbose=True, strict_mode=False)
    assert final_state is not None
    
    # Check that cardiologist rejected
    assert "Rejected" in final_state["steps"]["cardiologist_review"]["output"]
    
    # Check that arbitration output is disagreement
    assert final_state["steps"]["arbitration"]["output"] == "disagreement"
    
    # Check that manual_audit ran and validated_data did not run
    assert "manual_audit" in final_state["steps"]
    assert "validated_data" not in final_state["steps"]
