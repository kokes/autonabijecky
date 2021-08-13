import json
import logging
import os
from urllib.request import urlopen, Request

tdir = "stanice"

# IDs for diffs: .results.keys()
def pre():
    url = "https://chargepre.smatrics.com/cs/map/pois?operator%5B%5D=CZ*PRE"
    req = Request(url)
    req.add_header("Referer", "https://chargepre.smatrics.com/cs/")
    with urlopen(req) as r:
        return json.load(r)


# IDs for diffs: customID
def cez():
    url = "https://www.elektromobilita.cz/cs/charging-stations-markery-pay.json"
    with urlopen(url) as r:
        return json.load(r)


# IDs for diffs: id
def eon():
    url = "https://www.eon-drive.cz/api/v1/locations"
    with urlopen(url) as r:
        data = json.load(r)

    data = [j for j in data if j["country_code"] == "CZ"]
    return data


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    os.makedirs(tdir, exist_ok=True)

    funcs = [pre, cez, eon]

    for func in funcs:
        tfn = os.path.join(tdir, func.__name__ + ".json")
        data = func()
        # TODO: diff with existing data
        with open(tfn, "w", encoding="utf-8") as fw:
            json.dump(data, fw, indent=2, ensure_ascii=False, sort_keys=True)
