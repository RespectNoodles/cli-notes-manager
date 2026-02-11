# CLI Notes Manager

A cross-platform, menu-first CLI to browse and search your personal notes stored as **Markdown files in a separate Git repo**.

## What you get (MVP)
- Numbered menus (type `1`, `2`, etc.)
- Keys: `B` back, `M` main, `S` search, `G` git status, `U` quick sync (prints commands), `C` calculator, `H` help, `Q` quit
- Renders Markdown nicely in terminal (via Rich)
- Reads notes from a separate Git repo you clone locally

---

## Quick start (local dev)

### 1) Clone this app repo
```bash
git clone <YOUR_APP_REPO_URL>
cd cli-notes-manager
```

### 2) Create a venv and install
**macOS/Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

**Windows (PowerShell)**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
```

### 3) Clone your *notes* repo separately (Option A)
Pick a folder you like (example shown uses `~/notes-repo`):

```bash
git clone <YOUR_NOTES_REPO_URL> ~/notes-repo
```

### 4) Create `config.toml`
Copy the template:
```bash
cp config.example.toml config.toml
```

Edit `config.toml` and set `repo_path` to your notes repo location.

### 5) Run
```bash
notes-cli
```

---

## Notes repo structure (recommended)

In your notes repo:

```
notes-repo/
  notes/
    hacking/
      _index.yml
      tools/
        _index.yml
        nmap.md
      sql-injection.md
    general/
      _index.yml
      commands.md
```

Optional `_index.yml` controls title and order.

---

## Development
Run tests:
```bash
pytest -q
```

Lint:
```bash
ruff check .
```

---

## Publishing to GitHub
You already created a GitHub repo `cli-notes-manager`.

From this folder:
```bash
git add -A
git commit -m "Initial project skeleton"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

---

## Safety note about Git
By default, the app only **detects** status and prints copy-ready git commands.
If you enable `allow_git_exec=true`, it can run commands after explicit confirmation.
