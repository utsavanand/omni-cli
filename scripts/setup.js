#!/usr/bin/env node

const { execSync, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

console.log('Setting up omni-cli...\n');

/**
 * Find Python command
 */
function findPython() {
  const pythonCommands = ['python3', 'python'];

  for (const cmd of pythonCommands) {
    try {
      const result = spawnSync(cmd, ['--version'], {
        stdio: 'pipe',
        encoding: 'utf8'
      });

      if (result.status === 0) {
        const versionMatch = result.stdout.match(/Python (\d+)\.(\d+)/);
        if (versionMatch) {
          const major = parseInt(versionMatch[1]);
          const minor = parseInt(versionMatch[2]);

          if (major === 3 && minor >= 9) {
            return { cmd, version: result.stdout.trim() };
          } else if (major > 3) {
            return { cmd, version: result.stdout.trim() };
          }
        }
      }
    } catch (e) {
      continue;
    }
  }

  return null;
}

/**
 * Main setup
 */
function main() {
  try {
    // 1. Check Python
    console.log('Checking Python...');
    const python = findPython();

    if (!python) {
      console.error('✗ Python 3.9+ is required but not found');
      console.error('');
      console.error('Please install Python from: https://www.python.org/downloads/');
      console.error('');
      console.error('Omni CLI requires Python to run, but installation will continue.');
      console.error('You will need to install Python before running omni.');
      return; // Don't fail install, just warn
    }

    console.log(`✓ Found ${python.version}`);

    // 2. Install Python dependencies
    const requirementsPath = path.join(__dirname, '..', 'requirements.txt');

    if (fs.existsSync(requirementsPath)) {
      console.log('\nInstalling Python dependencies...');

      try {
        // Try to install with pip using --user flag (works with PEP 668)
        execSync(`${python.cmd} -m pip install --user --quiet -r "${requirementsPath}"`, {
          stdio: 'pipe' // Capture output to check for errors
        });
        console.log('✓ Python dependencies installed');
      } catch (e) {
        // If --user fails, try with --break-system-packages as fallback
        try {
          execSync(`${python.cmd} -m pip install --break-system-packages --quiet -r "${requirementsPath}"`, {
            stdio: 'pipe'
          });
          console.log('✓ Python dependencies installed (system packages)');
        } catch (e2) {
          console.warn('⚠ Warning: Failed to install Python dependencies automatically');
          console.warn('Please run manually:');
          console.warn(`  ${python.cmd} -m pip install --user -r "${requirementsPath}"`);
          console.warn('');
        }
      }
    }

    // 3. Create omni config directory
    console.log('\nSetting up configuration...');
    const homeDir = os.homedir();
    const omniDir = path.join(homeDir, '.omni');
    const chatsDir = path.join(omniDir, 'chats', 'permanent');

    if (!fs.existsSync(chatsDir)) {
      fs.mkdirSync(chatsDir, { recursive: true });
      console.log(`✓ Created config directory: ${omniDir}`);
    }

    // 4. Success
    console.log('\n✓ Omni CLI setup complete!');
    console.log('\nRun "omni" to get started');
    console.log('Type "/exit" to quit omni\n');

  } catch (error) {
    console.error('Setup encountered an error:', error.message);
    console.error('\nOmni CLI may not work correctly.');
    console.error('Please report this issue at: https://github.com/omni-cli/omni/issues');
    // Don't exit with error - let install complete
  }
}

// Run setup
main();
