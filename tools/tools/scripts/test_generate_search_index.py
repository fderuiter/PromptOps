import unittest
import json
from unittest.mock import patch, mock_open
from pathlib import Path

from tools.scripts.generate_search_index import (
    generate_index,
    extract_compliance,
    extract_complexity,
    extract_maturity,
    extract_audience,
    build_search_entry
)


class TestGenerateSearchIndex(unittest.TestCase):
    @patch('tools.scripts.generate_search_index.ROOT', new_callable=lambda: Path('/fake/root'))
    @patch('tools.scripts.generate_search_index.iter_prompt_files')
    @patch('tools.scripts.generate_search_index.load_yaml')
    @patch('builtins.open', new_callable=mock_open)
    @patch('tools.scripts.generate_search_index.print')
    def test_generate_index_success(self, mock_print, mock_file, mock_load_yaml, mock_iter, mock_root):
        mock_iter.return_value = [
            Path('/fake/root/prompts/test1.prompt.md'),
            Path('/fake/root/prompts/test2.prompt.md')
        ]

        mock_load_yaml.side_effect = [
            {"name": "Test 1", "description": "Desc 1", "tags": ["tag1", "tag2"]},
            {"description": "Desc 2"} # Missing name and tags to test fallbacks
        ]

        generate_index("custom_search.json")

        # Verify iter_prompt_files called with PROMPTS_DIR
        mock_iter.assert_called_once_with(mock_root / "prompts")

        # Verify file opened correctly
        mock_file.assert_called_once_with(mock_root / "custom_search.json", 'w', encoding='utf-8')

        # Get what was written
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)
        data = json.loads(written_content)

        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]["title"], "Test 1")
        self.assertEqual(data[0]["description"], "Desc 1")
        self.assertEqual(data[0]["tags"], "tag1, tag2")
        self.assertEqual(data[0]["url"], "prompts/test1.prompt.md")

        self.assertEqual(data[1]["title"], "prompts/test2.prompt.md")
        self.assertEqual(data[1]["description"], "Desc 2")
        self.assertEqual(data[1]["tags"], "")
        self.assertEqual(data[1]["url"], "prompts/test2.prompt.md")

        mock_print.assert_called_once()

    @patch('tools.scripts.generate_search_index.ROOT', new_callable=lambda: Path('/fake/root'))
    @patch('tools.scripts.generate_search_index.iter_prompt_files')
    @patch('tools.scripts.generate_search_index.load_yaml')
    @patch('builtins.open', new_callable=mock_open)
    @patch('tools.scripts.generate_search_index.print')
    def test_generate_index_value_error(self, mock_print, mock_file, mock_load_yaml, mock_iter, mock_root):
        # File not relative to ROOT
        mock_iter.return_value = [
            Path('/other/path/test.prompt.md')
        ]
        mock_load_yaml.return_value = {}

        generate_index()

        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)
        data = json.loads(written_content)

        # The ValueError should be caught and item skipped
        self.assertEqual(len(data), 0)
        mock_print.assert_called_once()

    @patch('tools.scripts.generate_search_index.ROOT', new_callable=lambda: Path('/fake/root'))
    @patch('tools.scripts.generate_search_index.iter_prompt_files')
    @patch('tools.scripts.generate_search_index.load_yaml')
    @patch('builtins.open', new_callable=mock_open)
    @patch('tools.scripts.generate_search_index.print')
    def test_generate_index_default_output(self, mock_print, mock_file, mock_load_yaml, mock_iter, mock_root):
        mock_iter.return_value = [
            Path('/fake/root/prompts/test.prompt.md')
        ]
        mock_load_yaml.return_value = {"name": "Test"}

        generate_index() # No args, should use default "search.json"

        mock_file.assert_called_once_with(mock_root / "search.json", 'w', encoding='utf-8')

    def test_extract_compliance(self):
        # Case 1: In metadata.requirements as list
        self.assertEqual(
            extract_compliance({"metadata": {"requirements": ["ISO-13485", "HIPAA"]}}),
            ["ISO-13485", "HIPAA"]
        )
        # Case 2: In metadata.requirements as single string
        self.assertEqual(
            extract_compliance({"metadata": {"requirements": "ISO-13485"}}),
            ["ISO-13485"]
        )
        # Case 3: Comma separated string
        self.assertEqual(
            extract_compliance({"metadata": {"requirements": "ISO-13485, HIPAA"}}),
            ["ISO-13485", "HIPAA"]
        )
        # Case 4: Top level requirements
        self.assertEqual(
            extract_compliance({"requirements": ["NIST"]}),
            ["NIST"]
        )
        # Case 5: Missing completely
        self.assertEqual(
            extract_compliance({}),
            []
        )

    def test_extract_complexity(self):
        # Case 1: In metadata
        self.assertEqual(extract_complexity({"metadata": {"complexity": "high"}}), "high")
        # Case 2: Top level
        self.assertEqual(extract_complexity({"complexity": "medium"}), "medium")
        # Case 3: Missing
        self.assertEqual(extract_complexity({}), "")

    def test_extract_maturity(self):
        # Case 1: In metadata
        self.assertEqual(extract_maturity({"metadata": {"maturity": "mature"}}), "mature")
        # Case 2: Top level
        self.assertEqual(extract_maturity({"maturity": "experimental"}), "experimental")
        # Case 3: Missing
        self.assertEqual(extract_maturity({}), "")

    def test_extract_audience(self):
        # Test 1: Developer and product manager role keywords matched
        content_1 = {
            "variables": [
                {"name": "tech_lead", "description": "The tech lead architect who designed the pipeline."},
                {"name": "scrum_master", "description": "Manage agile development process."}
            ]
        }
        # Matches tech_lead (tech lead -> developer, architect -> developer)
        # Matches scrum_master (scrum master -> product_manager, manager -> product_manager)
        self.assertEqual(
            extract_audience(content_1, is_clinical=False),
            ["developer", "product_manager"]
        )

        # Test 2: Clinical reviewer special case
        content_2 = {
            "variables": [
                {"name": "reviewer", "description": "Performs peer review."}
            ]
        }
        # Non-clinical domain
        self.assertEqual(extract_audience(content_2, is_clinical=False), [])
        # Clinical domain
        self.assertEqual(extract_audience(content_2, is_clinical=True), ["clinical_specialist"])

        # Test 3: Ignores helper variables
        content_3 = {
            "variables": [
                {"name": "temp", "description": "The temporary model code of a software engineer."},
                {"name": "api_key", "description": "Architect access code."},
                {"name": "real_architect", "description": "Principal designer."}
            ]
        }
        # temp and api_key are ignored entirely, even if descriptions have "software engineer" or "architect".
        # real_architect is not ignored and matches "architect" -> developer
        self.assertEqual(extract_audience(content_3, is_clinical=False), ["developer"])

    def test_build_search_entry(self):
        content = {
            "metadata": {
                "complexity": "high",
                "maturity": "stable",
                "requirements": ["ISO-13485"]
            },
            "variables": [
                {"name": "finance_analyst", "description": "Auditor reviewing financial portfolio."}
            ]
        }
        # Matches finance_analyst -> financial_analyst, auditor -> financial_analyst / compliance_officer
        # Let's see: "finance" -> financial_analyst, "analyst" -> financial_analyst, "auditor" -> financial_analyst AND compliance_officer, "portfolio" -> financial_analyst
        entry = build_search_entry(
            title="Strategic Financial Auditor",
            description="Auditing financial books",
            base_tags=["finance", "audit"],
            url="prompts/finance_audit.prompt.yaml",
            entry_type="prompt",
            content=content,
            path=Path("/fake/root/prompts/finance_audit.prompt.yaml")
        )

        # High-level dedicated fields
        self.assertEqual(entry["complexity"], "high")
        self.assertEqual(entry["maturity"], "stable")
        self.assertEqual(entry["compliance"], ["ISO-13485"])
        self.assertEqual(entry["audience"], ["compliance_officer", "financial_analyst"])

        # Prefixed tags injected and deduplicated
        expected_tags = "finance, audit, complexity:high, maturity:stable, compliance:ISO-13485, audience:compliance_officer, audience:financial_analyst"
        # Since tags are joined as comma-separated string:
        self.assertEqual(entry["tags"], expected_tags)


if __name__ == '__main__':
    unittest.main()
