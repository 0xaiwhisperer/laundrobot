# Contributing to Laundrobot

Thanks for your interest in contributing! This document explains the process for making changes and getting them merged.

## Development setup

```bash
git clone https://github.com/your-org/laundrobot.git
cd laundrobot

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
pre-commit install
```

## Making changes

1. **Fork** the repository on GitHub
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/my-feature
   # or
   git checkout -b fix/the-bug
   ```
3. **Make your changes** — see conventions below
4. **Test** your changes: `pytest tests/`
5. **Lint**: `ruff check .`
6. **Commit** with a clear message:
   ```
   feat: add trajectory looping support
   fix: stop preview loop before FAISS playback
   docs: add hardware wiring diagram
   ```
7. **Open a Pull Request** against `main`

## Coding conventions

### Python
- Follow the existing module structure — one file per concern
- Background loops go in `loops/`, Flask routes go in `routes/`
- Use `log_dash()` (not `print()`) for any output visible in the dashboard log
- Never let a loop hold the serial bus and the preview loop simultaneously — always call `loops.preview.stop()` before touching the bus, and `loops.preview.start()` in the `finally` block

### Serial bus safety pattern
Every loop that drives the robot arms must follow this pattern:

```python
def my_loop():
    from .. import loops as _loops
    _loops.preview.stop()
    try:
        # ... your loop ...
    finally:
        _loops.preview.start()
```

### JavaScript / HTML
- All JS lives inline in the template (no build step required)
- Use `async/await` with the `api(path, body)` helper — don't use `fetch` directly
- Match the existing CSS variable naming (`--bg`, `--grn`, `--rec`, etc.)

### Tests
- Unit tests go in `tests/`
- Use `pytest` fixtures; avoid real hardware in unit tests (mock the robot objects)
- Integration tests that require hardware are tagged `@pytest.mark.hardware` and skipped in CI

## Project structure conventions

```
loops/<name>.py       — one background thread concern per file
routes/<name>.py      — one Flask blueprint per domain
templates/<name>.html — standalone Jinja2 template (no build step)
docs/<topic>.md       — documentation for that topic
scripts/<name>.sh     — shell utility scripts
```

## Reporting bugs

Open a GitHub Issue with:
- Your hardware setup (arm model, OS, Python version)
- The exact error message + traceback from the dashboard Log tab
- Steps to reproduce

## Feature requests

Open a GitHub Discussion first — let's align on the design before writing code. This avoids duplicate effort and ensures the feature fits the project direction.
