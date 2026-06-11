#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${SHAGGY_REPO_URL:-https://github.com/shaggyaratia-69/shaggy-agent.git}"
BRANCH="${SHAGGY_BRANCH:-main}"
SHAGGY_HOME="${SHAGGY_HOME:-$HOME/.shaggy}"
INSTALL_DIR="${SHAGGY_INSTALL_DIR:-$SHAGGY_HOME/shaggy-agent}"
BIN_DIR="${SHAGGY_BIN_DIR:-$HOME/.local/bin}"
PYTHON_VERSION="${SHAGGY_PYTHON_VERSION:-3.11}"

echo "Shaggy Agent installer"
echo "Repo: $REPO_URL"
echo "Install dir: $INSTALL_DIR"
echo "Data dir: $SHAGGY_HOME"

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    return 1
  fi
}

if ! need_cmd git; then
  echo "Error: git is required. Install Git first, then run this installer again." >&2
  exit 1
fi

if ! need_cmd curl; then
  echo "Error: curl is required. Install curl first, then run this installer again." >&2
  exit 1
fi

mkdir -p "$SHAGGY_HOME" "$BIN_DIR"

if ! need_cmd uv; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

if ! need_cmd uv; then
  echo "Error: uv install did not put uv on PATH. Restart Terminal and rerun this installer." >&2
  exit 1
fi

if [ -d "$INSTALL_DIR/.git" ]; then
  echo "Existing Shaggy git install found. Updating safely..."
  cd "$INSTALL_DIR"
  current_url="$(git remote get-url origin 2>/dev/null || true)"
  if [ -z "$current_url" ]; then
    git remote add origin "$REPO_URL"
  elif [ "$current_url" != "$REPO_URL" ]; then
    echo "Updating origin remote to Shaggy repo..."
    git remote set-url origin "$REPO_URL"
  fi
  git fetch --prune origin
  if [ -n "$(git status --porcelain)" ]; then
    echo "Local code changes detected. Saving them in git stash before update..."
    git stash push -u -m "local changes before Shaggy installer update"
  fi
  git checkout "$BRANCH"
  git pull --ff-only origin "$BRANCH"
elif [ -e "$INSTALL_DIR" ]; then
  backup="$INSTALL_DIR.backup.$(date +%Y%m%d_%H%M%S)"
  echo "Existing non-git install folder found. Moving it to: $backup"
  mv "$INSTALL_DIR" "$backup"
  git clone --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
else
  echo "Cloning Shaggy Agent..."
  git clone --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

echo "Creating virtual environment..."
uv venv .venv --python "$PYTHON_VERSION"

echo "Installing Shaggy Agent..."
uv pip install --python .venv/bin/python -e .

cat > "$BIN_DIR/shaggy" <<EOF
#!/usr/bin/env bash
export SHAGGY_HOME="${SHAGGY_HOME}"
cd "${INSTALL_DIR}"
exec "${INSTALL_DIR}/.venv/bin/shaggy" "\$@"
EOF
chmod +x "$BIN_DIR/shaggy"

cat > "$BIN_DIR/shaggy-agent" <<EOF
#!/usr/bin/env bash
export SHAGGY_HOME="${SHAGGY_HOME}"
cd "${INSTALL_DIR}"
exec "${INSTALL_DIR}/.venv/bin/shaggy-agent" "\$@"
EOF
chmod +x "$BIN_DIR/shaggy-agent"

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *)
    shell_file="$HOME/.zshrc"
    if [ -n "${BASH_VERSION:-}" ]; then
      shell_file="$HOME/.bashrc"
    fi
    if [ -f "$shell_file" ] && ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$shell_file"; then
      printf '\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$shell_file"
    elif [ ! -f "$shell_file" ]; then
      printf 'export PATH="$HOME/.local/bin:$PATH"\n' >> "$shell_file"
    fi
    export PATH="$BIN_DIR:$PATH"
    ;;
esac

echo "Verifying Shaggy..."
"$BIN_DIR/shaggy" --version || true
"$BIN_DIR/shaggy" doctor || true

echo ""
echo "Done."
echo "Run: shaggy setup"
echo "Then: shaggy"
echo "If the command is not found, restart Terminal and try again."
