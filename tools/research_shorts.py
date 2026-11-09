"""Исследование вирусных Shorts в нише EV (запускается в GitHub Actions, там открыт YouTube).
1) поиск по запросам → кандидаты; 2) для каждого канала — медиана просмотров последних 30 shorts;
3) outlier = views / median; 4) для топ-40 — хук: авто-субтитры первых 3 сек.
Результат: research/shorts.json
"""
import json, os, statistics, subprocess, sys, glob

QUERIES = [
    "электромобиль зарядка", "зарядка электромобиля дома", "электромобиль зимой",
    "электромобиль расход", "зарядная станция электромобиль", "китайский электромобиль",
    "zeekr", "электромобиль минусы", "электромобиль vs бензин", "электрокар беларусь",
    "электромобиль из китая", "переходник gbt type2",
]
YT = [sys.executable, "-m", "yt_dlp", "--quiet", "--no-warnings", "--ignore-errors"]

def run(args):
    r = subprocess.run(YT + args, capture_output=True, text=True, timeout=600)
    return r.stdout

def flat(url, n):
    out = run(["--flat-playlist", "--playlist-end", str(n), "-J", url])
    try:
        return json.loads(out).get("entries") or []
    except Exception:
        return []

cands = {}
for q in QUERIES:
    for e in flat(f"ytsearch60:{q} #shorts", 60):
        if not e or not e.get("id"):
            continue
        dur = e.get("duration") or 0
        if dur and dur > 75:
            continue
        cands[e["id"]] = {
            "id": e["id"], "title": e.get("title"), "views": e.get("view_count") or 0,
            "channel": e.get("channel") or e.get("uploader"), "channel_id": e.get("channel_id"),
            "channel_url": e.get("channel_url") or e.get("uploader_url"), "duration": dur, "query": q,
        }

# медианы по каналам
by_ch = {}
for c in cands.values():
    if c["channel_url"]:
        by_ch.setdefault(c["channel_url"], []).append(c)
medians = {}
for url, items in sorted(by_ch.items(), key=lambda kv: -max(i["views"] for i in kv[1]))[:60]:
    ents = flat(url.rstrip("/") + "/shorts", 30)
    vs = [e.get("view_count") for e in ents if e and e.get("view_count")]
    if len(vs) >= 5:
        medians[url] = statistics.median(vs)

rows = []
for c in cands.values():
    m = medians.get(c["channel_url"])
    if m and c["views"]:
        c["median"] = m
        c["outlier"] = round(c["views"] / m, 2)
        rows.append(c)
rows.sort(key=lambda r: (-r["outlier"], -r["views"]))

# хуки (первые 3 сек речи) для топ-40 по outlier при views >= 50k
top = [r for r in rows if r["views"] >= 50000][:40]
os.makedirs("research/subs", exist_ok=True)
for r in top:
    run(["--skip-download", "--write-auto-subs", "--write-subs", "--sub-langs", "ru.*,ru",
         "--sub-format", "json3", "-o", f"research/subs/{r['id']}", f"https://www.youtube.com/shorts/{r['id']}"])
    files = glob.glob(f"research/subs/{r['id']}*.json3")
    words = []
    if files:
        try:
            d = json.load(open(files[0], encoding="utf-8"))
            for ev in d.get("events", []):
                t = ev.get("tStartMs", 0)
                if t > 3500:
                    break
                for s in ev.get("segs", []) or []:
                    words.append(s.get("utf8", ""))
        except Exception:
            pass
    r["hook_spoken"] = " ".join("".join(words).split())

os.makedirs("research", exist_ok=True)
json.dump({"candidates": len(cands), "channels_with_median": len(medians), "rows": rows[:200], "top": top},
          open("research/shorts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("candidates", len(cands), "rows", len(rows), "top", len(top))
