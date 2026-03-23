# OpenClaw ↔ GitHub PoC

Small proof-of-concept for using GitHub access from this OpenClaw workspace.

## What it does

The PoC script uses the GitHub CLI (`gh`) to:
- verify GitHub auth
- query issues from a repo
- print a clean JSON summary

This mirrors the kind of GitHub access OpenClaw can perform when asked to inspect issues, PRs, or CI.

## Files

- `poc/openclaw-github-poc.js` — Node script that fetches issue data with `gh`

## Requirements

- Node.js
- GitHub CLI (`gh`)
- authenticated session: `gh auth status`

## Usage

```bash
node poc/openclaw-github-poc.js <owner/repo> [state] [limit]
```

Examples:

```bash
node poc/openclaw-github-poc.js Robertkip/AIgemini closed 10
node poc/openclaw-github-poc.js cli/cli open 5
```

## Expected output

JSON like:

```json
{
  "repo": "Robertkip/AIgemini",
  "state": "closed",
  "count": 3,
  "issues": [
    {
      "number": 3,
      "title": "Add dark mode",
      "author": "Robertkip",
      "labels": [],
      "createdAt": null,
      "closedAt": "2026-03-22T10:39:54Z",
      "url": "https://github.com/Robertkip/AIgemini/issues/3"
    }
  ]
}
```

## Why this is useful

This gives you a minimal, inspectable baseline for GitHub access before building something bigger, like:
- issue triage automation
- PR summaries
- release-note generation
- OpenClaw commands that query GitHub and report back in chat
