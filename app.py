import streamlit as st
import streamlit.components.v1 as components

# Configura la pagina in modalità wide
st.set_page_config(
    page_title="WYSIWYG HTML Editor",
    layout="wide",
)

# HTML/CSS/JS del WYSIWYG editor
html_content = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WYSIWYG HTML Editor</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: white; color: #333; }
    .container { width: 100%; margin: 0 auto; padding: 20px; }
    .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #000; padding-bottom: 10px; }
    .toolbar { background: #f5f5f5; padding: 10px; border: 1px solid #ddd; border-radius: 5px; display: flex; flex-wrap: wrap; gap: 5px; align-items: center; }
    .toolbar button, .toolbar select, .toolbar input[type="color"] { font-size: 12px; }
    .divider { width: 100%; height: 2px; background: #000; margin: 15px 0; }
    .editor-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; height: 600px; }
    .editor-panel { border: 1px solid #ddd; border-radius: 5px; display: flex; flex-direction: column; overflow: hidden; }
    .panel-header { background: #f0f0f0; padding: 10px; font-weight: bold; border-bottom: 1px solid #ddd; }
    .editor, .html-editor { flex: 1; width: 100%; padding: 15px; border: none; outline: none; font-family: inherit; font-size: 14px; line-height: 1.6; background: white; overflow-y: auto; }
    .html-editor { font-family: Consolas, 'Courier New', monospace; background: #f8f8f8; white-space: pre-wrap; overflow-wrap: break-word; border: 1px solid #ddd; resize: none; }
    .table-controls { display: none; position: fixed; background: white; border: 2px solid #007acc; padding: 15px; border-radius: 5px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 1000; min-width: 250px; }
    .table-controls label, .table-controls input { display: block; width: 100%; margin-bottom: 8px; }
    .table-controls button { margin-right: 5px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>WYSIWYG HTML Editor</h1>
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
    </div>
    <div class="divider"></div>
    <div class="editor-container">
      <div class="editor-panel">
        <div class="panel-header">Visual</div>
        <div id="editor" class="editor" contenteditable="true"
             oninput="updateHTML()"
             onkeyup="updateHTML()"
             onclick="handleTableSelection(event)"
             onpaste="handlePaste(event)">
          <h2>Inizia a scrivere...</h2>
        </div>
      </div>
      <div class="editor-panel">
        <div class="panel-header">HTML</div>
        <textarea id="htmlEditor" class="html-editor"
                  oninput="updateVisual()"
                  onkeyup="updateVisual()"
                  placeholder="Codice HTML pulito..."></textarea>
      </div>
    </div>
    <input type="file" id="fileInput" accept=".html,.txt" style="display:none" onchange="loadFile(event)">
    <div class="table-controls" id="tableControls">
      <label>Width (px or %):<input type="text" id="tableWidth"></label>
      <label>Border (px):<input type="number" id="tableBorder" min="0"></label>
      <label>Cellspacing (px):<input type="number" id="tableCellSpacing" min="0"></label>
      <label>Cellpadding (px):<input type="number" id="tableCellPadding" min="0"></label>
      <button onclick="applyTableSettings()">Apply</button>
      <button onclick="closeTableControls()">Close</button>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/js-beautify@1.14.0/js/lib/beautify-html.js"></script>
  <script>
    let selectedTable = null;
    function execCmd(cmd, val=null) {
      document.execCommand(cmd, false, val);
      updateHTML();
    }
    function stripAttrs(html) {
      return html.replace(/\s*(?:class|style|id)=(?:"[^"]*"|'[^']*')/g, '');
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
      let rows = prompt('Rows','3'), cols = prompt('Cols','3');
      if(rows&&cols) {
        let tbl = '<table border="1" cellpadding="8" cellspacing="0">';
        for(let r=0;r<rows;r++){ tbl+='<tr>'; for(let c=0;c<cols;c++) tbl+='<td>Cell</td>'; tbl+='</tr>'; }
        tbl+='</table>';
        execCmd('insertHTML', tbl);
      }
    }
    function insertLink() {
      let url=prompt('URL','https://'), txt=prompt('Text','Link');
      if(url) execCmd('insertHTML', `<a href="${url}" target="_blank">${txt}</a>`);
    }
    function insertImage() {
      let url=prompt('Image URL',''), alt=prompt('Alt','');
      if(url) execCmd('insertHTML', `<img src="${url}" alt="${alt}" style="max-width:100%;height:auto;">`);
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
    function handleTableSelection(e) {
      document.querySelectorAll('table.selected').forEach(t=>t.classList.remove('selected'));
      let t = e.target.closest('table');
      if(t) { selectedTable = t; t.classList.add('selected'); showTableControls(e); }
      else { selectedTable=null; closeTableControls(); }
    }
    function showTableControls(e) {
      const ctl = document.getElementById('tableControls');
      ctl.style.display='block'; ctl.style.left=e.pageX+'px'; ctl.style.top=e.pageY+'px';
      document.getElementById('tableWidth').value = selectedTable.getAttribute('width')||selectedTable.style.width||'';
      document.getElementById('tableBorder').value = selectedTable.getAttribute('border')||1;
      document.getElementById('tableCellSpacing').value = selectedTable.getAttribute('cellspacing')||0;
      document.getElementById('tableCellPadding').value = selectedTable.getAttribute('cellpadding')||8;
    }
    function applyTableSettings() {
      if(!selectedTable) return;
      selectedTable.style.width = document.getElementById('tableWidth').value;
      selectedTable.setAttribute('border', document.getElementById('tableBorder').value);
      selectedTable.setAttribute('cellspacing', document.getElementById('tableCellSpacing').value);
      selectedTable.setAttribute('cellpadding', document.getElementById('tableCellPadding').value);
      updateHTML(); closeTableControls();
    }
    function closeTableControls() { document.getElementById('tableControls').style.display='none'; if(selectedTable) selectedTable.classList.remove('selected'); }
    function handlePaste(e){ setTimeout(updateHTML,10); }
    function pasteAsPlainText(){ navigator.clipboard.readText().then(t=>execCmd('insertText',t)).catch(_=>{ let t=prompt('Paste text'); execCmd('insertText',t); }); }
    document.addEventListener('keydown', function(event) {
      if ((event.ctrlKey||event.metaKey)&&!event.shiftKey) {
        if (event.key==='b'||event.key==='i'||event.key==='u') {
          event.preventDefault(); execCmd({b:'bold',i:'italic',u:'underline'}[event.key]); }
      }
    });
  </script>
</body>
</html>
"""

# Inietta il componente HTML in Streamlit
components.html(html_content, height=800, scrolling=True)
