import pytest
from notes_cli.utils.calc import safe_eval, CalcError

def test_safe_eval_basic():
    assert safe_eval("2+3*4") == 14.0
    assert safe_eval("(2+3)*4") == 20.0

def test_safe_eval_blocks_names():
    with pytest.raises(CalcError):
        safe_eval("__import__('os').system('echo hi')")
