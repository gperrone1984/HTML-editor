import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="WYSIWYG HTML Editor", layout="wide")

# Load the external HTML/JS editor
here = os.path.dirname(__file__)
path = os.path.join(here, "editor.html")
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# Embed it in Streamlit
components.html(html, height=800, scrolling=True)
