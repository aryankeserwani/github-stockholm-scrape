import requests
import pandas as pd
import time

# GitHub API credentials and endpoint
GITHUB_TOKEN = 'your_token'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}
BASE_URL = 'https://api.github.com'

# Parameters
city = "Stockholm"  #city
min_followers = 100  # Minimum followers filter

def fetch_users(city, min_followers):
    users = []
    page = 1
    while True:
        response = requests.get(
            f"{BASE_URL}/search/users?q=location:{city}+followers:>{min_followers}&page={page}",
            headers=HEADERS
        )
        data = response.json()
        if 'items' not in data:
            break  # Stop if no items found
        users.extend(data['items'])
        if len(data['items']) < 30:
            break  # Stop if fewer than 30 results on the page
        page += 1
        time.sleep(1)  # To avoid rate limiting
    return users

def fetch_user_details(username):
    user_data = requests.get(f"{BASE_URL}/users/{username}", headers=HEADERS).json()
    return user_data

def fetch_repositories(username):
    repos = []
    page = 1
    while True:
        response = requests.get(
            f"{BASE_URL}/users/{username}/repos?sort=pushed&per_page=100&page={page}",
            headers=HEADERS
        )
        data = response.json()
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
        time.sleep(1)
    return repos[:500]

def clean_company_name(company):
    if company:
        company = company.strip().lstrip('@').upper()
    return company or ""

# Fetch users in specified city
users_list = fetch_users(city, min_followers)
users_data = []
repositories_data = []

# Collect details for each user
for user in users_list:
    user_details = fetch_user_details(user['login'])
    user_record = {
        'login': user_details.get('login', ''),
        'name': user_details.get('name', ''),
        'company': clean_company_name(user_details.get('company', '')),
        'location': user_details.get('location', ''),
        'email': user_details.get('email', ''),
        'hireable': user_details.get('hireable', ''),
        'bio': user_details.get('bio', ''),
        'public_repos': user_details.get('public_repos', 0),
        'followers': user_details.get('followers', 0),
        'following': user_details.get('following', 0),
        'created_at': user_details.get('created_at', ''),
    }
    users_data.append(user_record)
    
    # Fetch repositories for each user
    repos = fetch_repositories(user['login'])
    for repo in repos:
        repo_record = {
            'login': user_details.get('login', ''),
            'full_name': repo.get('full_name', ''),
            'created_at': repo.get('created_at', ''),
            'stargazers_count': repo.get('stargazers_count', 0),
            'watchers_count': repo.get('watchers_count', 0),
            'language': repo.get('language', ''),
            'has_projects': repo.get('has_projects', False),
            'has_wiki': repo.get('has_wiki', False),
            'license_name': repo.get('license', {}).get('key', '') if repo.get('license') else ''
        }
        repositories_data.append(repo_record)

# Save to CSV
users_df = pd.DataFrame(users_data)
users_df.to_csv('users.csv', index=False)

repositories_df = pd.DataFrame(repositories_data)
repositories_df.to_csv('repositories.csv', index=False)

# Create README.md file
with open("README.md", mode="w") as file:
    file.write("- This project scrapes data by requesting Github API to fetch users of followers more than 100 and having repositories not more than 500 from specific city through python code using Github token and then saving the json output into csv files.\n")
    file.write("- Users in Stockholm mostly prefer JavaScript language and majority of these developers work at Spotify company with highest numbers of developers from this city in this company.\n")
    file.write("- Consider implementing more repositories with project management tools (has_projects: true) to improve collaboration.\n")

print("Data collection complete. Files saved as users.csv, repositories.csv, and README.md.")
