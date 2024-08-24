import requests
import pandas as pd

api_key = '1c23930e7943f34235c34619593256fb'
api_endpoint = 'https://api.elsevier.com/content/search/scopus'
query = (
    # 'AF-ID(60014340) OR '
    # 'AF-ID(60280373) OR '
    'AF-ID(60117285)'
)

params = {
    'query': query,
    'httpAccept': 'application/json',
    'count': 1,  
    'view': 'COMPLETE'  
}

headers = {
    'X-ELS-APIKey': api_key
}

response = requests.get(api_endpoint, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    
    total_results = int(data['search-results']['opensearch:totalResults'])
    print(f"Total number of results: {total_results}")

    entries = data['search-results']['entry']

    papers_info = []
    for entry in entries:
        title = entry.get('dc:title', 'No title available')
        authors = entry.get('dc:creator', 'No authors available')
        affiliation = entry.get('affiliation', [{'affilname': 'No affiliation available'}])[0]['affilname']
        publication_date = entry.get('prism:coverDate', 'No date available')
        source_title = entry.get('prism:publicationName', 'No source title available')
        doi = entry.get('prism:doi', 'No DOI available')
        
        papers_info.append({
            'Title': title,
            'Authors': authors,
            'Affiliation': affiliation,
            'Publication Date': publication_date,
            'Source Title': source_title,
            'DOI': doi
        })
    
    df = pd.DataFrame(papers_info)

#     df.to_excel('srm_ist_papers1.xlsx', index=False)
#     print("Data successfully saved to srm_ist_papers1.xlsx")

else:
    print(f"Failed to retrieve data: {response.status_code}, Reason: {response.reason}")
