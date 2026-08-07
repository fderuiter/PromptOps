import unittest
from unittest.mock import patch


from promptops.guard import guard, ProomptsValidationError  # type: ignore

class TestProomptsGuard(unittest.TestCase):
    @patch("promptops.guard.load_yaml")
    @patch("pathlib.Path.exists")
    def test_valid_json_output(self, mock_exists, mock_load_yaml):
        mock_exists.return_value = True
        mock_load_yaml.return_value = {
            "name": "Test",
            "description": "Test",
            "model": "gpt-4",
            "modelParameters": {"temperature": 0.0},
            "metadata": {"domain": "test", "complexity": "low", "tags": ["skill"]},
            "messages": [{"role": "system", "content": "hello"}, {"role": "user", "content": "world"}],
            "testData": [],
            "evaluators": [],
            "output_schema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "score": {"type": "integer"}
                },
                "required": ["summary"]
            }
        }
        
        @guard(prompt_id="test_prompt")
        def mock_llm_call():
            return '{"summary": "A good summary", "score": 10}'
            
        result = mock_llm_call()
        self.assertEqual(result, '{"summary": "A good summary", "score": 10}')
        
    @patch("promptops.guard.load_yaml")
    @patch("pathlib.Path.exists")
    def test_missing_field(self, mock_exists, mock_load_yaml):
        mock_exists.return_value = True
        mock_load_yaml.return_value = {
            "name": "Test",
            "description": "Test",
            "model": "gpt-4",
            "modelParameters": {"temperature": 0.0},
            "metadata": {"domain": "test", "complexity": "low", "tags": ["skill"]},
            "messages": [{"role": "system", "content": "hello"}, {"role": "user", "content": "world"}],
            "testData": [],
            "evaluators": [],
            "output_schema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"}
                },
                "required": ["summary"]
            }
        }
        
        @guard(prompt_id="test_prompt", mode="fail_fast")
        def mock_llm_call():
            return '{"not_summary": "A good summary"}'
            
        with self.assertRaises(ProomptsValidationError) as ctx:
            mock_llm_call()
        self.assertEqual(str(ctx.exception), "missing required field: 'summary'")

    @patch("promptops.guard.load_yaml")
    @patch("pathlib.Path.exists")
    def test_evaluator_failure(self, mock_exists, mock_load_yaml):
        mock_exists.return_value = True
        mock_load_yaml.return_value = {
            "name": "Test",
            "description": "Test",
            "model": "gpt-4",
            "modelParameters": {"temperature": 0.0},
            "metadata": {"domain": "test", "complexity": "low", "tags": ["skill"]},
            "messages": [{"role": "system", "content": "hello"}, {"role": "user", "content": "world"}],
            "testData": [],
            "evaluators": [
                {"name": "must contain hello", "python": "return 'hello' in output"}
            ]
        }
        
        @guard(prompt_id="test_prompt")
        def mock_llm_call():
            return 'world'
            
        with self.assertRaises(ProomptsValidationError) as ctx:
            mock_llm_call()
        self.assertIn("must contain hello", str(ctx.exception))

    @patch("promptops.guard.load_yaml")
    @patch("pathlib.Path.exists")
    def test_extraction_failure_fail_fast(self, mock_exists, mock_load_yaml):
        import tempfile
        import os
        import json
        import hmac
        import hashlib
        from promptops.engine import get_signing_key

        mock_exists.return_value = True
        mock_load_yaml.return_value = {
            "name": "Test",
            "description": "Test",
            "model": "gpt-4",
            "modelParameters": {"temperature": 0.0},
            "metadata": {"domain": "test", "complexity": "low", "tags": ["skill"]},
            "messages": [{"role": "system", "content": "hello"}],
            "testData": [],
            "evaluators": []
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, {"PROMPTOPS_WORKSPACE_AUDIT": tmp_dir}):
                @guard(prompt_id="test_prompt_fail_fast", mode="fail_fast")
                def mock_llm_call():
                    # Return an unrecognized format
                    return {"unrecognized": "format", "patient_ssn": "123-45-6789"}

                with self.assertRaises(ProomptsValidationError) as ctx:
                    mock_llm_call()
                self.assertIn("Extraction failed", str(ctx.exception))

                # Check that signed audit was written
                failures_dir = os.path.join(tmp_dir, "guard_failures")
                self.assertTrue(os.path.exists(failures_dir))
                files = os.listdir(failures_dir)
                json_files = [f for f in files if f.endswith(".json")]
                sig_files = [f for f in files if f.endswith(".sig")]
                self.assertEqual(len(json_files), 1)
                self.assertEqual(len(sig_files), 1)

                # Verify contents and signature
                json_path = os.path.join(failures_dir, json_files[0])
                sig_path = os.path.join(failures_dir, sig_files[0])

                with open(json_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                
                self.assertEqual(state["prompt_id"], "test_prompt_fail_fast")
                self.assertEqual(state["status"], "extraction_failure")
                self.assertEqual(state["mode"], "fail_fast")
                self.assertIn("Could not extract text", state["error"])

                with open(sig_path, "r", encoding="utf-8") as f:
                    sig_meta = json.load(f)

                self.assertEqual(sig_meta["algorithm"], "HMAC-SHA256")
                
                # Recalculate signature
                key = get_signing_key()
                timestamp = state["timestamp"]
                state_json = json.dumps(state, sort_keys=True)
                payload_to_sign = f"guard_failure|||test_prompt_fail_fast|||{timestamp}|||{state_json}"
                expected_sig = hmac.new(key, payload_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
                self.assertEqual(sig_meta["signature"], expected_sig)

    @patch("promptops.guard.load_yaml")
    @patch("pathlib.Path.exists")
    def test_extraction_failure_warning(self, mock_exists, mock_load_yaml):
        import tempfile
        import os
        import json
        import hmac
        import hashlib
        from promptops.engine import get_signing_key

        mock_exists.return_value = True
        mock_load_yaml.return_value = {
            "name": "Test",
            "description": "Test",
            "model": "gpt-4",
            "modelParameters": {"temperature": 0.0},
            "metadata": {"domain": "test", "complexity": "low", "tags": ["skill"]},
            "messages": [{"role": "system", "content": "hello"}],
            "testData": [],
            "evaluators": []
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, {"PROMPTOPS_WORKSPACE_AUDIT": tmp_dir}):
                @guard(prompt_id="test_prompt_warning", mode="warning")
                def mock_llm_call():
                    # Return an unrecognized format with patient data
                    return {
                        "ssn": "000-12-3456",
                        "email": "john.doe@hospital.org",
                        "phone": "+1 (555) 019-2834",
                        "dob": "1978/11/05"
                    }

                result = mock_llm_call()
                
                # Check output redaction
                self.assertIsInstance(result, str)
                self.assertNotIn("000-12-3456", result)
                self.assertNotIn("john.doe@hospital.org", result)
                self.assertNotIn("555", result)
                self.assertNotIn("1978", result)

                self.assertIn("[REDACTED_SSN]", result)
                self.assertIn("[REDACTED_EMAIL]", result)
                self.assertIn("[REDACTED_PHONE]", result)
                self.assertIn("[REDACTED_DATE]", result)

                # Check that signed audit was written
                failures_dir = os.path.join(tmp_dir, "guard_failures")
                self.assertTrue(os.path.exists(failures_dir))
                files = os.listdir(failures_dir)
                json_files = [f for f in files if f.endswith(".json")]
                sig_files = [f for f in files if f.endswith(".sig")]
                self.assertEqual(len(json_files), 1)
                self.assertEqual(len(sig_files), 1)

                # Verify contents and signature
                json_path = os.path.join(failures_dir, json_files[0])
                sig_path = os.path.join(failures_dir, sig_files[0])

                with open(json_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                
                self.assertEqual(state["prompt_id"], "test_prompt_warning")
                self.assertEqual(state["status"], "extraction_failure")
                self.assertEqual(state["mode"], "warning")
                self.assertIn("[REDACTED_SSN]", state["fallback_content"])

                with open(sig_path, "r", encoding="utf-8") as f:
                    sig_meta = json.load(f)

                self.assertEqual(sig_meta["algorithm"], "HMAC-SHA256")
                
                # Recalculate signature
                key = get_signing_key()
                timestamp = state["timestamp"]
                state_json = json.dumps(state, sort_keys=True)
                payload_to_sign = f"guard_failure|||test_prompt_warning|||{timestamp}|||{state_json}"
                expected_sig = hmac.new(key, payload_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
                self.assertEqual(sig_meta["signature"], expected_sig)

if __name__ == "__main__":
    unittest.main()
