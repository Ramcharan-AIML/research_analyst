"""
Streamlit front-end for the Multi-Agent Research Analyst.

UI only. Imports the agents/chains defined in agents.py; does not modify them.

Run with:  streamlit run app.py
"""

import re
import time
from datetime import datetime

import streamlit as st

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Research Analyst",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Inter:wght@400;500;600&display=swap');

:root {
    --ink:      #14181F;
    --body:     #33383F;
    --muted:    #6E747E;
    --faint:    #9AA0A9;
    --rule:     #E2DFD8;
    --rule-soft:#EDEAE4;
    --paper:    #FBFAF8;
    --card:     #FFFFFF;
    --tint:     #F6F4F0;
    --navy:     #1C3D5A;
    --navy-dk:  #142C42;
    --brass:    #9A7B4F;
    --serif:    'Source Serif 4', Georgia, 'Times New Roman', serif;
    --sans:     'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
}

html, body, [class*="css"], .stApp {
    font-family: var(--sans);
    -webkit-font-smoothing: antialiased;
    font-feature-settings: "kern" 1, "liga" 1;
}

.stApp { background: var(--paper); }
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2.4rem; padding-bottom: 4.5rem; max-width: 1080px; }

.caps {
    font-size:.685rem; font-weight:600; letter-spacing:.11em;
    text-transform:uppercase; color:var(--faint);
}
.num { font-variant-numeric: tabular-nums; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: var(--tint); border-right: 1px solid var(--rule); }
[data-testid="stSidebar"] .block-container { padding-top: 1.9rem; }

.brand {
    font-family:var(--serif); font-size:1.2rem; font-weight:600;
    color:var(--ink); letter-spacing:-.015em;
}
.brand-rule { width:26px; height:2px; background:var(--brass); margin:.55rem 0 .5rem; }
.brand-sub  { font-size:.78rem; color:var(--muted); line-height:1.5; }

.side-label {
    font-size:.685rem; font-weight:600; letter-spacing:.11em; text-transform:uppercase;
    color:var(--faint); margin:1.9rem 0 .75rem;
    padding-bottom:.45rem; border-bottom:1px solid var(--rule);
}
.side-row  { display:flex; gap:.75rem; padding:.45rem 0; align-items:baseline; }
.side-n    { font-family:var(--serif); font-size:.86rem; color:var(--brass);
             font-variant-numeric:tabular-nums; min-width:13px; }
.side-name { font-size:.84rem; color:var(--body); font-weight:500; }
.side-role { font-size:.765rem; color:var(--muted); margin-top:.05rem; }
.side-kv   { display:flex; justify-content:space-between; gap:1rem; padding:.32rem 0;
             font-size:.79rem; border-bottom:1px solid var(--rule-soft); }
.side-kv b { font-weight:500; color:var(--body); }
.side-kv span { color:var(--muted); }

/* ---------- Masthead ---------- */
.masthead { margin-bottom:2.1rem; }
.eyebrow  { display:flex; align-items:center; gap:.7rem; margin-bottom:.85rem; }
.eyebrow .line { width:22px; height:1px; background:var(--brass); }
.masthead h1 {
    font-family:var(--serif); font-size:2.75rem; font-weight:600; color:var(--ink);
    letter-spacing:-.028em; margin:0 0 .6rem; line-height:1.12;
}
.masthead p {
    color:var(--muted); font-size:1rem; margin:0; line-height:1.65;
    max-width:600px; font-weight:400;
}
.rule-heavy { height:1px; background:var(--rule); margin:1.9rem 0 1.5rem; }

/* ---------- Stage strip ---------- */
.stages { display:grid; grid-template-columns:repeat(4,1fr); gap:1px;
          background:var(--rule); border:1px solid var(--rule); border-radius:3px;
          overflow:hidden; margin:.4rem 0 2rem;
          box-shadow:0 1px 2px rgba(20,24,31,.035); }
.stage  { padding:1rem 1.1rem 1.05rem; background:var(--card); position:relative; }
.stage-top  { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:.5rem; }
.stage-n    { font-family:var(--serif); font-size:.95rem; color:var(--faint);
              font-variant-numeric:tabular-nums; line-height:1; }
.stage-flag { font-size:.645rem; font-weight:600; letter-spacing:.1em;
              text-transform:uppercase; color:var(--faint); }
.stage-name { font-size:.885rem; font-weight:600; color:var(--ink); letter-spacing:-.008em; }
.stage-role { font-size:.775rem; color:var(--muted); margin-top:.16rem; }
.stage.done   { background:var(--tint); }
.stage.done .stage-n    { color:var(--brass); }
.stage.done .stage-flag { color:var(--brass); }
.stage.active::before {
    content:""; position:absolute; top:0; left:0; right:0; height:2px; background:var(--navy);
}
.stage.active .stage-n    { color:var(--navy); }
.stage.active .stage-flag { color:var(--navy); }

/* ---------- Metrics ---------- */
.mrow   { display:grid; grid-template-columns:repeat(4,1fr); gap:1px;
          background:var(--rule); border:1px solid var(--rule); border-radius:3px;
          overflow:hidden; margin:0 0 2rem; box-shadow:0 1px 2px rgba(20,24,31,.035); }
.metric { background:var(--card); padding:1.15rem 1.25rem 1.2rem; }
.metric-k { font-size:.665rem; font-weight:600; letter-spacing:.11em;
            text-transform:uppercase; color:var(--faint); }
.metric-v { font-family:var(--serif); font-size:2rem; font-weight:600; color:var(--ink);
            letter-spacing:-.03em; margin-top:.45rem; line-height:1;
            font-variant-numeric:tabular-nums; }
.metric-v span { font-family:var(--sans); font-size:.8rem; color:var(--faint);
                 font-weight:400; letter-spacing:0; margin-left:.1rem; }
.metric-note { font-size:.755rem; color:var(--muted); margin-top:.5rem; }

/* ---------- Document ---------- */
.docwrap { border:1px solid var(--rule); border-radius:3px; background:var(--card);
           box-shadow:0 1px 3px rgba(20,24,31,.05); overflow:hidden; }
.dochead { padding:1.6rem 3rem 1.35rem; border-bottom:1px solid var(--rule); background:var(--card); }
.dochead h2 {
    font-family:var(--serif); font-size:1.35rem; font-weight:600; color:var(--ink);
    margin:.45rem 0 .55rem; letter-spacing:-.02em; line-height:1.3;
}
.dochead .meta { font-size:.755rem; color:var(--muted); display:flex; gap:.55rem; flex-wrap:wrap; }
.dochead .meta i { color:var(--faint); font-style:normal; }

.doc { padding:2.3rem 3rem 2.6rem; }
.doc p, .doc li {
    font-family:var(--serif); font-size:1.055rem; line-height:1.78; color:var(--body);
}
.doc p { margin:0 0 1.05rem; max-width:66ch; }
.doc h1, .doc h2, .doc h3 {
    font-family:var(--serif); color:var(--ink); font-weight:600;
    letter-spacing:-.018em; margin:2rem 0 .85rem; padding:0;
}
.doc h1 { font-size:1.5rem; }
.doc h2 { font-size:1.22rem; padding-bottom:.5rem; border-bottom:1px solid var(--rule-soft); }
.doc h3 { font-size:1.04rem; }
.doc h1:first-child, .doc h2:first-child, .doc h3:first-child { margin-top:0; }
.doc ul, .doc ol { padding-left:1.15rem; max-width:66ch; margin:0 0 1.05rem; }
.doc li { margin:.4rem 0; padding-left:.2rem; }
.doc li::marker { color:var(--brass); }
.doc strong { color:var(--ink); font-weight:600; }
.doc a { color:var(--navy); text-decoration:none; border-bottom:1px solid #C3CCD6; }
.doc a:hover { border-bottom-color:var(--navy); }
.doc code { font-family:ui-monospace,'SF Mono',Menlo,monospace; background:var(--tint);
            border:1px solid var(--rule-soft); padding:.08rem .34rem; border-radius:2px;
            font-size:.86em; color:var(--ink); }
.doc hr { border:none; border-top:1px solid var(--rule); margin:1.8rem 0; }

/* ---------- Sources ---------- */
.src   { padding:.95rem 0; border-bottom:1px solid var(--rule-soft); display:flex; gap:1.15rem; }
.src:last-child { border-bottom:none; }
.src-i { font-family:var(--serif); font-size:.9rem; color:var(--brass);
         font-variant-numeric:tabular-nums; min-width:22px; }
.src-d { font-size:.895rem; color:var(--ink); font-weight:500; letter-spacing:-.005em; }
.src-u { font-size:.785rem; color:var(--muted); word-break:break-all;
         text-decoration:none; display:inline-block; margin-top:.14rem; }
.src-u:hover { color:var(--navy); }

/* ---------- Score ---------- */
.score { border:1px solid var(--rule); border-radius:3px; background:var(--card);
         padding:1.35rem 1.6rem; margin-bottom:1.2rem;
         box-shadow:0 1px 2px rgba(20,24,31,.035); }
.score-v { font-family:var(--serif); font-size:2.5rem; font-weight:600; color:var(--ink);
           letter-spacing:-.035em; font-variant-numeric:tabular-nums; line-height:1; }
.score-d { color:var(--faint); font-size:1rem; }
.bar   { height:3px; background:var(--rule); margin-top:1.05rem; overflow:hidden; }
.bar-f { height:100%; background:var(--navy); }

/* ---------- Widgets ---------- */
.stTextInput input {
    background:var(--card) !important; border:1px solid #D5D1C9 !important;
    border-radius:3px !important; color:var(--ink) !important;
    padding:.72rem .9rem !important; font-size:.955rem !important;
    box-shadow:0 1px 2px rgba(20,24,31,.03) !important;
}
.stTextInput input:focus {
    border-color:var(--navy) !important; box-shadow:0 0 0 3px rgba(28,61,90,.08) !important;
}
.stTextInput input::placeholder { color:var(--faint) !important; }

.stButton > button {
    background:var(--card); border:1px solid #D5D1C9; color:var(--body);
    border-radius:3px; padding:.46rem .75rem; font-weight:400; font-size:.79rem;
    box-shadow:0 1px 2px rgba(20,24,31,.03); width:100%;
    transition:border-color .14s ease, color .14s ease, background .14s ease;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.stButton > button:hover { border-color:var(--navy); color:var(--navy); background:var(--card); }
.stButton > button:focus { box-shadow:0 1px 2px rgba(20,24,31,.03) !important; color:var(--navy) !important; }
.stButton > button[kind="primary"] {
    background:var(--navy); border:1px solid var(--navy); color:#FFF;
    font-weight:500; font-size:.9rem; padding:.72rem 1.15rem; letter-spacing:.005em;
    box-shadow:0 1px 3px rgba(20,44,66,.22);
}
.stButton > button[kind="primary"]:hover {
    background:var(--navy-dk); border-color:var(--navy-dk); color:#FFF;
    box-shadow:0 2px 6px rgba(20,44,66,.26);
}

.stDownloadButton > button {
    width:100%; background:var(--card); border:1px solid #D5D1C9; color:var(--body);
    border-radius:3px; font-size:.79rem; font-weight:400;
    box-shadow:0 1px 2px rgba(20,24,31,.03);
}
.stDownloadButton > button:hover { border-color:var(--navy); color:var(--navy); }

.stTabs [data-baseweb="tab-list"] { gap:2rem; border-bottom:1px solid var(--rule); }
.stTabs [data-baseweb="tab"] {
    background:transparent; color:var(--muted); padding:.6rem 0;
    font-size:.845rem; font-weight:500; letter-spacing:.005em;
}
.stTabs [aria-selected="true"] { color:var(--ink) !important; }
.stTabs [data-baseweb="tab-highlight"] { background:var(--navy); height:2px; }
.stTabs [data-baseweb="tab-border"] { display:none; }

div[data-testid="stExpander"] details {
    background:var(--card) !important; border:1px solid var(--rule) !important; border-radius:3px !important;
}
[data-testid="stNotification"] { border-radius:3px; }
[data-testid="stCode"] { border-radius:3px; }

.tag { display:inline-block; font-size:.715rem; color:var(--muted);
       border:1px solid var(--rule); border-radius:2px; padding:.2rem .55rem;
       background:var(--card); letter-spacing:.01em; }
.tag.live { color:var(--navy); border-color:#C3CCD6; }

.empty { border:1px solid var(--rule); border-radius:3px; padding:3.6rem 2rem;
         text-align:center; background:var(--card); box-shadow:0 1px 2px rgba(20,24,31,.03); }
.empty-t { font-family:var(--serif); font-size:1.15rem; color:var(--ink); font-weight:600;
           letter-spacing:-.015em; }
.empty-s { font-size:.875rem; color:var(--muted); margin-top:.45rem; }

.sec-label { font-size:.665rem; font-weight:600; letter-spacing:.11em; text-transform:uppercase;
             color:var(--faint); margin:1.6rem 0 .65rem; }
.hint { font-size:.735rem; color:var(--faint); margin:0 0 .55rem; letter-spacing:.01em; }
.foot { border-top:1px solid var(--rule); margin-top:3.4rem; padding-top:1.3rem;
        color:var(--faint); font-size:.765rem; display:flex; justify-content:space-between; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Pipeline stages (display metadata only)
# ----------------------------------------------------------------------------
STAGES = [
    ("I", "Search Agent", "Web retrieval via Tavily"),
    ("II", "Reader Agent", "Page scraping"),
    ("III", "Writer Chain", "Report synthesis"),
    ("IV", "Critic Chain", "Quality review"),
]


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def parse_score(feedback: str):
    m = re.search(r"Score\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*/\s*10", feedback or "", re.I)
    return float(m.group(1)) if m else None


def extract_urls(text: str):
    urls = re.findall(r"https?://[^\s\)\]\"'<>,]+", text or "")
    seen, out = set(), []
    for u in urls:
        u = u.rstrip(".,;")
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def domain_of(url: str) -> str:
    m = re.match(r"https?://(?:www\.)?([^/]+)", url)
    return m.group(1) if m else url


def as_text(content) -> str:
    """Flatten LangChain message content to a plain string.

    In LangChain 1.x a message's .content may be a str, or a list of content
    blocks such as [{"type": "text", "text": "..."}]. Everything downstream
    here expects a string, so normalise once at the boundary.
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return content.get("text", "") if isinstance(content.get("text"), str) else str(content)
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        return "\n".join(parts)
    return str(content)


def message_text(message) -> str:
    """Text of the last agent message, across LangChain versions."""
    text = getattr(message, "text", None)
    if callable(text):
        text = text()
    if isinstance(text, str) and text.strip():
        return text
    return as_text(getattr(message, "content", message))


def render_stages(active: int = -1, done: int = -1):
    """active = index currently running, done = index of last completed stage."""
    html = ['<div class="stages">']
    for i, (n, name, role) in enumerate(STAGES):
        if i <= done:
            cls, flag = "stage done", "Complete"
        elif i == active:
            cls, flag = "stage active", "Running"
        else:
            cls, flag = "stage", "Pending"
        html.append(
            f'<div class="{cls}"><div class="stage-top">'
            f'<span class="stage-n">{n}</span><span class="stage-flag">{flag}</span></div>'
            f'<div class="stage-name">{name}</div>'
            f'<div class="stage-role">{role}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def metric(label, value, unit="", note=""):
    u = f"<span>{unit}</span>" if unit else ""
    return (
        f'<div class="metric"><div class="metric-k">{label}</div>'
        f'<div class="metric-v">{value}{u}</div>'
        f'<div class="metric-note">{note}</div></div>'
    )


# ----------------------------------------------------------------------------
# Sample payload - lets the layout be reviewed without spending API calls
# ----------------------------------------------------------------------------
DEMO = {
    "search_results": (
        "Title: Small Language Models Are the Quiet Revolution\n"
        "URL: https://www.example-research.org/slm-revolution\n"
        "Snippet: Sub-10B parameter models now match 2024-era frontier systems on "
        "reasoning benchmarks while running on consumer hardware...\n\n"
        "---\n"
        "Title: On-Device Inference Benchmarks Q2 2026\n"
        "URL: https://benchmarks.example.dev/on-device-2026\n"
        "Snippet: Median latency for 7B-class models on laptop NPUs fell 61% "
        "year over year, driven by quantisation-aware training...\n\n"
        "---\n"
        "Title: The Economics of Distillation\n"
        "URL: https://journal.example.edu/distillation-economics\n"
        "Snippet: Training-compute cost per unit of downstream accuracy has dropped "
        "roughly 4x annually since 2023..."
    ),
    "scraped_content": (
        "Small language models (SLMs) occupy the 1B-15B parameter band. The 2026 "
        "generation is trained on heavily curated, synthetically augmented corpora "
        "rather than raw web scrape, which is the single largest driver of the "
        "quality jump. Quantisation-aware training at 4-bit has become default, "
        "cutting memory footprint ~3.5x with under 2% benchmark degradation. "
        "Deployment has shifted decisively toward the edge: phones, laptops and "
        "embedded industrial controllers now run capable models locally, removing "
        "per-token API cost and satisfying data-residency requirements that block "
        "cloud inference in regulated sectors."
    ),
    "report": """## Introduction

Small language models (SLMs) have moved from a research curiosity to the default
deployment target for a large share of production AI workloads. This report
examines the technical and economic forces behind that shift through mid-2026.

## Key Findings

**1. Data curation outweighs parameter count.** The 2026 SLM generation is trained
on curated, synthetically augmented corpora rather than raw web scrape. Sub-10B
models now match 2024-era frontier systems on standard reasoning benchmarks, a
result attributable primarily to data quality rather than architecture.

**2. Quantisation has become a first-class training concern.** Quantisation-aware
training at 4-bit precision is now the default rather than a post-hoc compression
step. The result is roughly a 3.5x reduction in memory footprint for under 2%
benchmark degradation, which is what makes laptop and phone deployment viable.

**3. The economics have inverted.** Training-compute cost per unit of downstream
accuracy has fallen roughly 4x annually since 2023. Combined with on-device
inference removing per-token API costs entirely, the total cost of ownership
argument now favours local models for high-volume, latency-sensitive workloads.

**4. Regulation is an accelerant, not a brake.** Data-residency requirements in
healthcare, finance and public sector procurement frequently prohibit cloud
inference outright. On-device SLMs sidestep the constraint rather than negotiating
with it, which has opened procurement channels closed to frontier API vendors.

## Conclusion

The SLM trajectory is best understood as a compounding of three independent
curves - data quality, quantisation efficiency and hardware acceleration - each
improving at its own rate. Frontier models retain a clear advantage on open-ended
reasoning and long-context synthesis, but the band of tasks where that advantage
justifies the cost and latency premium is narrowing each quarter.

## Sources

- https://www.example-research.org/slm-revolution
- https://benchmarks.example.dev/on-device-2026
- https://journal.example.edu/distillation-economics
""",
    "feedback": """Score: 8/10

Strengths:
- Clear causal structure: each finding names a mechanism rather than just a trend.
- Quantitative claims are specific (3.5x memory reduction, 4x annual cost decline)
  and tied back to named sources.
- The conclusion correctly scopes the claim instead of overstating SLM parity.

Areas to Improve:
- Finding 4 (regulation) is asserted without a supporting source in the research set.
- No discussion of failure modes: long-context degradation in SLMs is a known
  weakness and its omission makes the report read as one-sided.
- "Roughly 4x annually" is carried over from the source without noting the wide
  error bars on that estimate.

One line verdict:
A well-structured and technically credible report that would move from good to
excellent with an explicit treatment of SLM limitations.
""",
}

# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------
st.session_state.setdefault("result", None)
st.session_state.setdefault("history", [])
st.session_state.setdefault("topic_input", "")

# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="brand">Research Analyst</div><div class="brand-rule"></div>'
        '<div class="brand-sub">Multi-agent research pipeline</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">Mode</div>', unsafe_allow_html=True)
    demo_mode = st.toggle(
        "Sample data",
        value=True,
        help="On: render a sample result instantly, no API calls. "
             "Off: run the real agents from agents.py.",
    )
    st.markdown(
        '<span class="tag">Sample data &mdash; no API calls</span>' if demo_mode
        else '<span class="tag live">Live run &mdash; uses API credits</span>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">Pipeline</div>', unsafe_allow_html=True)
    for n, name, role in STAGES:
        st.markdown(
            f'<div class="side-row"><span class="side-n">{n}</span>'
            f'<div><div class="side-name">{name}</div>'
            f'<div class="side-role">{role}</div></div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="side-label">Configuration</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-kv"><b>Model</b><span>mistral-medium-latest</span></div>'
        '<div class="side-kv"><b>Runtime</b><span>LangChain &middot; LangGraph</span></div>'
        '<div class="side-kv"><b>Search</b><span>Tavily</span></div>'
        '<div class="side-kv" style="border-bottom:none;"><b>Scraper</b><span>BeautifulSoup</span></div>',
        unsafe_allow_html=True,
    )

    if st.session_state.history:
        st.markdown('<div class="side-label">Recent runs</div>', unsafe_allow_html=True)
        for h in reversed(st.session_state.history[-6:]):
            st.markdown(
                f'<div style="padding:.5rem 0;border-bottom:1px solid #EDEAE4;">'
                f'<div style="font-size:.815rem;color:#33383F;line-height:1.4;">{h["topic"][:44]}</div>'
                f'<div style="font-size:.735rem;color:#9AA0A9;margin-top:.15rem;" class="num">'
                f'{h["time"]} &nbsp;&middot;&nbsp; {h["elapsed"]}s</div></div>',
                unsafe_allow_html=True,
            )

# ----------------------------------------------------------------------------
# Masthead
# ----------------------------------------------------------------------------
st.markdown(
    '<div class="masthead">'
    '<div class="eyebrow"><span class="line"></span>'
    '<span class="caps">Multi-agent research pipeline</span></div>'
    '<h1>Research Analyst</h1>'
    '<p>Enter a topic. Two tool-using agents search and read the web, a writer chain '
    'drafts a structured report, and a critic chain reviews and scores it.</p></div>',
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Input
# ----------------------------------------------------------------------------
col_in, col_go = st.columns([4, 1], vertical_alignment="bottom")
with col_in:
    topic = st.text_input(
        "Research topic",
        key="topic_input",
        placeholder="Enter a research topic",
        label_visibility="collapsed",
    )
with col_go:
    run = st.button("Run analysis", type="primary", use_container_width=True)

EXAMPLES = [
    ("Small language models", "State of small language models in 2026"),
    ("India semiconductors", "India's semiconductor manufacturing push"),
    ("Agentic AI in the enterprise", "Agentic AI in enterprise workflows"),
    ("EV battery supply chain", "Global EV battery supply chain outlook"),
]


def _set_topic(t):
    st.session_state.topic_input = t


st.markdown('<div class="hint" style="margin-top:.85rem;">Suggested topics</div>',
            unsafe_allow_html=True)
ex_cols = st.columns(len(EXAMPLES))
for c, (short, full) in zip(ex_cols, EXAMPLES):
    c.button(short, key=f"ex_{short}", on_click=_set_topic, args=(full,),
             use_container_width=True)

st.markdown('<div class="rule-heavy"></div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------------
if run:
    if not topic.strip():
        st.warning("Enter a research topic to begin.")
    else:
        stage_slot = st.empty()
        started = time.time()

        if demo_mode:
            for i in range(4):
                with stage_slot.container():
                    render_stages(active=i, done=i - 1)
                time.sleep(0.4)
            with stage_slot.container():
                render_stages(done=3)
            st.session_state.result = {
                **DEMO, "topic": topic, "demo": True,
                "elapsed": round(time.time() - started, 1),
                "generated": datetime.now(),
            }
        else:
            try:
                from agents import (
                    build_search_agent,
                    build_reader_agent,
                    writer_chain,
                    critic_chain,
                )
            except Exception as e:
                st.error(f"Could not import agents.py: {type(e).__name__} - {e}")
                st.stop()

            state = {}
            try:
                # Stage 1 - search
                with stage_slot.container():
                    render_stages(active=0)
                with st.status("Search agent querying the web...", expanded=False) as s:
                    agent = build_search_agent()
                    out = agent.invoke({"messages": [
                        ("user", f"Find recent, reliable and detailed information about: {topic}")
                    ]})
                    state["search_results"] = message_text(out["messages"][-1])
                    s.update(label="Search agent complete", state="complete")

                # Stage 2 - read
                with stage_slot.container():
                    render_stages(active=1, done=0)
                with st.status("Reader agent scraping top source...", expanded=False) as s:
                    agent = build_reader_agent()
                    out = agent.invoke({"messages": [(
                        "user",
                        f"Based on the following search results about '{topic}', "
                        f"pick the most relevant URL and scrape it for deeper content.\n\n"
                        f"Search results:\n {state['search_results'][:800]}"
                    )]})
                    state["scraped_content"] = message_text(out["messages"][-1])
                    s.update(label="Reader agent complete", state="complete")

                # Stage 3 - write
                with stage_slot.container():
                    render_stages(active=2, done=1)
                with st.status("Writer chain drafting the report...", expanded=False) as s:
                    combined = (
                        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
                        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
                    )
                    state["report"] = as_text(writer_chain.invoke(
                        {"topic": topic, "research": combined}
                    ))
                    s.update(label="Writer chain complete", state="complete")

                # Stage 4 - critique
                with stage_slot.container():
                    render_stages(active=3, done=2)
                with st.status("Critic chain reviewing...", expanded=False) as s:
                    state["feedback"] = as_text(
                        critic_chain.invoke({"report": state["report"]})
                    )
                    s.update(label="Critic chain complete", state="complete")

                with stage_slot.container():
                    render_stages(done=3)

                state.update(topic=topic, demo=False,
                             elapsed=round(time.time() - started, 1),
                             generated=datetime.now())
                st.session_state.result = state

            except Exception as e:
                st.error(f"Pipeline failed: {type(e).__name__} - {e}")
                st.session_state.result = None

        if st.session_state.result:
            st.session_state.history.append({
                "topic": topic,
                "time": datetime.now().strftime("%H:%M"),
                "elapsed": st.session_state.result["elapsed"],
            })

# ----------------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------------
res = st.session_state.result

if res:
    # Normalise once so every renderer below is guaranteed plain strings.
    for key in ("search_results", "scraped_content", "report", "feedback"):
        res[key] = as_text(res.get(key, ""))

    score = parse_score(res["feedback"])
    sources = extract_urls(res["search_results"] + "\n" + res["report"])
    words = len(res["report"].split())
    stamp = res.get("generated") or datetime.now()

    st.markdown(
        '<div class="mrow">'
        + metric("Quality score", f"{score:g}" if score else "&mdash;", " / 10",
                 "Assigned by critic chain")
        + metric("Report length", f"{words:,}", " words", "Writer chain output")
        + metric("Sources", len(sources), "", "Unique URLs referenced")
        + metric("Run time", res.get("elapsed", "&mdash;"), "s",
                 "Sample data" if res.get("demo") else "Live pipeline")
        + "</div>",
        unsafe_allow_html=True,
    )

    if res.get("demo"):
        st.info("Sample data. Turn off **Sample data** in the sidebar to run the real agents.")

    tab_r, tab_c, tab_s, tab_raw = st.tabs(
        ["Report", "Critique", "Sources", "Research trail"]
    )

    with tab_r:
        st.markdown(
            f'<div class="docwrap"><div class="dochead">'
            f'<div class="caps">Research report</div>'
            f'<h2>{res.get("topic", "")}</h2>'
            f'<div class="meta"><span class="num">{stamp.strftime("%d %B %Y, %H:%M")}</span>'
            f'<i>&middot;</i><span>mistral-medium-latest</span>'
            f'<i>&middot;</i><span class="num">{len(sources)} sources</span>'
            f'<i>&middot;</i><span class="num">{words:,} words</span></div></div>'
            f'<div class="doc">',
            unsafe_allow_html=True,
        )
        st.markdown(res["report"] or "_No report generated._")
        st.markdown("</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
        d1, d2, _ = st.columns([1, 1, 3])
        slug = re.sub(r"[^a-z0-9]+", "_", res.get("topic", "report").lower())[:48]
        with d1:
            st.download_button(
                "Download report (.md)",
                data=f"# {res.get('topic', 'Research Report')}\n\n{res['report']}",
                file_name=f"report_{slug}.md",
                mime="text/markdown",
            )
        with d2:
            bundle = (
                f"# {res.get('topic', '')}\n\n## Report\n\n{res['report']}\n\n"
                f"## Critique\n\n{res['feedback']}\n\n"
                f"## Raw search results\n\n{res['search_results']}\n\n"
                f"## Scraped content\n\n{res['scraped_content']}\n"
            )
            st.download_button("Download full bundle (.md)", data=bundle,
                               file_name=f"bundle_{slug}.md", mime="text/markdown")

    with tab_c:
        if score is not None:
            pct = int(score * 10)
            st.markdown(
                f'<div class="score"><div class="caps">Critic score</div>'
                f'<div style="display:flex;align-items:baseline;gap:.45rem;margin-top:.5rem;">'
                f'<span class="score-v">{score:g}</span><span class="score-d">/ 10</span></div>'
                f'<div class="bar"><div class="bar-f" style="width:{pct}%;"></div></div></div>',
                unsafe_allow_html=True,
            )
        st.markdown('<div class="docwrap"><div class="doc">', unsafe_allow_html=True)
        st.markdown(res["feedback"] or "_No critique generated._")
        st.markdown("</div></div>", unsafe_allow_html=True)

    with tab_s:
        if sources:
            html = '<div class="docwrap"><div class="doc" style="padding:1.4rem 2rem;">'
            for i, u in enumerate(sources, 1):
                html += (
                    f'<div class="src"><div class="src-i">{i:02d}</div><div>'
                    f'<div class="src-d">{domain_of(u)}</div>'
                    f'<a class="src-u" href="{u}" target="_blank">{u}</a></div></div>'
                )
            html += "</div></div>"
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty"><div class="empty-t">No sources</div>'
                        '<div class="empty-s">No URLs were found in this run.</div></div>',
                        unsafe_allow_html=True)

    with tab_raw:
        st.markdown('<div class="sec-label">Stage I &middot; Search agent output</div>',
                    unsafe_allow_html=True)
        st.code(res["search_results"][:6000] or "empty", language="text")
        st.markdown('<div class="sec-label">Stage II &middot; Reader agent output</div>',
                    unsafe_allow_html=True)
        st.code(res["scraped_content"][:6000] or "empty", language="text")

else:
    render_stages()
    st.markdown(
        '<div class="empty"><div class="empty-t">No analysis yet</div>'
        '<div class="empty-s">Enter a topic above, or select a suggested topic, '
        'then run the analysis.</div></div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="foot"><span>Research Analyst</span>'
    '<span>LangChain &middot; LangGraph &middot; Mistral &middot; Tavily</span></div>',
    unsafe_allow_html=True,
)
