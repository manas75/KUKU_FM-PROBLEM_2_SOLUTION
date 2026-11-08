"""Nyaya Saathi UI.  streamlit run app.py"""
import os, streamlit as st
from core import llm, system_prompt, urgent_flags, TASKS

st.set_page_config(page_title="Nyaya Saathi", page_icon="⚖️")
st.title("⚖️ Nyaya Saathi")
st.caption("Legal *information* for everyday problems in India (rent deposit, refunds, unpaid salary, cheque bounce). Not a lawyer. Never share Aadhaar or bank numbers.")
mode = st.sidebar.radio("Mode", ["Help me with my problem", "Practise: AI plays the other side"])
st.sidebar.markdown("**Covers:** rent/deposit, consumer refunds, unpaid salary, cheque bounce.\n\n**Does not cover:** criminal, family, property, tax, court representation.")
st.sidebar.markdown(f"Model: `{os.getenv('LLM_MODEL','default')}` via `{os.getenv('LLM_PROVIDER','anthropic')}`")
st.session_state.setdefault("msgs", [])
for m in st.session_state.msgs: st.chat_message(m["role"]).write(m["content"])
hist = lambda: " ".join(m["content"] for m in st.session_state.msgs if m["role"] == "user")
c1, c2 = st.columns(2)
task = "Case summary" if c1.button("📋 Build my case summary") else "Draft legal notice" if c2.button("✉️ Draft a legal notice") else None
if p := st.chat_input("Tell me what happened, in any language..."):
    st.session_state.msgs.append({"role":"user","content":p}); st.chat_message("user").write(p)
    for f in urgent_flags(p): st.warning(f)
    with st.spinner("Thinking..."): r = llm(system_prompt(hist(), mode), st.session_state.msgs)
    st.session_state.msgs.append({"role":"assistant","content":r}); st.chat_message("assistant").write(r)
if task and st.session_state.msgs:
    with st.spinner("Preparing..."):
        out = llm(system_prompt(hist(), mode), st.session_state.msgs + [{"role":"user","content":TASKS[task]}])
    st.subheader(task); st.markdown(out)
    st.download_button("Download", out, file_name=f"{task.lower().replace(' ','_')}.txt")
