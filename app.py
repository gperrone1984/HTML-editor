import streamlit as st
import streamlit.components.v1 as components

# Configure the Streamlit page
st.set_page_config(
    page_title="WYSIWYG HTML Editor",
    layout="wide",
)

# The HTML/CSS/JS for the editor
html_content = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WYSIWYG HTML Editor</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #fff; color: #333; }
    .container { padding: 20px; }
    .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #000; padding-bottom: 10px; }
    .toolbar { background: #f5f5f5; padding: 10px; border: 1px solid #ddd; border-radius: 5px; display: flex; flex-wrap: wrap; gap: 5px; }
    .toolbar button, .toolbar select, .toolbar input[type="color"] { font-size: 12px; cursor: pointer; }
    .divider { height: 2px; background: #000; margin: 15px 0; }
    .editor-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; height: 600px; }
    .editor-panel { border: 1px solid #ddd; border-radius: 5px; display: flex; flex-direction: column; }
    .panel-header { background: #f0f0f0; padding: 10px; font-weight: bold; border-bottom: 1px solid #ddd; }
    .editor, .html-editor { flex: 1; padding: 15px; outline: none; font-size: 14px; line-height: 1.6; overflow-y: auto; }
    .editor { border: none; }
    .html-editor { border: 1px solid #ddd; background: #f8f8f8; font-family: Consolas, 'Courier New', monospace; white-space: pre-wrap; }
    .table-controls { display: none; position: fixed; background: #fff; border: 2px solid #007acc; padding: 15px; border-radius: 5px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 1000; width: 260px; }
    .table-controls label { margin-bottom: 5px; font-weight: bold; display: block; }
    .table-controls input { width: 100%; margin-bottom: 10px; padding: 5px; border: 1px solid #ccc; border-radius: 3px; }
    .table-controls button { margin-right: 5px; padding: 8px 12px; border: none; border-radius: 3px; color: #fff; background: #007acc; cursor: pointer; }
    .table-controls button:hover { background: #005999; }
    .table-controls .close-btn { background: #ccc; color: #333; }
    table.selected { outline: 2px solid #007acc; background: rgba(0,122,204,0.1); }
  </style>
</head>
<body>
  <div class="container">
    <div class="header"><h1>WYSIWYG HTML Editor</h1></div>

    <div class="toolbar">
      <button onclick="execCmd('bold')"><b>B</b></button>
      <button onclick="execCmd('italic')"><i>I</i></button>
      <button onclick="execCmd('underline')"><u>U</u></button>
      <button onclick="execCmd('strikeThrough')"><s>S</s></button>
      <select onchange="execCmd('formatBlock', this.value)">
        <option value="">Format</option>
        <option value="h1">H1</option>
        <option value="h2">H2</option>
        <option value="p">Paragraph</option>
      </select>
      <button onclick="execCmd('insertUnorderedList')">&bull; List</button>
      <button onclick="execCmd('insertOrderedList')">1. List</button>
      <input type="color" title="Text color" onchange="execCmd('foreColor', this.value)">
      <input type="color" title="Background color" onchange="execCmd('backColor', this.value)">
      <button onclick="insertTable()">Table</button>
      <button onclick="insertLink()">Link</button>
      <button onclick="insertImage()">Image</button>
      <button onclick="execCmd('removeFormat')">Clear</button>
      <button onclick="pasteAsPlainText()">Paste Plain</button>
      <button onclick="execCmd('undo')">&#x21B6;</button>
      <button onclick="execCmd('redo')">&#x21B7;</button>
      <button onclick="openFile()">Open File</button>
    </div>

    <div class="divider"></div>

    <div class="editor-container">
      <div class="editor-panel">
        <div class="panel-header">Visual</div>
        <div id="editor" class="editor" contenteditable="true"
             oninput="updateHTML()" onkeyup="updateHTML()"
             onclick="handleTableSelection(event)" onpaste="handlePaste(event)">
          <h2>Start typing...</h2>
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

    <div id="tableControls" class="table-controls">
      <label>Width (px):</label>
      <input type="number" id="tableWidth" min="50" placeholder="e.g. 500">
      <label>Border (px):</label>
      <input type="number" id="tableBorder" min="0" value="1">
      <label>Cell Spacing (px):</label>
      <input type="number" id="tableCellSpacing" min="0" value="0">
      <label>Cell Padding (px):</label>
      <input type="number" id="tableCellPadding" min="0" value="8">
      <button onclick="applyTableSettings()">Apply</button>
      <button class="close-btn" onclick="closeTableControls()">Close</button>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/js-beautify@1.14.0/js/lib/beautify-html.js"></script>
  <script>
    let selectedTable = null;
    let isUpdating = false;

    function execCmd(cmd, val = null) {
      document.execCommand(cmd, false, val);
      updateHTML();
    }

    function stripAttrs(html) {
      return html.replace(/\s*(?:class|style|id)=(?:"[^"]*"|'[^']*')/g, '');
    }

    function updateHTML() {
      if (isUpdating) return;
      isUpdating = true;
      const raw = stripAttrs(document.getElementById('editor').innerHTML);
      document.getElementById('htmlEditor').value =
        html_beautify(raw, { indent_size: 2, wrap_line_length: 80 });
      setTimeout(() => isUpdating = false, 10);
    }

    function updateVisual() {
      if (isUpdating) return;
      isUpdating = true;
      document.getElementById('editor').innerHTML =
        document.getElementById('htmlEditor').value;
      setTimeout(() => isUpdating = false, 10);
    }

    function insertTable() {
      let rows = prompt('Number of rows:', '3');
      let cols = prompt('Number of columns:', '3');
      if (rows && cols) {
        let tbl = '<table border="1" cellpadding="8" cellspacing="0" style="width:100%;border-collapse:collapse;">';
        for (let r = 0; r < rows; r++) {
          tbl += '<tr>';
          for (let c = 0; c < cols; c++) {
            tbl += `<td style="border:1px solid #ccc;padding:8px;">Cell ${r+1},${c+1}</td>`;
          }
          tbl += '</tr>';
        }
        tbl += '</table>';
        execCmd('insertHTML', tbl);
      }
    }

    function insertLink() {
      let url = prompt('URL:', 'https://');
      let txt = prompt('Link text:', 'Link');
      if (url) execCmd('insertHTML', `<a href="${url}" target="_blank">${txt}</a>`);
    }

    function insertImage() {
      let url = prompt('Image URL:', '');
      let alt = prompt('Alt text:', '');
      if (url) execCmd('insertHTML', `<img src="${url}" alt="${alt}" style="max-width:100%;height:auto;">`);
    }

    function pasteAsPlainText() {
      if (navigator.clipboard && navigator.clipboard.readText) {
        navigator.clipboard.readText().then(text => execCmd('insertText', text))
          .catch(() => {
            let text = prompt('Paste text:');
            if (text) execCmd('insertText', text);
          });
      } else {
        let text = prompt('Paste text:');
        if (text) execCmd('insertText', text);
      }
    }

    function openFile() {
      document.getElementById('fileInput').click();
    }

    function loadFile(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = e => {
        document.getElementById('editor').innerHTML = e.target.result;
        updateHTML();
      };
      reader.readAsText(file);
    }

    function handleTableSelection(e) {
      document.querySelectorAll('table.selected').forEach(t => t.classList.remove('selected'));
      let table = e.target.closest('table');
      if (table) {
        selectedTable = table;
        table.classList.add('selected');
        showTableControls(e);
      } else {
        selectedTable = null;
        closeTableControls();
      }
    }

    function showTableControls(e) {
      const controls = document.getElementById('tableControls');
      controls.style.display = 'block';
      controls.style.left = Math.min(e.pageX + 10, window.innerWidth - 280) + 'px';
      controls.style.top = Math.min(e.pageY + 10, window.innerHeight - 250) + 'px';
      controls.querySelector('#tableWidth').value = parseInt(selectedTable.style.width) || '';
      controls.querySelector('#tableBorder').value = selectedTable.getAttribute('border') || 1;
      controls.querySelector('#tableCellSpacing').value = selectedTable.getAttribute('cellspacing') || 0;
      controls.querySelector('#tableCellPadding').value = selectedTable.getAttribute('cellpadding') || 8;
    }

    function applyTableSettings() {
      if (!selectedTable) return;
      const w = document.getElementById('tableWidth').value;
      const b = document.getElementById('tableBorder').value;
      const cs = document.getElementById('tableCellSpacing').value;
      const cp = document.getElementById('tableCellPadding').value;
      if (w) {
        selectedTable.style.width = w + 'px';
        selectedTable.setAttribute('width', w);
      }
      selectedTable.setAttribute('border', b);
      selectedTable.setAttribute('cellspacing', cs);
      selectedTable.setAttribute('cellpadding', cp);
      selectedTable.querySelectorAll('td, th').forEach(cell => {
        cell.style.padding = cp + 'px';
      });
      updateHTML();
      closeTableControls();
    }

    function closeTableControls() {
      document.getElementById('tableControls').style.display = 'none';
      if (selectedTable) selectedTable.classList.remove('selected');
      selectedTable = null;
    }

    function handlePaste(e) {
      setTimeout(updateHTML, 10);
    }

    document.addEventListener('keydown', function(event) {
      if ((event.ctrlKey || event.metaKey) && !event.shiftKey) {
        const map = { 'b': 'bold', 'i': 'italic', 'u': 'underline' };
        if (map[event.key]) {
          event.preventDefault();
          execCmd(map[event.key]);
        }
      }
    });

    document.addEventListener('click', function(e) {
      const controls = document.getElementById('tableControls');
      if (!controls.contains(e.target) && !e.target.closest('table') && controls.style.display === 'block') {
        closeTableControls();
      }
    });

    // Initial sync
    setTimeout(() => { updateHTML(); }, 100);
  </script>
</body>
</html>
"""

# Inject the HTML into Streamlit
components.html(html_content, height=800, scrolling=True)
