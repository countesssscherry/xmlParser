from flask import Flask, send_from_directory, request
import collections
import pandas as pd

import xml.etree.ElementTree as ET

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = collections.defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['text'] = text
        else:
            d[t.tag] = text
    return d


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

@app.route('/', methods=['POST'])
def hello():
    """Return a parsed xml file in html table"""

    s = request.stream.read()

    tree = ET.fromstring(s)
    res = etree_to_dict(tree)
    print(res.keys())
    res = res[list(res.keys())[0]]
    res = res[list(res.keys())[0]]
    res = [flatten(r) for r in res]
    
    df = pd.DataFrame(res).to_html('temp.html')
    
    return send_from_directory('','temp.html')


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. You
    # can configure startup instructions by adding `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
