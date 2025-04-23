import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
import sys

import requests

MY_TEAM_ID = sys.argv[1]
HTTP_CACHE_DIR = Path("http_cache")

def stable_str_hash(in_val: str) -> str:
    return hex(int(hashlib.md5(in_val.encode("utf-8")).hexdigest(), 16))[2:]

def get_json(url: str) -> dict:
    HTTP_CACHE_DIR.mkdir(exist_ok=True)

    cache = {}
    cache_file_path = HTTP_CACHE_DIR / f"{stable_str_hash(url)}.json"
    try:
        with open(cache_file_path) as cache_file:
            cache = json.load(cache_file)
    except FileNotFoundError:
        pass

    # Return from cache if the cache entry is less than 5 minutes old
    now = datetime.now(timezone.utc)
    if (
            url in cache and
            "__archived_at" in cache[url] and
            cache[url]["__archived_at"] > (now - timedelta(minutes=5)).isoformat()
    ):
        return cache[url]

    data = requests.get(url).json()
    cache[url] = data
    cache[url]["__archived_at"] = now.isoformat()
    with open(cache_file_path, "w") as cache_file:
        json.dump(cache, cache_file)

    return data

def main():

    csv_file = open("full_league.csv","a")

    team_obj = get_json(f"https://mmolb.com/api/team/{MY_TEAM_ID}")
    print(f"Processing {team_obj['Emoji']} {team_obj['Location']} {team_obj['Name']}")

    for player in team_obj["Players"]:
        try:
            player_obj = get_json(f"https://mmolb.com/api/player/{player['PlayerID']}")
        except:
            # idk why this is happening
            continue

        try:
            # I'm pretty sure IDs are lexicographically ordered, so we want the
            # maximum value to get stats for the latest season
            stats_obj = player_obj["Stats"][max(player_obj["Stats"].keys())]
        except ValueError:
            csv_file.write(f"{player['FirstName']} {player['LastName']}| {player['Position']}||||||||||{team_obj['Location']} {team_obj['Name']}\n")
            continue

        singles = stats_obj.get("singles", 0)
        doubles = stats_obj.get("doubles", 0)
        triples = stats_obj.get("triples", 0)
        home_runs = stats_obj.get("home_runs", 0)
        hits = singles + doubles + triples + home_runs
        bb = stats_obj.get("walked", 0)
        hbp = stats_obj.get("hit_by_pitch", 0)
        earned_runs = stats_obj.get("earned_runs", 0)

        try:
            ab = stats_obj["at_bats"]
        except KeyError:
            ba_str = "|"
        else:
            ba = hits / ab
            ba_str = f"{ab}|{ba:.3f}"

        try:
            pa = stats_obj["plate_appearances"]
            ab = stats_obj["at_bats"]
        except KeyError:
            ops_str = "|||"
        else:
            obp = (hits + bb + hbp) / pa
            slg = (singles + 2 * doubles + 3 * triples + 4 * home_runs) / ab
            ops = obp + slg
            pa_str = dot_format(pa)
            ops_str = f"{obp:.3f}|{slg:.3f}|{pa_str}|{ops:.3f}"

        try:
            ip = stats_obj["batters_faced"] / 3
        except KeyError:
            era_str = "|"
        else:
            era = 9 * earned_runs / ip
            ip_str = dot_format(ip)
            era_str = f"{era:.2f}|{ip_str}"

        stats_str = "|".join(s for s in [era_str, ba_str, ops_str])
        if stats_str:
            csv_file.write(f"{player['FirstName']} {player['LastName']}| {player['Position']}| {stats_str}||{team_obj['Location']} {team_obj['Name']}\n")


    csv_file.close()


def dot_format(in_val: float) -> str:
    ip_whole = int(in_val)
    ip_remainder = int((in_val - ip_whole) / 3 * 10)
    if ip_remainder == 0:
        ip_str = f"{ip_whole}"
    else:
        ip_str = f"{ip_whole}.{ip_remainder}"
    return ip_str


if __name__ == '__main__':
    main()

