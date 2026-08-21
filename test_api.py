#!/usr/bin/env python
import requests
import json

body = {
    'percentile': 85,
    'category_code': 'GOPENH',
    'preferred_districts': [],
    'preferred_branch_codes': [],
    'max_reach': 100,
    'max_match': 100,
    'max_safe': 100
}

response = requests.post('http://localhost:8000/api/v1/generate-list', json=body)
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Reach: {data["reach_count"]}, Match: {data["match_count"]}, Safe: {data["safe_count"]}, Explore: {data["explore_count"]}')
    if data['entries']:
        print('\nFirst 3 entries:')
        for entry in data['entries'][:3]:
            print(f'  {entry["college_name"]} - {entry["branch_name"]} ({entry["classification"]})')
else:
    print(f'Error: {response.text}')
