import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="HTML Editor", layout="wide")

html_content = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HTML Editor</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: white; color: #333; }
    p, ul, ol, h1, h2, h3, h4, h5, h6 { margin-bottom: 1em; }

    .container { width: 100%; margin: 0 auto; padding: 20px; }
    .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #000; padding-bottom: 10px; }
    .toolbar {
      background: #f5f5f5; padding: 10px; border: 1px solid #ddd;
      border-radius: 5px; display: flex; flex-wrap: wrap; gap: 5px; align-items: center;
    }
    .toolbar button, .toolbar select, .toolbar input[type="color"], .toolbar input[type="text"] {
      font-size: 12px; padding: 5px;
    }
    .divider { width: 100%; height: 2px; background: #000; margin: 15px 0; }
    .editor-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; height: 600px; }
    .editor-panel { border: 1px solid #ddd; border-radius: 5px; display: flex; flex-direction: column; overflow: hidden; }
    .panel-header { background: #f0f0f0; padding: 10px; font-weight: bold; border-bottom: 1px solid #ddd; }
    .editor, .html-editor {
      flex: 1; width: 100%; padding: 15px; border: none; outline: none;
      font-family: inherit; font-size: 14px; line-height: 1.6; background: white; overflow-y: auto;
    }
    .html-editor {
      font-family: Consolas, 'Courier New', monospace; background: #f8f8f8;
      white-space: pre-wrap; overflow-wrap: break-word; border: 1px solid #ddd; resize: none;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>HTML Editor</h1>
    </div>
    <div class="toolbar">
      <button onclick="execCmd('bold')">B</button>
      <button onclick="execCmd('italic')">I</button>
      <button onclick="execCmd('underline')">U</button>
      <button onclick="execCmd('strikeThrough')">S</button>
      <select onchange="execCmd('formatBlock', this.value)">
        <option value="">Format</option>
        <option value="h1">H1</option>
        <option value="h2">H2</option>
        <option value="p">P</option>
      </select>
      <button onclick="execCmd('insertUnorderedList')">• List</button>
      <button onclick="execCmd('insertOrderedList')">1. List</button>
      <input type="color" onchange="execCmd('foreColor', this.value)">
      <input type="color" onchange="execCmd('backColor', this.value)">
      <button onclick="insertTable()">Table</button>
      <button onclick="insertLink()">Link</button>
      <button onclick="insertImage()">Image</button>
      <button onclick="execCmd('removeFormat')">Clear</button>
      <button onclick="pasteAsPlainText()">Paste Plain</button>
      <button onclick="execCmd('undo')">↶</button>
      <button onclick="execCmd('redo')">↷</button>
      <button onclick="openFile()">Open</button>
      <input type="text" id="findText" placeholder="Find" style="width:100px;">
      <input type="text" id="replaceText" placeholder="Replace" style="width:100px;">
      <button onclick="findText()">Find</button>
      <button onclick="findAndReplace()">Replace</button>
    </div>
    <div class="divider"></div>
    <div class="editor-container">
      <div class="editor-panel">
        <div class="panel-header">Preview</div>
        <div id="editor" class="editor" contenteditable="true"
             oninput="updateHTML()" onkeyup="updateHTML()" onpaste="handlePaste(event)">
          <h2>Start writing...</h2>
        </div>
      </div>
      <div class="editor-panel">
        <div class="panel-header">HTML</div>
        <textarea id="htmlEditor" class="html-editor"
                  oninput="updateVisual()" onkeyup="updateVisual()"
                  placeholder="Clean HTML code..."></textarea>
      </div>
    </div>
    <input type="file" id="fileInput" accept=".html,.txt" style="display:none" onchange="loadFile(event)">
  </div>

  <script src="https://cdn.jsdelivr.net/npm/js-beautify@1.14.0/js/lib/beautify-html.js"></script>
  <script>
    function execCmd(cmd, val=null) {
      document.execCommand(cmd, false, val);
      updateHTML();
    }

    function stripAttrs(html) {
      return html
        .replace(/<!--\[if !supportLists\]-->.*?<!--\[endif\]-->/gi, '')
        .replace(/<\/?o:p>/gi, '')
        .replace(/<\/?span[^>]*>/gi, '')
        .replace(/\s*(class|style|id)=("[^"]*"|'[^']*')/gi, '');
    }

    function updateHTML() {
      let raw = stripAttrs(document.getElementById('editor').innerHTML);
      let formatted = html_beautify(raw, { indent_size: 2, wrap_line_length: 80 });
      document.getElementById('htmlEditor').value = formatted;
    }

    function updateVisual() {
      document.getElementById('editor').innerHTML = document.getElementById('htmlEditor').value;
    }

    function insertTable() {
      let rows = prompt('Number of rows', '3'), cols = prompt('Number of columns', '3');
      if (rows && cols) {
        let tbl = '<table border="1" cellpadding="8" cellspacing="0">';
        for (let r = 0; r < rows; r++) {
          tbl += '<tr>';
          for (let c = 0; c < cols; c++) tbl += '<td>Cell</td>';
          tbl += '</tr>';
        }
        tbl += '</table>';
        execCmd('insertHTML', tbl);
      }
    }

    function insertLink() {
      let url = prompt('Enter URL', 'https://'), txt = prompt('Display text', 'Link');
      if (url) execCmd('insertHTML', `<a href="${url}" target="_blank">${txt}</a>`);
    }

    function insertImage() {
      let url = prompt('Image URL', ''), alt = prompt('Alt text', '');
      if (url) execCmd('insertHTML', `<img src="${url}" alt="${alt}" style="max-width:100%;height:auto;">`);
    }

    function openFile() {
      document.getElementById('fileInput').click();
    }

    function loadFile(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function(e) {
        const content = e.target.result;
        document.getElementById('editor').innerHTML = content;
        updateHTML();
      };
      reader.readAsText(file);
    }

    function handlePaste(e) { setTimeout(updateHTML, 10); }

    function pasteAsPlainText() {
      navigator.clipboard.readText().then(t => execCmd('insertText', t)).catch(_ => {
        let t = prompt('Paste text');
        execCmd('insertText', t);
      });
    }

    function findText() {
      const textToFind = document.getElementById("findText").value;
      if (!textToFind) return;
      const editor = document.getElementById("editor");
      const innerHTML = editor.innerHTML;
      const regex = new RegExp(`(${textToFind})`, 'gi');
      const highlighted = innerHTML.replace(regex, '<mark>$1</mark>');
      editor.innerHTML = highlighted;
      updateHTML();
    }

    function findAndReplace() {
      const find = document.getElementById("findText").value;
      const replace = document.getElementById("replaceText").value;
      if (!find) return;
      const editor = document.getElementById("editor");
      const regex = new RegExp(find, 'gi');
      editor.innerHTML = editor.innerHTML.replace(regex, replace);
      updateHTML();
    }

    document.addEventListener('keydown', function(event) {
      if ((event.ctrlKey || event.metaKey) && !event.shiftKey) {
        if (event.key === 'b' || event.key === 'i' || event.key === 'u') {
          event.preventDefault();
          execCmd({ b: 'bold', i: 'italic', u: 'underline' }[event.key]);
        }
      }
    });
  </script>
</body>
</html>
"""

components.html(html_content, height=800, scrolling=True)
