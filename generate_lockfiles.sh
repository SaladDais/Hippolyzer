uv pip compile --extra gui --extra proxy --output-file=requirements.txt pyproject.toml
uv pip compile --extra gui --extra proxy --extra test --output-file=requirements-test.txt pyproject.toml
