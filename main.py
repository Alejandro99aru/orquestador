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

users = []
resp = requests.get(
    f'https://api.github.com/repos/{nom_owner}/{nom_repo}/contributors')
for user in resp.json():
    if user['type'] == 'User':
        resp = requests.get(f'https://api.github.com/users/{user["login"]}')
        if resp.status_code == 200:
            userj = resp.json()
            human = HumanName(userj['name'])
            human.nickname = user['login']
            if human not in users:
                users.append(human)
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
