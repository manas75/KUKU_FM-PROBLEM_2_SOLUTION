# Nyaya Saathi - grounded AI legal helper for India (Problem 2)
## Run
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key        # or: LLM_PROVIDER=openai OPENAI_API_KEY=...
streamlit run app.py
## Swap the model (no code change)
LLM_PROVIDER=anthropic|openai   LLM_MODEL=<name>   LLM_BASE_URL=<any OpenAI-compatible endpoint>
## Reproduce the test outputs
python run_tests.py --tag offline            # retrieval + safety flags, no key needed
python run_tests.py --llm --tag with_model   # full run incl. model replies (needs key)
## Files
core.py (KB, retrieval, safety flags, prompt, model adapter) | app.py (UI) | tests.json | run_tests.py | raw_outputs/
## Limits
Covers 4 problem types. KB is hand-written and must be verified against indiacode.nic.in before real use. Not legal advice.
