import streamlit as st
import streamlit.components.v1 as components

# Configure page layout
st.set_page_config(
    page_title="WYSIWYG HTML Editor",
    layout="wide",
)

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
    .container { width: 100%; margin: 0 auto; padding: 20px; }
    .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #000; padding-bottom: 10px; }
    .toolbar { background: #f5f5f5; padding: 10px; border: 1px solid #ddd; border-radius: 5px; display: flex; flex-wrap: wrap; gap: 5px; align-items: center; }
    .toolbar button, .toolbar select, .toolbar input[type="color"] { font-size: 12px; cursor: pointer; }
    .divider { width: 100%; height: 2px; background: #000; margin: 15px 0; }
    .editor-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; height: 600px; }
    .editor-panel { border: 1px solid #ddd; border-radius: 5px; display: flex; flex-direction: column; overflow: hidden; }
    .panel-header { background: #f0f0f0; padding: 10px; font-weight: bold; border-bottom: 1px solid #ddd; }
    .editor, .html-editor { flex: 1; width: 100%; padding: 15px; border: none; outline: none; font-family: inherit; font-size: 14px; line-height: 1.6; background: #fff; overflow-y: auto; }
    .html-editor { font-family: Consolas, 'Courier New', monospace; background: #f8f8f8; white-space: pre-wrap; overflow-wrap: break-word; border: 1px solid #ddd; resize: none; user-select: text; }
    .table-controls { display: none; position: fixed; background: #fff; border: 2px solid #007acc; padding: 15px; border-radius: 5px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 1000; min-width: 250px; }
    .table-controls label { display: block; margin-bottom: 5px; font-weight: bold; }
    .table-controls input { width: 100%; padding: 5px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 3px; }
    .table-controls button { margin-right: 5px; padding: 8px 12px; background: #007acc; color: #fff; border: none; border-radius: 3px; cursor: pointer; }
    .table-controls button:hover { background: #005999; }
    .table-controls .close-btn { background: #ccc; color: #333; }
    .table-controls .close-btn:hover { background: #999; }
    table.selected { outline: 2px solid #007acc; background-color: rgba(0, 122, 204, 0.1); }
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
    <div class="table-controls" id="tableControls">
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
    let selectedTable = null, isUpdating = false;

    function execCmd(cmd, val=null) {
      document.execCommand(cmd, false, val);
      updateHTML();
    }
    function stripAttrs(html) {
      return html.replace(/\s*(?:class|style|id)=(?:"[^"]*"|'[^']*')/g, '');
    }
    function updateHTML() {
      if(isUpdating) return;
      isUpdating = true;
      const raw = stripAttrs(editor.innerHTML);
      htmlEditor.value = html_beautify(raw, { indent_size:2, wrap_line_length:80 });
      setTimeout(()=>isUpdating=false,10);
    }
    function updateVisual() {
      if(isUpdating) return;
      isUpdating = true;
      editor.innerHTML = htmlEditor.value;
      setTimeout(()=>isUpdating=false,10);
    }

    // Listen for any text selection change
    document.addEventListener('selectionchange', () => {
      const sel = window.getSelection();
      // Only act when selection is inside the visual editor
      if(!sel.rangeCount) return;
      const container = sel.getRangeAt(0).commonAncestorContainer;
      if(!editor.contains(container)) return;
      if(sel.isCollapsed) return;
      const text = sel.toString().trim();
      if(text.length < 2) return;
      highlightInHTML(text);
    });

    function highlightInHTML(searchText) {
      const lower = htmlEditor.value.toLowerCase();
      const idx = lower.indexOf(searchText.toLowerCase());
      if(idx !== -1) {
        htmlEditor.focus();
        htmlEditor.setSelectionRange(idx, idx + searchText.length);
      }
    }

    function highlightInVisual(searchText) {
      // (kept for HTML→Visual sync; not needed for this fix)
    }

    function insertTable() { /* same as before */ }
    function insertLink()  { /* ... */ }
    function insertImage() { /* ... */ }
    function openFile()    { fileInput.click(); }
    function loadFile(e) { /* ... */ }
    function handleTableSelection(e) { /* ... */ }
    function applyTableSettings() { /* ... */ }
    function closeTableControls() { /* ... */ }
    function handlePaste(e) { setTimeout(updateHTML,10); }
    function pasteAsPlainText() { /* ... */ }
    // keyboard shortcuts, click-outside logic, etc. remain unchanged

    // Initialize
    setTimeout(updateHTML, 100);
  </script>
</body>
</html>
"""

components.html(html_content, height=800, scrolling=True)
