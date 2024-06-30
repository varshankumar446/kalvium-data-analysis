import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import json

# URL of the website containing election results
url = "https://results.eci.gov.in/PcResultGenJune2024/partywisewinresultState-369.htm"

# Fetch the HTML content
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Initialize list to store the data
data = []

# Find the table containing the election results
table = soup.find('table', {'class': 'table table-striped table-bordered'})

# Check if table is found
if table:
    for row in table.find_all('tr')[1:]:  # Skip header row
        cols = row.find_all('td')
        if len(cols) > 3:  # Adjust this based on actual number of columns
            constituency = cols[1].text.strip()
            candidate = cols[2].text.strip()
            try:
                votes = int(cols[3].text.strip().replace(',', ''))
            except ValueError:
                votes = None  # Handle non-numeric values gracefully
            data.append([constituency, candidate, votes])
else:
    print("Table not found on the webpage.")

# Create a DataFrame
df = pd.DataFrame(data, columns=['Constituency', 'Candidate', 'Votes'])

# Drop rows where votes are None
df.dropna(subset=['Votes'], inplace=True)

# Save the DataFrame to an Excel file (.xlsx)
df.to_excel('lok_sabha_results.xlsx', index=False, engine='openpyxl')

# Load the scraped data
df = pd.read_excel('lok_sabha_results.xlsx', engine='openpyxl')

# Example insights:
# 1. Total number of constituencies
total_constituencies = df['Constituency'].nunique()

# 2. Total votes per candidate
total_votes_per_candidate = df.groupby('Candidate')['Votes'].sum().reset_index()

# 3. Top 10 candidates with the highest votes
top_10_candidates = df.nlargest(10, 'Votes')

# 4. Constituency with the highest voter turnout
highest_voter_turnout = df.loc[df['Votes'].idxmax()]

# Plot total votes per candidate
plt.figure(figsize=(10, 6))
plt.bar(total_votes_per_candidate['Candidate'], total_votes_per_candidate['Votes'])
plt.xlabel('Candidate')
plt.ylabel('Total Votes')
plt.title('Total Votes per Candidate')
plt.xticks(rotation=90)
plt.show()

# Compile the insights into a report
report = {
    'Total Constituencies': total_constituencies,
    'Total Votes Per Candidate': total_votes_per_candidate.to_dict('records'),
    'Top 10 Candidates': top_10_candidates.to_dict('records'),
    'Constituency with Highest Voter Turnout': highest_voter_turnout.to_dict()
}

# Save the report to a file
with open('election_report.json', 'w') as f:
    json.dump(report, f, indent=4)

print("Report generated and saved as election_report.json")
