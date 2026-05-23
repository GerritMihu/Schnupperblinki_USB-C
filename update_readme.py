#!/usr/bin/env python3
"""
Updates README.md with preview links for GitHub.
- Detects the GitHub repository URL.
- Updates the Interactive BOM link using htmlpreview.github.io.
- Ensures other documentation links are present.
"""

import os
import re
import subprocess
import sys
import urllib.parse


def get_git_remote_url():
    try:
        url = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], text=True).strip()
        # Convert SSH to HTTPS if needed
        if url.startswith('git@github.com:'):
            url = url.replace('git@github.com:', 'https://github.com/').replace('.git', '')
        elif url.endswith('.git'):
            url = url[:-4]
        return url
    except Exception:
        # Fallback to env vars (useful in GitHub Actions)
        repo = os.environ.get('GITHUB_REPOSITORY')
        if repo:
            return f'https://github.com/{repo}'
    return None


def get_git_branch():
    try:
        return subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], text=True).strip()
    except Exception:
        return os.environ.get('GITHUB_REF_NAME', 'main')


def find_ibom_file(bom_dir='bom'):
    if not os.path.exists(bom_dir):
        return None
    for f in os.listdir(bom_dir):
        if f.endswith('-ibom.html'):
            return os.path.join(bom_dir, f)
    return None


def update_readme(readme_path='README.md'):
    if not os.path.exists(readme_path):
        print(f'{readme_path} not found.')
        return False

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    repo_url = get_git_remote_url()
    branch = get_git_branch()

    if not repo_url:
        print('Could not determine GitHub repository URL. Skipping README update.')
        return False

    print(f'Detected Repo: {repo_url}')
    print(f'Detected Branch: {branch}')

    ibom_file = find_ibom_file()
    if ibom_file:
        # URL encode the path part
        encoded_path = urllib.parse.quote(ibom_file)
        # htmlpreview.github.io/?https://github.com/USER/REPO/blob/BRANCH/PATH/TO/FILE
        preview_url = f'https://htmlpreview.github.io/?{repo_url}/blob/{branch}/{encoded_path}'
        
        # Look for the BOM link and update it
        # Pattern: [BOM (HTML-Preview)](URL)
        pattern = r'\[BOM \(HTML-Preview\)\]\(.*?\)'
        replacement = f'[BOM (HTML-Preview)]({preview_url})'
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                print(f'Updating BOM preview link in {readme_path}')
                content = new_content
            else:
                print('BOM preview link is already up to date.')
        else:
            print('BOM preview link pattern not found in README.md. You might want to add it manually first or I can append it.')
            # Optional: Append if not found? User might prefer manual placement.
            # For now, just print a warning.

    # Also update PDF/SVG links to be relative if they aren't already, 
    # or ensure they point to the correct branch if preferred.
    # The current README uses relative links like [./Dok/Dok_PCB.pdf](./Dok/Dok_PCB.pdf)
    # which is generally better for GitHub rendering anyway.

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True


if __name__ == '__main__':
    if update_readme():
        print('README update complete.')
        sys.exit(0)
    else:
        sys.exit(1)
