import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.title("AI-Native-Book Chapter 12 Example")

html_path = Path("examples/chapter12/index.html")

if html_path.exists():
    html_file = html_path.read_text(encoding="utf-8")
    components.html(html_file, height=600, scrolling=True)
else:
    st.error(f"File not found: {html_path}")
<h1>Hello, Streamlit!</h1>
<p>This is a test.</p>



