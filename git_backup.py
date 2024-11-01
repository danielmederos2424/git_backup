import os
import shutil
import datetime
import requests
import sys
from dotenv import load_dotenv

if not load_dotenv():
    print("Warning: .env file not found. Using system environment variables.")

def validate_environment():
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
        sys.exit(1)
    
    return required_vars

def get_github_repos(token, org_name):
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
            print(f"\nError fetching repositories: {str(e)}")
            sys.exit(1)
    
    print(f"Total repositories found: {len(repos)}")
    return repos

def clone_repo(repo_url, destination_dir, token):
    print(f"\nCloning repository: {repo_url}")
    try:
        auth_url = repo_url.replace("https://", f"https://oauth2:{token}@")
        result = os.system(f"git clone --quiet {auth_url} {destination_dir}")
        
        if result == 0:
            print(f"Repository cloned successfully")
        else:
            print(f"Error: Git clone failed with exit code: {result}")
            
    except Exception as e:
        print(f"Error cloning repository: {str(e)}")
        raise

def delete_old_backups(backup_dir):
    print(f"\nChecking for old backups in: {backup_dir}")
    try:
        if not os.path.exists(backup_dir):
            return
            
        backup_dates = [d for d in os.listdir(backup_dir) if os.path.isdir(os.path.join(backup_dir, d))]
        backup_dates.sort(reverse=True)
        
        if len(backup_dates) > 2:
            for old_date in backup_dates[2:]:
                old_path = os.path.join(backup_dir, old_date)
                print(f"Deleting old backup: {old_path}")
                shutil.rmtree(old_path)
            
    except Exception as e:
        print(f"Error during backup cleanup: {str(e)}")
        raise

def main():
    print("Starting GitHub Organization Backup Script")
    
    env_vars = validate_environment()
    token = env_vars["GITHUB_TOKEN"]
    org_name = env_vars["GITHUB_ORG"]
    backup_dir = env_vars["BACKUP_DIR"]
    
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    backup_date = start_of_week.strftime("%Y-%m-%d")
    
    try:
        repos = get_github_repos(token, org_name)
        
        if not repos:
            print("No repositories found. Exiting.")
            return
        
        date_backup_dir = os.path.join(backup_dir, backup_date)
        os.makedirs(date_backup_dir, exist_ok=True)
        
        for repo in repos:
            repo_url = repo['clone_url']
            repo_name = repo['name']
            repo_backup_path = os.path.join(date_backup_dir, repo_name)
            
            if os.path.exists(repo_backup_path):
                shutil.rmtree(repo_backup_path)
            
            clone_repo(repo_url, repo_backup_path, token)
        
        delete_old_backups(backup_dir)
        
        print("\nBackup completed successfully!")
        
    except Exception as e:
        print(f"\nError during backup process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()