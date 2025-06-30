import streamlit as st
import streamlit.components.v1 as components

# Configure page layout
st.set_page_config(
    page_title="WYSIWYG HTML Editor",
    layout="wide",
)

# HTML/CSS/JS for the WYSIWYG editor
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
    .toolbar button, .toolbar select, .toolbar input[type="color"] { font-size: 12px; }
    .divider { width: 100%; height: 2px; background: #000; margin: 15px 0; }
    .editor-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; height: 600px; }
    .editor-panel { border: 1px solid #ddd; border-radius: 5px; display: flex; flex-direction: column; overflow: hidden; }
    .panel-header { background: #f0f0f0; padding: 10px; font-weight: bold; border-bottom: 1px solid #ddd; }
    .editor, .html-editor { flex: 1; width: 100%; padding: 15px; border: none; outline: none; font-family: inherit; font-size: 14px; line-height: 1.6; background: #fff; overflow-y: auto; }
    .html-editor { font-family: Consolas, 'Courier New', monospace; background: #f8f8f8; white-space: pre-wrap; overflow-wrap: break-word; border: 1px solid #ddd; resize: none; }
    .table-controls { display: none; position: fixed; background: #fff; border: 2px solid #007acc; padding: 15px; border-radius: 5px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 1000; min-width: 250px; }
    .table-controls label { display: block; margin-bottom: 5px; font-weight: bold; }
    .table-controls input { width: 100%; padding: 5px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 3px; }
    .table-controls button { margin-right: 5px; padding: 8px 12px; background: #007acc; color: #fff; border: none; border-radius: 3px; cursor: pointer; }
    .table-controls button:hover { background: #005999; }
    .table-controls .close-btn { background: #ccc; color: #333; }
    .table-controls .close-btn:hover { background: #999; }
    
    /* Highlight selected table */
    table.selected { outline: 2px solid #007acc; background-color: rgba(0, 122, 204, 0.1); }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>WYSIWYG HTML Editor</h1>
    </div>
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
             onclick="handleTableSelection(event)" onmouseup="handleSelectionChange()"
             onpaste="handlePaste(event)">
          <h2>Start typing...</h2>
        </div>
      </div>
      <div class="editor-panel">
        <div class="panel-header">HTML</div>
        <textarea id="htmlEditor" class="html-editor"
                  oninput="updateVisual()" onkeyup="updateVisual()"
                  onselect="handleHTMLSelection()"
                  placeholder="Clean HTML code..."></textarea>
      </div>
    </div>
    <input type="file" id="fileInput" accept=".html,.txt" style="display:none" onchange="loadFile(event)">
    
    <!-- Table settings panel -->
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
    let selectedTable = null;
    let isUpdating = false;
    
    // Execute formatting commands
    function execCmd(cmd, val = null) {
      document.execCommand(cmd, false, val);
      updateHTML();
    }
    
    // Strip class/style/id attributes for clean HTML
    function stripAttrs(html) {
      return html.replace(/\s*(?:class|style|id)=(?:"[^"]*"|'[^']*')/g, '');
    }
    
    // Update HTML panel from Visual editor
    function updateHTML() {
      if (isUpdating) return;
      isUpdating = true;
      
      const raw = stripAttrs(document.getElementById('editor').innerHTML);
      const formatted = html_beautify(raw, { indent_size: 2, wrap_line_length: 80 });
      document.getElementById('htmlEditor').value = formatted;
      
      setTimeout(() => isUpdating = false, 10);
    }
    
    // Update Visual editor from HTML panel
    function updateVisual() {
      if (isUpdating) return;
      isUpdating = true;
      
      document.getElementById('editor').innerHTML = document.getElementById('htmlEditor').value;
      setTimeout(() => isUpdating = false, 10);
    }
    
    // When text is selected in Visual, highlight it in the HTML textarea
    function handleSelectionChange() {
      if (isUpdating) return;
      const sel = window.getSelection();
      if (!sel.rangeCount || sel.isCollapsed) return;
      const text = sel.toString().trim();
      if (text.length < 2) return;
      highlightInHTML(text);
    }
    
    // When HTML is selected, highlight it in the Visual editor
    function handleHTMLSelection() {
      if (isUpdating) return;
      const ta = document.getElementById('htmlEditor');
      const start = ta.selectionStart, end = ta.selectionEnd;
      if (start === end) return;
      const selectedHTML = ta.value.substring(start, end).trim();
      const temp = document.createElement('div');
      temp.innerHTML = selectedHTML;
      const text = temp.textContent || temp.innerText || '';
      if (text.trim()) highlightInVisual(text.trim());
    }
    
    // Highlight matching text in HTML textarea
    function highlightInHTML(searchText) {
      const ta = document.getElementById('htmlEditor');
      const lower = ta.value.toLowerCase();
      const idx = lower.indexOf(searchText.toLowerCase());
      if (idx !== -1) {
        ta.focus();
        ta.setSelectionRange(idx, idx + searchText.length);
      }
    }
    
    // Highlight matching text in Visual editor
    function highlightInVisual(searchText) {
      const editor = document.getElementById('editor');
      const walker = document.createTreeWalker(editor, NodeFilter.SHOW_TEXT, null, false);
      let node;
      while (node = walker.nextNode()) {
        const txt = node.textContent.toLowerCase();
        const idx = txt.indexOf(searchText.toLowerCase());
        if (idx !== -1) {
          const range = document.createRange();
          range.setStart(node, idx);
          range.setEnd(node, idx + searchText.length);
          const sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(range);
          break;
        }
      }
    }
    
    // Insert a table
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
    
    // Insert a link
    function insertLink() {
      let url = prompt('URL:', 'https://');
      let txt = prompt('Link text:', 'Link');
      if (url) execCmd('insertHTML', `<a href="${url}" target="_blank">${txt}</a>`);
    }
    
    // Insert an image
    function insertImage() {
      let url = prompt('Image URL:', '');
      let alt = prompt('Alt text:', '');
      if (url) execCmd('insertHTML', `<img src="${url}" alt="${alt}" style="max-width:100%;height:auto;">`);
    }
    
    // Open local file
    function openFile() {
      document.getElementById('fileInput').click();
    }
    function loadFile(e) {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = evt => {
        document.getElementById('editor').innerHTML = evt.target.result;
        updateHTML();
      };
      reader.readAsText(file);
    }
    
    // Table selection & settings
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
      const ctl = document.getElementById('tableControls');
      ctl.style.display = 'block';
      ctl.style.left = Math.min(e.pageX + 10, window.innerWidth - 280) + 'px';
      ctl.style.top = Math.min(e.pageY + 10, window.innerHeight - 250) + 'px';
      if (selectedTable) {
        document.getElementById('tableWidth').value = parseInt(selectedTable.style.width) || '';
        document.getElementById('tableBorder').value = selectedTable.getAttribute('border') || 1;
        document.getElementById('tableCellSpacing').value = selectedTable.getAttribute('cellspacing') || 0;
        document.getElementById('tableCellPadding').value = selectedTable.getAttribute('cellpadding') || 8;
      }
    }
    function applyTableSettings() {
      if (!selectedTable) return;
      const w = document.getElementById('tableWidth').value;
      if (w) {
        selectedTable.style.width = w + 'px';
        selectedTable.setAttribute('width', w);
      }
      selectedTable.setAttribute('border', document.getElementById('tableBorder').value);
      selectedTable.setAttribute('cellspacing', document.getElementById('tableCellSpacing').value);
      selectedTable.setAttribute('cellpadding', document.getElementById('tableCellPadding').value);
      selectedTable.querySelectorAll('td, th').forEach(cell => {
        cell.style.padding = document.getElementById('tableCellPadding').value + 'px';
      });
      updateHTML();
      closeTableControls();
    }
    function closeTableControls() {
      document.getElementById('tableControls').style.display = 'none';
      if (selectedTable) selectedTable.classList.remove('selected');
      selectedTable = null;
    }
    
    // Handle paste events
    function handlePaste(e) {
      setTimeout(updateHTML, 10);
    }
    function pasteAsPlainText() {
      if (navigator.clipboard && navigator.clipboard.readText) {
        navigator.clipboard.readText().then(txt => execCmd('insertText', txt))
          .catch(() => {
            let t = prompt('Paste text:');
            if (t) execCmd('insertText', t);
          });
      } else {
        let t = prompt('Paste text:');
        if (t) execCmd('insertText', t);
      }
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(event) {
      if ((event.ctrlKey || event.metaKey) && !event.shiftKey) {
        const map = { 'b':'bold', 'i':'italic', 'u':'underline' };
        if (map[event.key]) {
          event.preventDefault();
          execCmd(map[event.key]);
        }
      }
    });
    
    // Close table controls when clicking outside
    document.addEventListener('click', function(e) {
      const ctl = document.getElementById('tableControls');
      if (!ctl.contains(e.target) && !e.target.closest('table') && ctl.style.display==='block') {
        closeTableControls();
      }
    });
    
    // Initialize
    setTimeout(updateHTML, 100);
  </script>
</body>
</html>
"""

# Inject the HTML component into Streamlit
components.html(html_content, height=800, scrolling=True)
