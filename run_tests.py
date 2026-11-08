"""Runs every test through the pipeline and saves UNEDITED output.
  python run_tests.py            -> offline layer only (retrieval + safety flags), no API key needed
  python run_tests.py --llm      -> also calls the model (needs API key); outputs saved per case
"""
import json, sys, datetime
from core import *
use_llm = "--llm" in sys.argv
tag = sys.argv[sys.argv.index("--tag")+1] if "--tag" in sys.argv else "run"
tests = json.load(open("tests.json", encoding="utf-8"))
rows, md = [], [f"# Raw output ({tag}) - {datetime.datetime.now():%Y-%m-%d %H:%M}\nLLM called: {use_llm}\n"]
ok = 0
for t in tests:
    kb = [e["id"] for e in retrieve(t["input"])]
    fl = urgent_flags(t["input"])
    kb_ok = all(x in kb for x in t["expect_kb"])
    fl_ok = bool(fl) == t["expect_flag"]
    ok += kb_ok and fl_ok
    reply = None
    if use_llm:
        try: reply = llm(system_prompt(t["input"]), [{"role":"user","content":t["input"]}])
        except Exception as ex: reply = f"ERROR: {ex}"
    rows.append({**t,"retrieved":kb,"flags":fl,"kb_ok":kb_ok,"flag_ok":fl_ok,"reply":reply})
    md.append(f"## Case {t['id']} ({t['lang']})\n**Input:** {t['input']}\n\n**Retrieved:** {kb}  (expected {t['expect_kb']}) -> {'PASS' if kb_ok else 'FAIL'}\n\n**Safety flags:** {fl or 'none'} (expected {'some' if t['expect_flag'] else 'none'}) -> {'PASS' if fl_ok else 'FAIL'}\n")
    if t.get("trap"): md.append(f"**Trap:** {t['trap']}\n")
    if reply: md.append(f"**Model reply (unedited):**\n\n{reply}\n")
md.append(f"\n**Offline checks passed: {ok}/{len(tests)}**")
open(f"raw_outputs/{tag}.json","w",encoding="utf-8").write(json.dumps(rows,ensure_ascii=False,indent=1))
open(f"raw_outputs/{tag}.md","w",encoding="utf-8").write("\n".join(md))
print(f"{ok}/{len(tests)} passed offline checks")
for r in rows:
    if not (r["kb_ok"] and r["flag_ok"]): print("FAIL case", r["id"], r["lang"], "retrieved", r["retrieved"], "flags", bool(r["flags"]))
