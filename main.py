import os
import bibtexparser
import json
import requests
from nameparser import HumanName

# urlrepo = "https://github.com/usc-isi-i2/kgtk"
urlrepo = "https://github.com/KnowledgeCaptureAndDiscovery/somef"

os.system("rm -r tmp/*")  # remove all files in tmp
os.system("somef configure -a")  # configure somef
os.system(
    f"somef describe -r {urlrepo} -o tmp/someftmp.json -p --keep_tmp tmp/somef")  # execute somef

# get the path of the repo in tmp
path = 'tmp/somef/'
path += os.listdir(path)[0] + '/'
path += os.listdir(path)[0]
os.system(
    f'inspect4py -i {path} -f --output_dir tmp/inspect4pytmp --software_invocation')  # execute inspect4py


with open('tmp/someftmp.json') as f:
    somef = json.load(f)
with open('langs.json') as f:
    langs = json.load(f)
with open('licensesspdx.json') as f:
    lin = json.load(f)

citations = somef['citation']

# Get all the users that have contributed to the repo releases
nom_repo = somef['name']['excerpt']
nom_owner = somef['owner']['excerpt']

users_contributors = []

headers = {
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'Authorization': f'Bearer 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'
}
resp = requests.get(
    f'https://api.github.com/repos/{nom_owner}/{nom_repo}/contributors', headers=headers)

if resp.status_code == 200:
    for user in resp.json():
        if user['type'] == 'User':
            users_contributors.append(user)

graphql_query = """
query($ids:[ID!]!) {
	nodes(ids:$ids) {
    	... on User {
        		login
     		name
    	}
	}
}
"""

variables = {
    "ids": [user['node_id'] for user in users_contributors]
}

request = requests.post('https://api.github.com/graphql',
                        json={'query': graphql_query, 'variables': variables}, headers=headers)
if request.status_code == 200:
    rjson = request.json()
    # añadir el nombre al json de los usuarios identificados por login en users_contributors
    for user in rjson['data']['nodes']:
        for u in users_contributors:
            if user['login'] == u['login']:
                u['name'] = user['name']
# users = []
# for excerpt in somef['releases']['excerpt']:
#     res = requests.get(f'https://api.github.com/users/{excerpt["authorName"]}')
#     if res.status_code == 200:
#         user = res.json()
#         human = HumanName(user['name'])
#         human.nickname = user['login']
#     if human not in users:
#         users.append(human)
# print(len(users))

articulos = []
# Get all the articles cited in the repo
for citation in citations:
    art = citation['excerpt']
    bib_database = bibtexparser.loads(art)
    for bib in bib_database.entries:
        if bib["ENTRYTYPE"] == "article" and bib not in articulos:
            articulos.append(bib)

# Get all the languages used in the repo
lngs = []
for lang in somef['languages']['excerpt']:
    for l in langs["results"]["bindings"]:
        if lang == l['lenLabel']['value']:
            lngs.append(l)

print(len(articulos))

# Get the license
licenseurl = somef['license']['excerpt']["url"]
request = requests.get(licenseurl)
license = request.json()
for l in lin["results"]["bindings"]:
    if license["spdx_id"] == l['spdx']['value']:
        license["wiki"] = l
print(license)
