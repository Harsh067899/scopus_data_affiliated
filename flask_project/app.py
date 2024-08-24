from flask import Flask, render_template, request, send_file
import requests
import pandas as pd
import io

app = Flask(__name__)

API_KEY = '1c23930e7943f34235c34619593256fb'
API_ENDPOINT = 'https://api.elsevier.com/content/search/scopus'

# Affiliation details
AFFILIATIONS = {
    '60014340': 'SRM Institute of Science and Technology',
    '60117285': 'SRM Institute of Science and Technology Ramapuram Campus',
    '60118182': 'SRM University-AP',
    '60110553': 'SRM University Delhi-NCR, Sonepat',
    '60117286': 'SRM Institute of Science and Technology, NCR Campus',
    '60114400': 'Valliammai Engineering College',
    '60271883': 'SRM Dental College',
    '60079447': 'SRM Group Of Educational Institutions',
    '60120782': 'SRM institute of science and technology, Vadapalani campus',
    '60279986': 'SRM Kattankulathur Dental College and Hospital',
    '60105678': 'S.R.M. Arts & Science College',
    '60280373': 'SRM Institute of Science and Technology Tiruchirappalli Campus',
    '60118184': 'SRM University Sikkim'
}

def fetch_papers(affiliation_ids, count):
    query = ' OR '.join([f'AF-ID("{aff_id}")' for aff_id in affiliation_ids])

    params = {
        'query': query,
        'httpAccept': 'application/json',
        'count': count,
        'view': 'COMPLETE'
    }

    headers = {
        'X-ELS-APIKey': API_KEY
    }

    response = requests.get(API_ENDPOINT, headers=headers, params=params)

    # Extract remaining request limit from headers
    remaining_requests = response.headers.get('X-RateLimit-Remaining', 'Unknown')
    
    if response.status_code == 200:
        data = response.json()
        total_results = int(data['search-results']['opensearch:totalResults'])

        entries = data['search-results']['entry']

        papers_info = []
        for entry in entries:
            title = entry.get('dc:title', 'No title available')
            authors = entry.get('dc:creator', 'No authors available')
            publication_date = entry.get('prism:coverDate', 'No date available')
            source_title = entry.get('prism:publicationName', 'No source title available')
            doi = entry.get('prism:doi', 'No DOI available')

            # Extracting affiliations and institutions
            affiliation_list = entry.get('affiliation', [])
            institutions = ', '.join([affil.get('affilname', 'No affiliation available') for affil in affiliation_list])
            affiliations = ', '.join([affil.get('affilname', 'No affiliation available') for affil in affiliation_list])

            papers_info.append({
                'Title': title,
                'Authors': authors,
                'Affiliations': affiliations,
                'Institutions': institutions,
                'Publication Date': publication_date,
                'Source Title': source_title,
                'DOI': doi
            })

        return papers_info, total_results, remaining_requests

    else:
        print(f"Failed to retrieve data: {response.status_code}, Reason: {response.reason}")
        return [], 0, 'Unknown'

@app.route('/', methods=['GET', 'POST'])
def index():
    papers_info = []
    total_results = 0
    download_url = None
    remaining_requests = 'Unknown'

    if request.method == 'POST':
        selected_affiliations = [aff_id for aff_id in AFFILIATIONS.keys() if request.form.get(aff_id)]
        count = int(request.form.get('count', 25))
        papers_info, total_results, remaining_requests = fetch_papers(selected_affiliations, count)

        # Save to Excel in memory
        output = io.BytesIO()
        df = pd.DataFrame(papers_info)
        df.to_excel(output, index=False)
        output.seek(0)
        download_url = '/download_excel'

        # Save the Excel file to disk for download
        with open('srm_ist_papers.xlsx', 'wb') as f:
            f.write(output.getvalue())

    return render_template('index.html', affiliations=AFFILIATIONS, papers=papers_info, total=total_results, download_url=download_url, remaining_requests=remaining_requests)

@app.route('/download_excel')
def download_excel():
    return send_file('srm_ist_papers.xlsx', as_attachment=True, download_name='srm_ist_papers.xlsx')

if __name__ == '__main__':
    app.run(debug=True)
