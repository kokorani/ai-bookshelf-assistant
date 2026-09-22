"""Interactive Streamlit bookshelf for the existing reading-tracker project.

Run: streamlit run bookshelf_ui.py
"""

import html
import json
import os
from datetime import date

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from openai import OpenAI

from my_tools import my_tools
from tools import add_book, delete_book, get_books, get_reading_summary, update_book


load_dotenv()
st.set_page_config(page_title="My e-bookshelf", page_icon="📚", layout="wide")

STATUSES = ["Currently Reading", "On Hold", "Completed"]
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
STATUS_DETAILS = {
    "Currently Reading": ("currently reading", "#3bb6a5"),
    "On Hold": ("on hold", "#b58ddb"),
    "Completed": ("completed", "#4d8dd8"),
}
BOOK_COLOURS = ["#f3a65a", "#e77868", "#8cc9c3", "#b18bd3", "#c2cf80", "#e3a1bb", "#659bd4", "#e5c45f"]
TOOL_MAPPING = {
    "add_book": add_book,
    "get_books": get_books,
    "update_book": update_book,
    "delete_book": delete_book,
    "get_reading_summary": get_reading_summary,
}

SYSTEM_INSTRUCTIONS = f"""
You are the helpful assistant inside a personal reading tracker. Today is {date.today().isoformat()}.
You can add, view, update, delete, and summarize books through the provided tools.

Follow these rules:
- When adding a book, use status "Currently Reading" unless the user explicitly chooses another valid status.
- When the user says they are starting a book, first call get_books to find its exact id, then update it to
  "Currently Reading" and set started_at to today unless the user supplies a date.
- When the user says they are putting a book on hold, first find it, then set status to "On Hold".
- When the user says they finished a book, first find it, then set status to "Completed" and completed_at to
  today unless they supply a date.
- Never guess a book id. Call get_books before updating or deleting by title unless the user gave an id.
- If a match is ambiguous, ask a short clarifying question instead of changing anything.
- Use get_reading_summary for count/average-rating requests.
- Be concise, state what changed, and do not claim an action succeeded unless its tool call succeeds.
"""


@st.cache_data(ttl=15, show_spinner=False)
def load_books():
    """Fetch current books from the unchanged project database."""
    try:
        data = get_books()
        return data, None
    except Exception as error:
        return pd.DataFrame(columns=["id", "title", "author", "genre", "status"]), str(error)


def data_for_tool_output(value):
    """Return safe, compact output for the OpenAI function-call continuation."""
    if isinstance(value, pd.DataFrame):
        return value.to_json(orient="records", date_format="iso")
    return str(value)


def ask_assistant(message):
    """Run the same function-calling loop as main.py, but inside Streamlit."""
    client = OpenAI()
    request = {
        "model": os.getenv("OPENAI_MODEL", "gpt-5.6-sol"),
        "input": message,
        "instructions": SYSTEM_INSTRUCTIONS,
        "tools": my_tools,
    }
    if st.session_state.previous_response_id:
        request["previous_response_id"] = st.session_state.previous_response_id

    response = client.responses.create(**request)
    made_change = False

    while True:
        tool_outputs = []
        for item in response.output:
            if item.type != "function_call":
                continue

            arguments = json.loads(item.arguments)
            function = TOOL_MAPPING[item.name]
            result = function(**arguments)
            if item.name in {"add_book", "update_book", "delete_book"}:
                made_change = True
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": data_for_tool_output(result),
                }
            )

        if not tool_outputs:
            break

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6-sol"),
            input=tool_outputs,
            previous_response_id=response.id,
            instructions=SYSTEM_INSTRUCTIONS,
            tools=my_tools,
        )

    st.session_state.previous_response_id = response.id
    return response.output_text, made_change


def bookshelf_svg(books):
    """Create the four-shelf illustration from the latest database rows."""
    shelf_blocks = []
    shelf_y = [400, 665, 930]

    for shelf_index, (status, y) in enumerate(zip(STATUSES, shelf_y)):
        status_books = books[books["status"] == status].reset_index(drop=True)
        friendly_name, label_colour = STATUS_DETAILS[status]
        label_y = y - 190
        book_shapes = []

        if status_books.empty:
            book_shapes.append(
                f'<text class="empty" x="510" y="{y - 62}" text-anchor="middle">0 books here</text>'
            )
        else:
            shown_books = status_books.head(8)
            start_x = 235
            widths = [43, 54, 47, 60, 40, 52, 45, 57]
            heights = [145, 174, 155, 184, 139, 166, 151, 177]

            for i, (_, book) in enumerate(shown_books.iterrows()):
                width = widths[i]
                height = heights[i]
                x = start_x + sum(widths[:i]) + (i * 8)
                tilt = [-2, 1, -1, 2, -2, 1, 0, -1][i]
                title = html.escape(str(book.get("title", "Untitled")).upper()[:20])
                author = html.escape(str(book.get("author", "")).upper()[:16])
                colour = BOOK_COLOURS[(i + shelf_index * 2) % len(BOOK_COLOURS)]
                book_shapes.append(
                    f'''<g transform="translate({x}, {y - height}) rotate({tilt} {width / 2} {height / 2})">
                        <rect width="{width}" height="{height}" rx="3" fill="{colour}"/>
                        <rect x="5" y="6" width="{width - 10}" height="{height - 12}" fill="none" stroke="#241e1b" opacity=".28"/>
                        <text class="book-title" x="{width / 2}" y="{height / 2 - 6}" text-anchor="middle"
                           transform="rotate(-90 {width / 2} {height / 2})">{title}</text>
                        <text class="book-author" x="{width / 2}" y="{height / 2 + 10}" text-anchor="middle"
                           transform="rotate(-90 {width / 2} {height / 2})">{author}</text>
                    </g>'''
                )

            hidden = len(status_books) - len(shown_books)
            if hidden:
                book_shapes.append(
                    f'<text class="more" x="760" y="{y - 50}">+{hidden} more</text>'
                )

        shelf_blocks.append(
            f'''
            <g transform="rotate(-7 104 {label_y})">
              <rect x="28" y="{label_y - 30}" width="183" height="48" rx="22" fill="#fff3d8"
                    stroke="{label_colour}" stroke-width="3"/>
              <text class="label" x="47" y="{label_y + 1}">{friendly_name} · {len(status_books)}</text>
            </g>
            <path d="M112 {label_y + 44} C130 {label_y + 74}, 160 {y - 22}, 208 {y - 35}"
                  fill="none" stroke="#1c1b19" stroke-width="3"/>
            <path d="M199 {y - 44} l11 10 -14 2" fill="none" stroke="#1c1b19" stroke-width="3"/>
            {''.join(book_shapes)}
            <rect x="200" y="{y}" width="635" height="18" rx="9" fill="#e57265"/>
            <rect x="205" y="{y + 3}" width="625" height="7" rx="4" fill="#ffc16f"/>
            '''
        )

    return f"""
    <!doctype html>
    <html><head>
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@500;600;700&family=DM+Sans:wght@400;500&display=swap');
        * {{ box-sizing: border-box; }}
        html, body {{ width:100%; height:100%; }}
        body {{ margin: 0; background: #edf1ff; }}
        svg {{ display:block; width:100%; height:100%; animation:shelf-in .32s ease-out both; }}
        @keyframes shelf-in {{ from {{ opacity:.2; transform:translateY(8px); }} to {{ opacity:1; transform:translateY(0); }} }}
        .label,.empty,.more {{ font-family:'Caveat',cursive; font-weight:700; }}
        .label {{ font-size:22px; fill:#273250; }}
        .empty {{ font-size:23px; fill:#53607f; }}
        .more {{ font-size:18px; fill:#53607f; }}
        .book-title {{ font-family:'DM Sans',sans-serif; font-size:7px; font-weight:700; fill:#211d1b; }}
        .book-author {{ font-family:'DM Sans',sans-serif; font-size:5.5px; fill:#211d1b; }}
      </style>
    </head><body>
      <svg viewBox="0 0 870 1080" role="img" aria-label="Four shelf reading bookshelf">
        <defs>
          <linearGradient id="nightShelf" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#243c61"/><stop offset=".48" stop-color="#2c5074"/>
            <stop offset="1" stop-color="#203a5a"/>
          </linearGradient>
          <pattern id="stars" width="92" height="92" patternUnits="userSpaceOnUse">
            <circle cx="14" cy="16" r="1.3" fill="#a7cbe7" opacity=".48"/>
            <circle cx="68" cy="37" r="1" fill="#f9d787" opacity=".65"/>
            <circle cx="37" cy="76" r="1.1" fill="#d8c4ef" opacity=".45"/>
          </pattern>
          <filter id="shadow" x="-20%" y="-20%" width="140%" height="150%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="8"/><feOffset dy="9"/>
            <feComponentTransfer><feFuncA type="linear" slope=".24"/></feComponentTransfer>
            <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <!-- Original night-reading decor: a moon lamp, small globe, and tea set. -->
        <g transform="translate(252 30)">
          <circle cx="70" cy="71" r="51" fill="#f9d787"/>
          <circle cx="94" cy="52" r="51" fill="#edf1ff"/>
          <path d="M70 122v35M37 158h66" stroke="#465474" stroke-width="8" stroke-linecap="round"/>
          <circle cx="38" cy="22" r="3" fill="#a78ad3"/><circle cx="18" cy="53" r="2" fill="#6e9fda"/>
        </g>
        <g transform="translate(456 52)">
          <circle cx="54" cy="57" r="45" fill="#5a9cc7" stroke="#273250" stroke-width="5"/>
          <path d="M13 57h82M54 12c-23 25-23 64 0 90M54 12c23 25 23 64 0 90" fill="none" stroke="#d5e7f1" stroke-width="3"/>
          <path d="M54 103v39M16 142h76" stroke="#4c3f70" stroke-width="7" stroke-linecap="round"/>
        </g>
        <g transform="translate(620 72)">
          <path d="M15 67c0-26 18-44 49-44s49 18 49 44v33H15z" fill="#d78397"/>
          <path d="M113 47c35 2 35 40 5 42" fill="none" stroke="#d78397" stroke-width="12"/>
          <path d="M43 22V4m27 18V4" stroke="#273250" stroke-width="6" stroke-linecap="round"/>
          <rect x="23" y="98" width="81" height="10" rx="5" fill="#f1bd62"/>
          <circle cx="62" cy="62" r="8" fill="#f1bd62"/>
        </g>
        <g filter="url(#shadow)">
          <rect x="180" y="182" width="690" height="870" rx="28" fill="#7868b3"/>
          <rect x="200" y="204" width="635" height="806" fill="url(#nightShelf)"/>
          <rect x="200" y="204" width="635" height="806" fill="url(#stars)"/>
          <rect x="180" y="996" width="55" height="56" fill="#7868b3"/>
          <rect x="815" y="996" width="55" height="56" fill="#7868b3"/>
        </g>
        {''.join(shelf_blocks)}
      </svg>
    </body></html>
    """


st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=DM+Sans:wght@400;500;700&display=swap');
      .stApp { background:#edf1ff; color:#273250; }
      .block-container { max-width:1520px; margin-left:1.2rem; margin-right:auto; padding-top:1.25rem; padding-bottom:1rem; }
      h1 { font-family:'Caveat',cursive; font-size:4rem !important; line-height:.9; margin-bottom:.15rem; }
      .intro { font-size:1.1rem; max-width:42rem; color:#53607f; }
      .chat-title { font-family:'Caveat',cursive; font-size:2rem; margin:0; }
      .chat-caption { font-size:.88rem; color:#637096; margin:.1rem 0 1rem; }
      [data-testid="stVerticalBlockBorderWrapper"] { background:linear-gradient(145deg, #f9f8ff 0%, #e4e6fb 100%); border:1px solid #bcb8df; border-radius:22px; box-shadow:0 12px 28px rgba(57, 68, 115, .14); }
      [data-testid="stVerticalBlockBorderWrapper"] > div { padding:1rem .9rem .9rem; }
      [data-testid="stChatMessage"] { background:#f9f8ff; border:1px solid #c9c5e4; border-radius:14px; }
      [data-testid="stChatInput"] { border:1px solid #9b93c5; border-radius:18px; background:#f9f8ff; }
      [data-testid="stRadio"] { border-left:2px solid #53607f; height:530px; margin-top:6.8rem; padding-left:.85rem; transform:translateX(-6rem); }
      [data-testid="stRadio"] [role="radiogroup"] { display:flex; flex-direction:column; height:100%; justify-content:space-between; }
      [data-testid="stRadio"] label { margin-bottom:.05rem; cursor:pointer; white-space:nowrap; }
      [data-testid="stRadio"] label > div:first-child { display:none; }
      [data-testid="stRadio"] label p { color:#53607f; font-family:'Caveat',cursive; font-size:1.7rem; font-weight:700; line-height:1.28; transition:color .18s ease, transform .18s ease; }
      [data-testid="stRadio"] label:hover p { color:#e57265; transform:translateX(3px); }
      [data-testid="stRadio"] label:has(input:checked) p { color:#e57265; text-decoration:underline; text-underline-offset:3px; }
      .stAlert { border-radius:10px; }
      @media(max-width:1000px) { [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; min-width:1120px; } }
      @media(max-width:700px) { h1 { font-size:3.2rem !important; } }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! Ask me to add a book, start reading one, put one on hold, finish one, or show your reading summary.",
        }
    ]
if "previous_response_id" not in st.session_state:
    st.session_state.previous_response_id = None
if "month_selector" not in st.session_state:
    st.session_state.month_selector = MONTHS[date.today().month - 1]

st.title("my e-bookshelf")
st.markdown(
    "<p class='intro'>Welcome to my e-bookshelf where I track my monthly reads for 2026.</p>",
    unsafe_allow_html=True,
)

books, database_error = load_books()
if database_error:
    st.warning("The bookshelf could not connect to the local database. Check that MySQL is running, then refresh the page.")

selected_month = MONTHS.index(st.session_state.month_selector) + 1
if "target_month" in books.columns:
    displayed_books = books[books["target_month"].astype("Int64") == selected_month]
else:
    displayed_books = books.iloc[0:0]

illustration, month_rail, chat = st.columns([1.6, 0.18, 1.2], gap="small", vertical_alignment="top")
with illustration:
    components.html(bookshelf_svg(displayed_books), height=690, scrolling=False)

with month_rail:
    st.radio(
        "Reading month",
        MONTHS,
        key="month_selector",
        label_visibility="collapsed",
    )

with chat:
    with st.container(border=True):
        st.markdown("<p class='chat-title'>Ask your bookshelf</p>", unsafe_allow_html=True)
        st.markdown("<p class='chat-caption'>For example: “Add Dune by Frank Herbert”, “I started Dune”, or “Show my summary”.</p>", unsafe_allow_html=True)
        chat_box = st.container(height=480, border=False)
        with chat_box:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        prompt = st.chat_input("Tell me about your reading…")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_box:
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Updating your bookshelf…"):
                        try:
                            reply, made_change = ask_assistant(prompt)
                        except Exception as error:
                            reply, made_change = (
                                f"I couldn’t reach the assistant right now: {error}",
                                False,
                            )
                        st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            if made_change:
                load_books.clear()
                st.rerun()
