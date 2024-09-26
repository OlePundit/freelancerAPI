import requests
import pandas as pd

# Fetch projects data
url = "https://www.freelancer.com/api/projects/0.1/projects/active/?compact=&limit=10&min_avg_hourly_rate=8&min_avg_price=25&job_details=true&query=web%20developer&jobs%5B%5D=3,13,38,113,137,323,602,669,759,1042"
headers = {'freelancer-oauth-v1': '**********'}
response = requests.request("GET", url, headers=headers)
data = response.json()


# Tokenization and generation helper function
def generate_proposal(job_names, title):
    # Combine job names and description into a prompt for LLaMA
    proposal = f"I am interested in helping you with your project on {title}. I am an experienced full stack developer with years of experience and skills across various tech stacks and frameworks such as {job_names}. I can work with both SQL and NoSQL environments, with skills and expertise in PostgreSQL, MySQL, and eloquent-orm. I can also perform system operations in Apache and Nginx. I build RESTful apps and I am familiar with git version control, CI/CD, and agile methodologies. I can work well as a team, or alone under minimal supervision. I possess excellent communication and interpersonal skills. I am eager to work with you."
    
    return proposal


# Extract data into DataFrame
extracted_data = []
for project in data['result']['projects']:
    project_id = project['id']
    budget_min = project['budget'].get('minimum', None)
    seo_url = project['seo_url']
    job_names = [job['name'] for job in project.get('jobs', [])]  # Get 'name' from each job in 'jobs'
    job_ids = [job['id'] for job in project.get('jobs', [])]

    title=project['title']
    
    # Generate proposal using Llama
    proposal = generate_proposal(", ".join(job_names), title)

    
    extracted_data.append({
        "id": project_id, 
        "budget_minimum": budget_min, 
        "seo_url": seo_url, 
        "proposal": proposal,  # Add the generated proposal to the DataFrame
        "title":title,
        "job_ids":job_ids
    })

df = pd.DataFrame(extracted_data)

# Add skills
url = 'https://www.freelancer.com/api/users/0.1/self/jobs' 
headers = {
    'Content-Type': 'application/json',
    'freelancer-oauth-v1': '***************'
}

def add_skill(row):
    payload={
        "jobs[]": row['job_ids']  # Use 'jobs[]' instead of 'job_ids'
    }

    response = requests.post(url, headers=headers, json=payload)
    print(f"JOB IDS: {row['job_ids']}, Status Code: {response.status_code}, Response: {response.text}")

df.apply(add_skill, axis=1)

# Function to send a POST request for each row
url_bid = 'https://www.freelancer.com/api/projects/0.1/bids/?compact=' 
headers = {
    'Content-Type': 'application/json',
    'freelancer-oauth-v1': '*****************'
}

def submit_bid(row):
    payload = {
        "project_id": row['id'],
        "bidder_id": 24319783,  # Replace with the actual bidder_id
        "amount": row['budget_minimum'],
        "period": 7,
        "milestone_percentage": 100,
        "description": row['proposal']  # Use the generated proposal as the description
    }
    
    response = requests.post(url_bid, headers=headers, json=payload)
    print(f"Project ID: {row['id']}, Status Code: {response.status_code}, Response: {response.text}")

# Loop through each row in the DataFrame and execute the bid request
df.apply(submit_bid, axis=1)
