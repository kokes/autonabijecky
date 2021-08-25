import hashlib
import json
import logging
import os
from urllib.request import urlopen, Request

tdir = "stanice"

# "csStatus": "under_construction"... resolve?
def pre():
    url = "https://chargepre.smatrics.com/cs/map/pois?operator%5B%5D=CZ*PRE"
    req = Request(url)
    req.add_header("Referer", "https://chargepre.smatrics.com/cs/")
    with urlopen(req) as r:
        raw = json.load(r)

    # TODO: dataclass for this? or maybe wrap in a helper that takes arguments of nameID, idID
    # and does the rest automatically
    return {
        # hmmm, tady se budou přepisovat přes sebe, protože PRE má víc nabíječek na jednom místě
        # v různých klíčích, ale se stejným csId... ale já to chci mít per místo
        el["csId"]: {
            "name": el["csName"],
            "sha1": hashlib.sha1(json.dumps(el).encode()).hexdigest(),
            "station": el,
        }
        for el in raw["results"].values()
    }


def cez():
    url = "https://www.elektromobilita.cz/cs/charging-stations-markery-pay.json"
    with urlopen(url) as r:
        raw = json.load(r)

    return {
        el["customID"]: {
            "name": el["name"],
            "sha1": hashlib.sha1(json.dumps(el).encode()).hexdigest(),
            "station": el,
        }
        for el in raw
    }


def eon():
    url = "https://www.eon-drive.cz/api/v1/locations"
    with urlopen(url) as r:
        data = json.load(r)

    data = [j for j in data if j["country_code"] == "CZ"]
    # musime umazat informace o tom, jestli se zrovna nabiji
    for station in data:
        station["last_updated"] = "RESET"
        for ev in station["evses"]:
            ev["status"] = "RESET"
            ev["last_updated"] = "RESET"

    return {
        el["id"]: {
            "name": el["name"],
            "sha1": hashlib.sha1(json.dumps(el).encode()).hexdigest(),
            "station": el,
        }
        for el in data
    }


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    os.makedirs(tdir, exist_ok=True)

    funcs = [pre, cez, eon]
    changelog = []
    stats = [0, 0, 0]
    total = 0

    for func in funcs:
        tfn = os.path.join(tdir, func.__name__ + ".json")
        existing = dict()
        if os.path.isfile(tfn):
            with open(tfn, "rt", encoding="utf-8") as f:
                existing = json.load(f)
        new_data = func()
        total += len(new_data)

        old_ids = set(existing.keys())
        new_ids = set(new_data.keys())

        for added in new_ids - old_ids:
            changelog.append(f"Nová: {func.__name__.upper()} {new_data[added]['name']}")
            stats[0] += 1

        for deleted in old_ids - new_ids:
            changelog.append(
                f"Zrušená: {func.__name__.upper()} {existing[deleted]['name']}"
            )
            stats[1] += 1

        for sid in old_ids & new_ids:
            if existing[sid]["sha1"] != new_data[sid]["sha1"]:
                changelog.append(
                    f"Změněná: {func.__name__.upper()} {new_data[sid]['name']}"
                )
                stats[2] += 1

        with open(tfn, "w", encoding="utf-8") as fw:
            json.dump(new_data, fw, indent=2, ensure_ascii=False, sort_keys=True)

    if len(changelog) > 0:
        print(
            f"Nové: {stats[0]}, zrušené: {stats[1]}, změněné: {stats[2]}. Celkem: {total}"
        )
        print("\n".join(sorted(changelog)))
