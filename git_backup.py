import os
import shutil
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

def get_github_repos(token, org_name):
    """Fetch repositories for a given GitHub organization."""
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org_name}/repos"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        params = {
            "page": page,
            "per_page": 100
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching repositories: {response.status_code}")
            print(f"Response: {response.text}")
            break
        
        page_repos = response.json()
        
        if not page_repos:
            break
        
        repos.extend(page_repos)
        page += 1
    
    return repos

def clone_repo(repo_url, destination_dir):
    """Clones a GitHub repository to a local directory."""
    print(f"Cloning repository: {repo_url}")
    try:
        os.makedirs(destination_dir, exist_ok=True)
        os.system(f"git clone {repo_url} {destination_dir}")
        print(f"Repository cloned successfully: {repo_url}")
    except Exception as e:
        print(f"Error cloning repository: {repo_url} - {str(e)}")

def delete_old_backups(backup_dir):
    """Deletes old backups, keeping only the latest two."""
    print("Deleting old backups...")
    try:
        backups = os.listdir(backup_dir)
        backups.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)), reverse=True)
        if len(backups) > 2:
            for backup in backups[2:]:
                try:
                    shutil.rmtree(os.path.join(backup_dir, backup))
                    print(f"Deleted old backup: {backup}")
                except Exception as e:
                    print(f"Error deleting backup: {backup} - {str(e)}")
    except FileNotFoundError:
        print(f"Backup directory {backup_dir} does not exist.")
    except Exception as e:
        print(f"Error processing backups: {str(e)}")

def main():
    token = os.environ.get("GITHUB_TOKEN")
    
    org_name = os.environ.get("GITHUB_ORG")
    
    backup_dir = os.environ.get("BACKUP_DIR")
    
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    
    print(f"Starting backup for week: {start_of_week}")
    
    repos = get_github_repos(token, org_name)
    
    for repo in repos:
        repo_url = repo['clone_url']
        repo_name = repo['name']
        
        backup_path = os.path.join(backup_dir, repo_name, start_of_week.strftime("%Y-%m-%d"))
        
        clone_repo(repo_url, backup_path)
    
    delete_old_backups(backup_dir)
    
    print("Backup completed successfully!")

if __name__ == "__main__":
    main()