#!/usr/bin/env node

const { execFileSync } = require('node:child_process');

function runGh(args) {
  try {
    return execFileSync('gh', args, { encoding: 'utf8' }).trim();
  } catch (error) {
    const stderr = error.stderr?.toString?.() || error.message;
    console.error(`gh command failed: gh ${args.join(' ')}`);
    console.error(stderr);
    process.exit(1);
  }
}

function usage() {
  console.log(`OpenClaw GitHub PoC

Usage:
  node poc/openclaw-github-poc.js <owner/repo> [state] [limit]

Examples:
  node poc/openclaw-github-poc.js Robertkip/AIgemini closed 10
  node poc/openclaw-github-poc.js cli/cli open 5
`);
}

const repo = process.argv[2];
const state = process.argv[3] || 'closed';
const limit = process.argv[4] || '10';

if (!repo || repo === '--help' || repo === '-h') {
  usage();
  process.exit(repo ? 0 : 1);
}

const authStatus = runGh(['auth', 'status']);
if (!authStatus.includes('Logged in to github.com')) {
  console.error('GitHub CLI is not authenticated. Run: gh auth login');
  process.exit(1);
}

const raw = runGh([
  'issue',
  'list',
  '--repo',
  repo,
  '--state',
  state,
  '--limit',
  String(limit),
  '--json',
  'number,title,closedAt,createdAt,author,labels,url'
]);

const issues = JSON.parse(raw);

const summary = {
  repo,
  state,
  count: issues.length,
  issues: issues.map((issue) => ({
    number: issue.number,
    title: issue.title,
    author: issue.author?.login || null,
    labels: (issue.labels || []).map((label) => label.name),
    createdAt: issue.createdAt || null,
    closedAt: issue.closedAt || null,
    url: issue.url,
  })),
};

console.log(JSON.stringify(summary, null, 2));
