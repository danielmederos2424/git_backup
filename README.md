# GitHub Organization Backup Script

## Overview

This Python script provides an automated solution for backing up all repositories within a GitHub organization. It offers a simple, efficient way to create weekly backups of your organization's repositories, helping to ensure data preservation and disaster recovery.

## Features

- 🔄 Automatic backup of all repositories in a specified GitHub organization
- 📅 Weekly backup strategy with date-based folder naming
- 🗑️ Automatic cleanup of old backups (keeps only the latest two)
- 🔐 Secure authentication using GitHub Personal Access Token
- 🌐 Configurable via environment variables

## Prerequisites

- Python 3.7+
- Git
- GitHub Personal Access Token

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/danielmederos2424/git_backup.git
   cd git_backup
   ```

2. Install dependencies:

   ```bash
   pip3 install -r requirements.txt
   ```

## Configuration

Configure the script using environment variables:

- `GITHUB_TOKEN`: Your GitHub Personal Access Token
- `GITHUB_ORG`: Your GitHub Organization name
- `BACKUP_DIR`: Path to backup directory

Alternatively, you can directly modify the script's placeholders.

## Usage

Run the script directly:

```bash
python3 git_backup.py
```

For automated backups, consider scheduling with cron (Linux/macOS) or Task Scheduler (Windows).

## Security Considerations

- Keep your GitHub Personal Access Token confidential
- Use a token with minimal required permissions
- Secure your backup directory with appropriate access controls

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
