import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="WYSIWYG HTML Editor", layout="wide")

# Load our external editor.html (must live in the same directory)
here = os.path.dirname(__file__)
with open(os.path.join(here, "editor.html"), "r", encoding="utf-8") as f:
    html = f.read()

# Render the editor
components.html(html, height=800, scrolling=True)
