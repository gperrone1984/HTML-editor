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
    .table-controls label { display: block; margin-bottom: 5px; font-weight: bold; }
    .table-controls input { width: 100%; padding: 5px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 3px; }
    .table-controls button { margin-right: 5px; padding: 8px 12px; background: #007acc; color: white; border: none; border-radius: 3px; cursor: pointer; }
    .table-controls button:hover { background: #005999; }
    .table-controls .close-btn { background: #ccc; color: #333; }
    .table-controls .close-btn:hover { background: #999; }
    
    /* Stili per tabella selezionata */
    table.selected { outline: 2px solid #007acc; background-color: rgba(0, 122, 204, 0.1); }
    
    /* Evidenziazione selezione */
    .html-highlight { background-color: #ffff99; }
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
             onmouseup="handleSelectionChange()"
             onpaste="handlePaste(event)">
          <h2>Inizia a scrivere...</h2>
        </div>
      </div>
      <div class="editor-panel">
        <div class="panel-header">HTML</div>
        <textarea id="htmlEditor" class="html-editor"
                  oninput="updateVisual()"
                  onkeyup="updateVisual()"
                  onselect="handleHTMLSelection()"
                  placeholder="Codice HTML pulito..."></textarea>
      </div>
    </div>
    <input type="file" id="fileInput" accept=".html,.txt" style="display:none" onchange="loadFile(event)">
    
    <!-- Controlli tabella -->
    <div class="table-controls" id="tableControls">
      <label>Larghezza (px):</label>
      <input type="number" id="tableWidth" min="50" placeholder="es. 500">
      
      <label>Bordo (px):</label>
      <input type="number" id="tableBorder" min="0" value="1">
      
      <label>Spaziatura celle (px):</label>
      <input type="number" id="tableCellSpacing" min="0" value="0">
      
      <label>Padding celle (px):</label>
      <input type="number" id="tableCellPadding" min="0" value="8">
      
      <button onclick="applyTableSettings()">Applica</button>
      <button class="close-btn" onclick="closeTableControls()">Chiudi</button>
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
      
      let raw = stripAttrs(document.getElementById('editor').innerHTML);
      let formatted = html_beautify(raw, { indent_size: 2, wrap_line_length: 80 });
      document.getElementById('htmlEditor').value = formatted;
      
      setTimeout(() => { isUpdating = false; }, 10);
    }
    
    function updateVisual() {
      if (isUpdating) return;
      isUpdating = true;
      
      document.getElementById('editor').innerHTML = document.getElementById('htmlEditor').value;
      
      setTimeout(() => { isUpdating = false; }, 10);
    }
    
    // Gestione selezione sincronizzata
    function handleSelectionChange() {
      if (isUpdating) return;
      
      const selection = window.getSelection();
      if (selection.rangeCount === 0 || selection.isCollapsed) return;
      
      const selectedText = selection.toString().trim();
      if (selectedText.length < 2) return;
      
      // Trova e evidenzia nel HTML
      highlightInHTML(selectedText);
    }
    
    function handleHTMLSelection() {
      if (isUpdating) return;
      
      const htmlEditor = document.getElementById('htmlEditor');
      const start = htmlEditor.selectionStart;
      const end = htmlEditor.selectionEnd;
      
      if (start === end) return;
      
      const selectedHTML = htmlEditor.value.substring(start, end).trim();
      if (selectedHTML.length < 2) return;
      
      // Estrai il testo dal HTML selezionato
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = selectedHTML;
      const textContent = tempDiv.textContent || tempDiv.innerText || '';
      
      if (textContent.trim().length > 0) {
        highlightInVisual(textContent.trim());
      }
    }
    
    function highlightInHTML(searchText) {
      const htmlEditor = document.getElementById('htmlEditor');
      const htmlContent = htmlEditor.value.toLowerCase();
      const searchLower = searchText.toLowerCase();
      
      const index = htmlContent.indexOf(searchLower);
      if (index !== -1) {
        htmlEditor.focus();
        htmlEditor.setSelectionRange(index, index + searchText.length);
      }
    }
    
    function highlightInVisual(searchText) {
      const editor = document.getElementById('editor');
      const selection = window.getSelection();
      
      // Cerca il testo nell'editor visuale
      const walker = document.createTreeWalker(
        editor,
        NodeFilter.SHOW_TEXT,
        null,
        false
      );
      
      let node;
      while (node = walker.nextNode()) {
        const nodeText = node.textContent.toLowerCase();
        const searchLower = searchText.toLowerCase();
        const index = nodeText.indexOf(searchLower);
        
        if (index !== -1) {
          const range = document.createRange();
          range.setStart(node, index);
          range.setEnd(node, index + searchText.length);
          
          selection.removeAllRanges();
          selection.addRange(range);
          break;
        }
      }
    }
    
    function insertTable() {
      let rows = prompt('Numero di righe:', '3');
      let cols = prompt('Numero di colonne:', '3');
      if (rows && cols) {
        let tbl = '<table border="1" cellpadding="8" cellspacing="0" style="width: 100%; border-collapse: collapse;">';
        for (let r = 0; r < rows; r++) {
          tbl += '<tr>';
          for (let c = 0; c < cols; c++) {
            tbl += '<td style="border: 1px solid #ccc; padding: 8px;">Cella ' + (r + 1) + ',' + (c + 1) + '</td>';
          }
          tbl += '</tr>';
        }
        tbl += '</table>';
        execCmd('insertHTML', tbl);
      }
    }
    
    function insertLink() {
      let url = prompt('URL:', 'https://');
      let txt = prompt('Testo del link:', 'Link');
      if (url) execCmd('insertHTML', `<a href="${url}" target="_blank">${txt}</a>`);
    }
    
    function insertImage() {
      let url = prompt('URL immagine:', '');
      let alt = prompt('Testo alternativo:', '');
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
    
    // Gestione tabelle
    function handleTableSelection(e) {
      // Rimuovi selezione precedente
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
      
      if (selectedTable) {
        // Carica valori correnti
        const currentWidth = selectedTable.style.width || selectedTable.getAttribute('width') || '';
        const widthValue = parseInt(currentWidth) || '';
        
        document.getElementById('tableWidth').value = widthValue;
        document.getElementById('tableBorder').value = selectedTable.getAttribute('border') || 1;
        document.getElementById('tableCellSpacing').value = selectedTable.getAttribute('cellspacing') || 0;
        document.getElementById('tableCellPadding').value = selectedTable.getAttribute('cellpadding') || 8;
      }
    }
    
    function applyTableSettings() {
      if (!selectedTable) return;
      
      // Applica larghezza
      const widthValue = document.getElementById('tableWidth').value;
      if (widthValue) {
        selectedTable.style.width = widthValue + 'px';
        selectedTable.setAttribute('width', widthValue);
      }
      
      // Applica altri attributi
      const border = document.getElementById('tableBorder').value;
      const cellspacing = document.getElementById('tableCellSpacing').value;
      const cellpadding = document.getElementById('tableCellPadding').value;
      
      selectedTable.setAttribute('border', border);
      selectedTable.setAttribute('cellspacing', cellspacing);
      selectedTable.setAttribute('cellpadding', cellpadding);
      
      // Applica padding alle celle
      const cells = selectedTable.querySelectorAll('td, th');
      cells.forEach(cell => {
        cell.style.padding = cellpadding + 'px';
      });
      
      updateHTML();
      closeTableControls();
    }
    
    function closeTableControls() {
      document.getElementById('tableControls').style.display = 'none';
      if (selectedTable) {
        selectedTable.classList.remove('selected');
        selectedTable = null;
      }
    }
    
    function handlePaste(e) {
      setTimeout(updateHTML, 10);
    }
    
    function pasteAsPlainText() {
      if (navigator.clipboard && navigator.clipboard.readText) {
        navigator.clipboard.readText().then(text => {
          execCmd('insertText', text);
        }).catch(_ => {
          let text = prompt('Incolla il testo:');
          if (text) execCmd('insertText', text);
        });
      } else {
        let text = prompt('Incolla il testo:');
        if (text) execCmd('insertText', text);
      }
    }
    
    // Scorciatoie da tastiera
    document.addEventListener('keydown', function(event) {
      if ((event.ctrlKey || event.metaKey) && !event.shiftKey) {
        const shortcuts = {
          'b': 'bold',
          'i': 'italic',
          'u': 'underline'
        };
        
        if (shortcuts[event.key]) {
          event.preventDefault();
          execCmd(shortcuts[event.key]);
        }
      }
    });
    
    // Chiudi controlli tabella quando si clicca fuori
    document.addEventListener('click', function(e) {
      const controls = document.getElementById('tableControls');
      if (!controls.contains(e.target) && !e.target.closest('table') && controls.style.display === 'block') {
        closeTableControls();
      }
    });
    
    // Inizializza
    setTimeout(() => {
      updateHTML();
    }, 100);
  </script>
</body>
</html>
"""

# Inietta il componente HTML in Streamlit
components.html(html_content, height=800, scrolling=True)
