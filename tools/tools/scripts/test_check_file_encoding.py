import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from check_file_encoding import check_file, main

def test_check_file_encoding_missing(tmp_path):
    p = tmp_path / "test.py"
    p.write_text("f = open('test.txt')\n", encoding="utf-8")
    errors = check_file(str(p))
    assert errors == [(1, "open")]

def test_check_file_encoding_present(tmp_path):
    p = tmp_path / "test.py"
    p.write_text("f = open('test.txt', encoding='utf-8')\n", encoding="utf-8")
    errors = check_file(str(p))
    assert errors == []

def test_check_file_binary_mode(tmp_path):
    p = tmp_path / "test.py"
    p.write_text("f = open('test.txt', 'rb')\n", encoding="utf-8")
    errors = check_file(str(p))
    assert errors == []
    
    p2 = tmp_path / "test2.py"
    p2.write_text("f = open('test.txt', mode='wb')\n", encoding="utf-8")
    errors2 = check_file(str(p2))
    assert errors2 == []

def test_check_file_read_text_missing(tmp_path):
    p = tmp_path / "test.py"
    p.write_text("Path('test.txt').read_text()\n", encoding="utf-8")
    errors = check_file(str(p))
    assert errors == [(1, "read_text")]

def test_check_file_syntax_error(tmp_path):
    p = tmp_path / "test.py"
    p.write_text("def class int:\n", encoding="utf-8")
    errors = check_file(str(p))
    assert len(errors) == 1
    assert errors[0][0] == -1
    assert "SYNTAX_ERROR" in errors[0][1]

def test_main_success(tmp_path):
    # Mock walk_workspace to yield a clean file
    p = tmp_path / "clean.py"
    p.write_text("open('test.txt', encoding='utf-8')\n", encoding="utf-8")
    
    def mock_walk(*args, **kwargs):
        yield str(tmp_path), [], ["clean.py"]
        
    with patch("promptops.utils.walk_workspace", side_effect=mock_walk):
        with patch.object(sys, 'exit') as mock_exit:
            main()
            mock_exit.assert_called_with(0)

def test_main_failure(tmp_path):
    p = tmp_path / "bad.py"
    p.write_text("open('test.txt')\n", encoding="utf-8")
    
    def mock_walk(*args, **kwargs):
        yield str(tmp_path), [], ["bad.py"]
        
    with patch("promptops.utils.walk_workspace", side_effect=mock_walk):
        with patch.object(sys, 'exit') as mock_exit:
            main()
            mock_exit.assert_called_with(1)
