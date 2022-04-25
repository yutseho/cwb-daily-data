import codecs
import json
import os
from bs4 import BeautifulSoup

html_doc = """
<option value="CCCCCC_測站_1.0m">CCCCCC_測站</option>
"""

soup = BeautifulSoup(html_doc, 'html.parser')
option_tags = soup.find_all('option')

data = {}
if os.path.exists("stations.json"):
    with open("stations.json", encoding="utf-8-sig") as f:
        data = json.load(f)

with open("stations.json", 'w', encoding="utf-8-sig") as f:
    for tag in option_tags:
        row = tag.get('value')
        strs = row.split('_')
        if len(strs)!=3:
            print("unknown str: {}".format(row))
            exit()

        new_obj = {
            strs[0]:
            {
                "altitude": float(strs[2][:-1]),
                "name": strs[1],
            }
        }
        data.update(new_obj)

    json.dump(data, f, ensure_ascii=False, indent=4)
