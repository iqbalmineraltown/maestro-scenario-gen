#!/usr/bin/env node

/**
 * OpenSkill CLI - Install Claude Code skills from GitHub repositories
 *
 * Usage:
 *   npx openskill https://github.com/user/repo
 *   npx openskill github.com/user/repo
 *   npx openskill user/repo
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Parse GitHub URL into owner/repo
function parseGitHubUrl(input) {
  // Remove protocol and domain if present
  let cleaned = input
    .replace(/^https?:\/\//, '')
    .replace(/^git@/, '')
    .replace(/\.git$/, '');

  // Remove github.com: or github.com/ prefix
  cleaned = cleaned.replace(/^github\.com[:/]/, '');

  // Should now be owner/repo
  const parts = cleaned.split('/');
  if (parts.length < 2) {
    throw new Error(`Invalid GitHub repository: ${input}`);
  }

  return {
    owner: parts[0],
    repo: parts[1],
    fullName: `${parts[0]}/${parts[1]}`
  };
}

// Download file from GitHub
function downloadFile(owner, repo, filePath, destPath) {
  return new Promise((resolve, reject) => {
    const url = `https://raw.githubusercontent.com/${owner}/${repo}/main/${filePath}`;
    const fallbackUrl = `https://raw.githubusercontent.com/${owner}/${repo}/master/${filePath}`;

    const tryDownload = (urlToTry, fallback = null) => {
      https.get(urlToTry, (res) => {
        if (res.statusCode === 404 && fallback) {
          tryDownload(fallback);
          return;
        }
        if (res.statusCode !== 200) {
          reject(new Error(`Failed to download ${filePath}: ${res.statusCode}`));
          return;
        }

        const dir = path.dirname(destPath);
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }

        const file = fs.createWriteStream(destPath);
        res.pipe(file);
        file.on('finish', () => {
          file.close();
          resolve();
        });
      }).on('error', reject);
    };

    tryDownload(url, fallbackUrl);
  });
}

// Get skill metadata from SKILL.md
function getSkillMetadata(skillMdPath) {
  try {
    const content = fs.readFileSync(skillMdPath, 'utf8');

    // Parse YAML frontmatter
    const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (frontmatterMatch) {
      const frontmatter = frontmatterMatch[1];
      const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
      const descMatch = frontmatter.match(/^description:\s*[\s]*([\s\S]*?)(?=^[a-z]|\s*$)/m);

      return {
        name: nameMatch ? nameMatch[1].trim() : null,
        description: descMatch ? descMatch[1].trim().split('\n')[0].trim() : null
      };
    }
  } catch (e) {
    // Ignore
  }
  return { name: null, description: null };
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
\x1b[36m╔════════════════════════════════════════════════════════════╗
║              \x1b[1mOpenSkill - Claude Code Skill Installer\x1b[0m\x1b[36m             ║
╚════════════════════════════════════════════════════════════╝\x1b[0m

\x1b[1mUsage:\x1b[0m
  npx openskill <github-url>
  npx openskill <owner/repo>

\x1b[1mExamples:\x1b[0m
  npx openskill https://github.com/iqbalmineraltown/maestro-scenario-gen
  npx openskill iqbalmineraltown/maestro-scenario-gen

\x1b[1mOptions:\x1b[0m
  --help, -h     Show this help message
  --version, -v  Show version
  --list         List installed skills
`);
    process.exit(0);
  }

  if (args[0] === '--version' || args[0] === '-v') {
    const pkg = require('./package.json');
    console.log(`openskill v${pkg.version}`);
    process.exit(0);
  }

  if (args[0] === '--list') {
    const skillsDir = path.join(process.env.HOME, '.claude', 'skills');
    if (!fs.existsSync(skillsDir)) {
      console.log('No skills installed yet.');
      process.exit(0);
    }
    const skills = fs.readdirSync(skillsDir).filter(f => {
      return fs.statSync(path.join(skillsDir, f)).isDirectory();
    });
    if (skills.length === 0) {
      console.log('No skills installed yet.');
    } else {
      console.log('\x1b[1mInstalled Skills:\x1b[0m');
      skills.forEach(skill => {
        const skillMdPath = path.join(skillsDir, skill, 'SKILL.md');
        if (fs.existsSync(skillMdPath)) {
          const meta = getSkillMetadata(skillMdPath);
          console.log(`  \x1b[36m•\x1b[0m ${skill}${meta.description ? ` - ${meta.description.substring(0, 60)}...` : ''}`);
        } else {
          console.log(`  \x1b[36m•\x1b[0m ${skill}`);
        }
      });
    }
    process.exit(0);
  }

  const input = args[0];
  let github;

  try {
    github = parseGitHubUrl(input);
  } catch (e) {
    console.error(`\x1b[31m✗ Error:\x1b[0m ${e.message}`);
    process.exit(1);
  }

  console.log(`\x1b[36m╔════════════════════════════════════════════════════════════╗
║              \x1b[1mOpenSkill - Claude Code Skill Installer\x1b[0m\x1b[36m             ║
╚════════════════════════════════════════════════════════════╝\x1b[0m
`);
  console.log(`\x1b[90m→ Installing skill from ${github.fullName}...\x1b[0m`);

  // Determine skill name (will be set from SKILL.md or repo name)
  const skillName = github.repo.replace(/-/g, '-').toLowerCase();
  const skillsDir = path.join(process.env.HOME, '.claude', 'skills');
  const targetDir = path.join(skillsDir, skillName);

  // Create skills directory if it doesn't exist
  if (!fs.existsSync(skillsDir)) {
    fs.mkdirSync(skillsDir, { recursive: true });
  }

  // Files to download
  const filesToDownload = [
    'SKILL.md',
    'scripts/analyze_widgets.py',
    'scripts/generate_scenario.py',
    'references/flutter-semantics.md',
    'references/commands.md'
  ];

  // Download each file
  let downloadedCount = 0;
  const errors = [];

  for (const file of filesToDownload) {
    const destPath = path.join(targetDir, file);
    try {
      await downloadFile(github.owner, github.repo, file, destPath);
      downloadedCount++;
      console.log(`  \x1b[32m✓\x1b[0m ${file}`);
    } catch (e) {
      // Non-critical files can fail silently
      if (file === 'SKILL.md') {
        errors.push(file);
        console.log(`  \x1b[31m✗\x1b[0m ${file} (required)`);
      } else {
        console.log(`  \x1b[33m○\x1b[0m ${file} (optional, skipped)`);
      }
    }
  }

  if (errors.length > 0) {
    console.error(`\n\x1b[31m✗ Failed to install skill. Missing required files.\x1b[0m`);
    process.exit(1);
  }

  // Get skill metadata
  const skillMdPath = path.join(targetDir, 'SKILL.md');
  const meta = getSkillMetadata(skillMdPath);

  console.log(`
\x1b[32m╔════════════════════════════════════════════════════════════╗
║                    \x1b[1m✓ Skill Installed!\x1b[0m\x1b[32m                        ║
╚════════════════════════════════════════════════════════════╝\x1b[0m

\x1b[1mName:\x1b[0m        ${meta.name || skillName}
\x1b[1mLocation:\x1b[0m    ${targetDir}
\x1b[1mFiles:\x1b[0m       ${downloadedCount} installed

\x1b[90mThe skill is now available in Claude Code.\x1b[0m
\x1b[90mRestart Claude Code if it was already running.\x1b[0m
`);
}

main().catch(err => {
  console.error(`\x1b[31m✗ Error:\x1b[0m ${err.message}`);
  process.exit(1);
});
