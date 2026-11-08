"""Core logic for Nyaya Saathi (no UI, testable)."""
import os, re

KB = [
 {"id":"CPA-69","topics":["refund","consumer","product","service","defect","deficiency","online","order","flipkart","amazon","paisa wapas"],
  "text":"Consumer Protection Act, 2019, s.69: a consumer complaint should be filed within 2 years of the cause of action."},
 {"id":"CPA-FORUM","topics":["refund","consumer","product","service","defect","deficiency","online","order","flipkart","amazon","paisa wapas"],
  "text":"Consumer complaints go to the District Commission (claims up to Rs 50 lakh), State Commission (Rs 50 lakh-2 crore) or National Commission (above Rs 2 crore), by value of goods/services paid. Can be filed online on e-Daakhil. National Consumer Helpline: 1915. A prior legal notice is customary but not mandatory."},
 {"id":"LIMIT-1963","topics":["deposit","salary","money","loan","recover","court","suit","முன்பணம்","জামানত"],
  "text":"Limitation Act, 1963: most civil suits to recover money must be filed within 3 years of the right arising. Check the exact starting date with a lawyer."},
 {"id":"RENT-STATE","topics":["deposit","landlord","tenant","rent","evict","flat","house","मकान मालिक","किरायेदार","जमानत","முன்பணம்","வீட்டு உரிமையாளர்","জামানত","বাড়িওয়ালা"],
  "text":"Rent and security deposit rules are mainly STATE law (state Rent Control Acts). The Model Tenancy Act, 2021 (deposit cap of 2 months' rent for residential) is a central model that applies only in states that adopted it. The rent agreement terms matter most."},
 {"id":"NI-138","topics":["cheque","bounce","dishonour","138","चेक"],
  "text":"Negotiable Instruments Act s.138 (cheque dishonour): written demand notice must be sent within 30 days of getting the bank's return memo; drawer has 15 days to pay; if unpaid, complaint must be filed within 1 month after that period ends. These deadlines are strict."},
 {"id":"WAGES","topics":["salary","wages","unpaid","employer","job","termination","labour","तनख्वाह","वेतन","சம்பளம்","বেতন"],
  "text":"Unpaid wages can be raised with the state Labour Commissioner / wage authority. Which statute applies (Payment of Wages Act, 1936 or the newer Code on Wages, 2019) depends on notification status and the worker's category - verify. Keep appointment letter, payslips, bank statements and chats as proof."},
 {"id":"LEGAL-AID","topics":["legal aid","free lawyer","afford","poor","cannot pay"],
  "text":"Legal Services Authorities Act, 1987: free legal aid is available to eligible people (e.g. women, children, SC/ST, low-income, victims of trafficking, persons in custody) via District/State Legal Services Authorities. NALSA helpline: 15100."},
]

URGENT_PATTERNS = {
 r"\b(arrest|police (called|came|station)|fir|jail|custody|summons|warrant)\b":
  "Police/criminal matters are time-critical. Please speak to a criminal lawyer or the free legal-aid authority (NALSA 15100) immediately.",
 r"(\b(beat|violence|threat|abuse|dowry|harass|stalk|assault)\w*|\b(maar|peet|marpit|dhamki|hinsa|torture)\w*|मार|हिंसा|धमकी)":
  "If you are in danger, call 112 now. Women's helpline: 181. A lawyer or legal-aid authority should handle this.",
 r"\b(court (date|hearing|notice)|ex.?parte|decree|attachment)\b":
  "A court notice has a hard date. Do not ignore it; get a lawyer or legal aid before the date.",
 r"\b(property dispute|inheritance|partition|will (deed|dispute)|child custody|divorce)\b":
  "This area is complex and high-stakes; this tool only gives orientation, not a plan. Please consult a lawyer.",
}

def retrieve(text, k=4):
    t = text.lower()
    scored = [(sum(w.lower() in t for w in e["topics"]), e) for e in KB]
    return [e for s, e in sorted(scored, key=lambda x: -x[0]) if s > 0][:k]

def urgent_flags(text):
    return [m for p, m in URGENT_PATTERNS.items() if re.search(p, text.lower())]

def llm(system, messages):
    provider = os.getenv("LLM_PROVIDER", "anthropic")
    model = os.getenv("LLM_MODEL", "claude-sonnet-4-6" if provider == "anthropic" else "gpt-4o-mini")
    if provider == "anthropic":
        import anthropic
        r = anthropic.Anthropic().messages.create(model=model, max_tokens=1200, system=system, messages=messages)
        return r.content[0].text
    from openai import OpenAI
    c = OpenAI(base_url=os.getenv("LLM_BASE_URL") or None)
    r = c.chat.completions.create(model=model, messages=[{"role":"system","content":system}]+messages)
    return r.choices[0].message.content

BASE = """You are Nyaya Saathi, a legal information assistant for ordinary people in India. You are NOT a lawyer.
RULES
1. Reply in the language and script the user writes in (Hindi, Hinglish, English, Tamil, Bengali, etc.). Use plain words, short sentences.
2. GROUNDING: You may state specific laws, sections, deadlines, amounts or forum names ONLY if they appear in the LEGAL NOTES below; cite their id like [CPA-69]. For anything else say "general understanding, please verify". Never invent section numbers or case names. If a user asks about a section you cannot find in the notes, say you cannot verify it. If unsure, say "I don't know".
3. Never invent facts about the user's situation. Ask at most 2 short questions at a time (who, what, when, how much, what proof, what has been tried).
4. Say plainly when a real lawyer or legal aid is needed (criminal case, court dates, large amounts, property, family disputes, anything unclear).
5. Give practical next steps: collect proof, send a written demand/notice, use the right forum. Mention free options (legal aid, consumer helpline) where relevant.
6. Never promise an outcome.
"""

def system_prompt(user_text, mode="Help me with my problem"):
    notes = retrieve(user_text)
    ctx = "\n".join(f"[{e['id']}] {e['text']}" for e in notes) or "(no matching notes - answer only in general terms and recommend a lawyer for specifics)"
    extra = ""
    if mode.startswith("Practise"):
        extra = "\nMODE: Role-play the opposing party (landlord/employer/seller) realistically but fairly so the user can practise. After 3-4 exchanges step out and give feedback on their strongest and weakest points."
    return BASE + extra + "\nLEGAL NOTES (the only citable sources):\n" + ctx

TASKS = {
 "Case summary":"From the whole conversation produce: 1) What happened (dated list), 2) Who is involved, 3) Proof the user HAS, 4) Proof still MISSING, 5) What they want. Mark anything not stated as 'not provided'. Do not guess.",
 "Draft legal notice":"Draft a polite but firm legal notice from the user to the other party using only facts the user stated. Use [PLACEHOLDERS] for missing names/dates/amounts. Give a clear demand and a reasonable deadline (e.g. 15 days). Cite law only from LEGAL NOTES. End with a reminder to have a lawyer review before sending.",
}
