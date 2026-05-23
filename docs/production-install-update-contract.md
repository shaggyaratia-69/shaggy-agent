# Shaggy Agent production install and update contract

This repository is the permanent production source of truth for Shaggy Agent:

- Official source repo: https://github.com/shaggyaratia-69/shaggy-agent
- Git remote used by installers and updates: https://github.com/shaggyaratia-69/shaggy-agent.git
- Product name: Shaggy Agent / Shaggy the Agent
- Company: Cherries and Co Research

## Customer install commands

Customers can install from the official GitHub source with these commands.

Linux, macOS, WSL2, and Termux:

```bash
curl -fsSL https://raw.githubusercontent.com/shaggyaratia-69/shaggy-agent/main/scripts/install.sh | bash
```

Windows PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/shaggyaratia-69/shaggy-agent/main/scripts/install.ps1)
```

The source installer must clone or update only the official production repo. It must never pull from old upstream repositories or legacy company URLs.

## Customer update command

After installation, customers update with:

```bash
shaggy update
```

`shaggy update` must fetch and pull from the official GitHub production repo through the installed checkout's `origin` remote. The code also treats this repo as the official upstream when a user intentionally works from a fork.

## Password-gated website package downloads

The public Cherries and Co website may show install commands, but protected product ZIP/package downloads must require an access password. The real password must never be committed to this repository, public HTML, installer scripts, test fixtures, release notes, screenshots, or logs.

Use placeholders only:

```text
[SHAGGY_ACCESS_PASSWORD]
```

Approved protected-download behavior:

1. The website/worker protects direct package paths.
2. The Mac/Linux/WSL installer prompts:

```text
Shaggy Agent access password
```

3. The Windows installer prompts with a secure PowerShell prompt.
4. Installers send the user-entered password only in memory as an HTTP header:

```text
X-Shaggy-Access
```

5. If the password is missing or wrong, the package download, unzip, and install fail safely with a clear access-denied message.
6. Direct package links must not be exposed in public page copy unless Rahim explicitly approves that release structure.

## Release process

1. Edit locally in `/Users/shaagy/Projects/shaggy-agent`.
2. Run focused tests, compile checks, `git diff --check`, and branding scans.
3. Commit and push to `origin main`.
4. Verify the GitHub remote after push.
5. If website/package files are changed, rebuild the product ZIP, update checksums, deploy only after approval, then download the live package back and verify checksum and password gate behavior.

## Required public branding scan

Before release, tracked customer-facing text must stay clean of old product/company names and URLs. The regression tests and release checks cover the specific forbidden strings requested for this production repo.
