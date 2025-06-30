import streamlit as st
import streamlit.components.v1 as components
import os

# Configure the Streamlit page
st.set_page_config(
    page_title="WYSIWYG HTML Editor",
    layout="wide",
)

# Load the external HTML file
html_path = os.path.join(os.path.dirname(__file__), "editor.html")
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Render it in Streamlit
components.html(html_content, height=800, scrolling=True)
