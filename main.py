import os
import bibtexparser
import json
import requests

urlrepo = "https://github.com/usc-isi-i2/kgtk"

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

articulos = []
# Get all the articles cited in the repo
for citation in citations:
    art = citation['excerpt']
    bib_database = bibtexparser.loads(art)
    for bib in bib_database.entries:
        if bib["ENTRYTYPE"] == "article" and bib not in articulos:
            articulos.append(bib)

# Get all the users that have contributed to the repo releases
users = []
for excerpt in somef['releases']['excerpt']:
    if excerpt['authorName'] not in users:
        users.append(excerpt['authorName'])
print(len(users))

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
