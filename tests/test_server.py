from boot_python.server import _derive_user_spec_prompt, _load_prompts

def test_prompts_load():
    comps = _load_prompts()
    assert "base_instructions.txt" in comps
    assert isinstance(comps["base_instructions.txt"], str)

def test_spec_prompt_parse_ok():
    toml = """
[project]
name = "demo"
description = "Test"
language = "python"
"""
    s = _derive_user_spec_prompt(toml)
    assert "demo" in s and "python" in s

def test_spec_prompt_parse_bad():
    s = _derive_user_spec_prompt("not: toml")
    assert "Description" in s
