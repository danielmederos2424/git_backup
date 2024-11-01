import os
import shutil
import datetime
import requests
import sys
from dotenv import load_dotenv

if not load_dotenv():
    print("Warning: .env file not found. Using system environment variables.")

def validate_environment():
    """Validate required environment variables."""
    required_vars = {
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
        "GITHUB_ORG": os.getenv("GITHUB_ORG"),
        "BACKUP_DIR": os.getenv("BACKUP_DIR")
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        print("\nPlease set these variables in your .env file or environment.")
        print("Example .env file contents:")
        print("GITHUB_TOKEN=your_github_token_here")
        print("GITHUB_ORG=your_organization_name")
        print("BACKUP_DIR=/path/to/backup/directory")
        sys.exit(1)
    
    return required_vars

def get_github_repos(token, org_name):
    """Fetch repositories for a given GitHub organization."""
    repos = []
    page = 1
    
    print(f"\nFetching repositories for organization: {org_name}")
    
    while True:
        url = f"https://api.github.com/orgs/{org_name}/repos"
        headers = {
            "Authorization": f"Bearer {token}", 
            "Accept": "application/vnd.github.v3+json"
        }
        params = {
            "page": page,
            "per_page": 100
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status() 
            
            page_repos = response.json()
            if not page_repos:
                break
            
            repos.extend(page_repos)
            print(f"Fetched page {page} ({len(page_repos)} repositories)")
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"\nError fetching repositories:")
            print(f"Status code: {response.status_code}")
            print(f"Error message: {response.text}")
            print(f"Exception: {str(e)}")
            sys.exit(1)
    
    print(f"Total repositories found: {len(repos)}")
    return repos

def clone_repo(repo_url, destination_dir):
    """Clones a GitHub repository to a local directory."""
    print(f"\nCloning repository: {repo_url}")
    try:

        if os.path.exists(destination_dir):
            print(f"Directory already exists: {destination_dir}")
            print("Removing existing directory...")
            shutil.rmtree(destination_dir)
        
        os.makedirs(destination_dir, exist_ok=True)
        result = os.system(f"git clone --quiet {repo_url} {destination_dir}")
        
        if result == 0:
            print(f"Repository cloned successfully to: {destination_dir}")
        else:
            print(f"Error: Git clone command failed with exit code: {result}")
            
    except Exception as e:
        print(f"Error cloning repository: {str(e)}")
        raise

def delete_old_backups(backup_dir):
    """Deletes old backups, keeping only the latest two."""
    print(f"\nChecking for old backups in: {backup_dir}")
    try:
        if not os.path.exists(backup_dir):
            print("Backup directory does not exist. Skipping cleanup.")
            return
            
        backups = []

        for repo_dir in os.listdir(backup_dir):
            repo_path = os.path.join(backup_dir, repo_dir)
            if os.path.isdir(repo_path):
                for date_dir in os.listdir(repo_path):
                    full_path = os.path.join(repo_path, date_dir)
                    if os.path.isdir(full_path):
                        backups.append((full_path, os.path.getmtime(full_path)))
        

        backups.sort(key=lambda x: x[1], reverse=True)
        
        if len(backups) > 2:
            print(f"Found {len(backups)} backups. Keeping the latest 2.")
            for backup_path, _ in backups[2:]:
                print(f"Deleting old backup: {backup_path}")
                shutil.rmtree(backup_path)
        else:
            print(f"Found {len(backups)} backups. No cleanup needed.")
            
    except Exception as e:
        print(f"Error during backup cleanup: {str(e)}")
        raise

def main():
    print("Starting GitHub Organization Backup Script")
    print("=========================================")
    
    env_vars = validate_environment()
    token = env_vars["GITHUB_TOKEN"]
    org_name = env_vars["GITHUB_ORG"]
    backup_dir = env_vars["BACKUP_DIR"]
    
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    print(f"\nBackup date: {start_of_week.strftime('%Y-%m-%d')}")
    
    try:
        repos = get_github_repos(token, org_name)
        
        if not repos:
            print("No repositories found. Exiting.")
            return
        
        os.makedirs(backup_dir, exist_ok=True)
        
        for repo in repos:
            repo_url = repo['clone_url']
            repo_name = repo['name']
            backup_path = os.path.join(
                backup_dir, 
                repo_name, 
                start_of_week.strftime("%Y-%m-%d")
            )
            
            clone_repo(repo_url, backup_path)
        
        delete_old_backups(backup_dir)
        
        print("\nBackup completed successfully!")
        
    except Exception as e:
        print(f"\nError during backup process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()