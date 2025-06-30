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
    .table-controls { display: none; position: fixed; background: white; border: 2px solid #007acc; padding: 15px; border-radius: 5px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 1000; min-width: 280px; }
    .table-controls label { display: block; margin-bottom: 8px; font-weight: bold; }
    .table-controls input, .table-controls select { width: 100%; padding: 5px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 3px; }
    .table-controls button { margin-right: 5px; padding: 8px 12px; background: #007acc; color: white; border: none; border-radius: 3px; cursor: pointer; }
    .table-controls button:hover { background: #005999; }
    .table-controls .close-btn { background: #ccc; color: #333; }
    .table-controls .close-btn:hover { background: #999; }
    
    /* Stili per evidenziazione sincronizzata */
    .highlight-visual { background-color: rgba(255, 255, 0, 0.3) !important; }
    .highlight-html { background-color: rgba(255, 255, 0, 0.3); }
    
    /* Stili per tabella selezionata */
    table.selected { outline: 2px solid #007acc; background-color: rgba(0, 122, 204, 0.1); }
    
    /* Stili per resize handles */
    .resize-handle { position: absolute; background: #007acc; }
    .resize-handle.right { width: 4px; height: 100%; right: -2px; top: 0; cursor: col-resize; }
    .resize-handle.bottom { width: 100%; height: 4px; bottom: -2px; left: 0; cursor: row-resize; }
    .resize-handle.corner { width: 8px; height: 8px; right: -4px; bottom: -4px; cursor: nw-resize; }
    
    table { position: relative; }
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
             onselectionchange="handleSelectionChange()"
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
    
    <!-- Controlli tabella migliorati -->
    <div class="table-controls" id="tableControls">
      <label>Larghezza:</label>
      <select id="tableWidthType" onchange="toggleWidthInput()">
        <option value="px">Pixel (px)</option>
        <option value="%">Percentuale (%)</option>
        <option value="auto">Auto</option>
      </select>
      <input type="number" id="tableWidthValue" min="1" placeholder="Valore">
      
      <label>Altezza:</label>
      <select id="tableHeightType">
        <option value="px">Pixel (px)</option>
        <option value="auto">Auto</option>
      </select>
      <input type="number" id="tableHeightValue" min="1" placeholder="Valore">
      
      <label>Bordo (px):</label>
      <input type="number" id="tableBorder" min="0" value="1">
      
      <label>Spaziatura celle (px):</label>
      <input type="number" id="tableCellSpacing" min="0" value="0">
      
      <label>Padding celle (px):</label>
      <input type="number" id="tableCellPadding" min="0" value="8">
      
      <button onclick="applyTableSettings()">Applica</button>
      <button onclick="addTableRow()">+ Riga</button>
      <button onclick="addTableColumn()">+ Colonna</button>
      <button onclick="deleteTable()">Elimina</button>
      <button class="close-btn" onclick="closeTableControls()">Chiudi</button>
    </div>
  </div>
  
  <script src="https://cdn.jsdelivr.net/npm/js-beautify@1.14.0/js/lib/beautify-html.js"></script>
  <script>
    let selectedTable = null;
    let isUpdatingFromHTML = false;
    let isUpdatingFromVisual = false;
    
    function execCmd(cmd, val=null) {
      document.execCommand(cmd, false, val);
      updateHTML();
    }
    
    function stripAttrs(html) {
      return html.replace(/\s*(?:class|style|id)=(?:"[^"]*"|'[^']*')/g, '');
    }
    
    function updateHTML() {
      if (isUpdatingFromHTML) return;
      isUpdatingFromVisual = true;
      
      let raw = stripAttrs(document.getElementById('editor').innerHTML);
      let formatted = html_beautify(raw, { indent_size: 2, wrap_line_length: 80 });
      document.getElementById('htmlEditor').value = formatted;
      
      setTimeout(() => { isUpdatingFromVisual = false; }, 10);
    }
    
    function updateVisual() {
      if (isUpdatingFromVisual) return;
      isUpdatingFromHTML = true;
      
      document.getElementById('editor').innerHTML = document.getElementById('htmlEditor').value;
      
      setTimeout(() => { isUpdatingFromHTML = false; }, 10);
    }
    
    // Gestione selezione sincronizzata
    function handleSelectionChange() {
      if (isUpdatingFromHTML) return;
      
      const selection = window.getSelection();
      if (selection.rangeCount === 0) return;
      
      const range = selection.getRangeAt(0);
      const container = document.getElementById('editor');
      
      // Rimuovi evidenziazioni precedenti
      clearHighlights();
      
      if (range.collapsed) return;
      
      // Trova il testo selezionato
      const selectedText = range.toString().trim();
      if (selectedText.length === 0) return;
      
      // Evidenzia nel HTML
      highlightInHTML(selectedText);
    }
    
    function handleHTMLSelection() {
      const htmlEditor = document.getElementById('htmlEditor');
      const selectedText = htmlEditor.value.substring(htmlEditor.selectionStart, htmlEditor.selectionEnd).trim();
      
      clearHighlights();
      
      if (selectedText.length > 0) {
        highlightInVisual(selectedText);
      }
    }
    
    function clearHighlights() {
      // Rimuovi evidenziazioni dall'editor visuale
      document.querySelectorAll('.highlight-visual').forEach(el => {
        el.classList.remove('highlight-visual');
      });
      
      // Rimuovi evidenziazioni dall'HTML
      const htmlEditor = document.getElementById('htmlEditor');
      htmlEditor.classList.remove('highlight-html');
    }
    
    function highlightInHTML(text) {
      const htmlEditor = document.getElementById('htmlEditor');
      const htmlContent = htmlEditor.value;
      
      if (htmlContent.includes(text)) {
        htmlEditor.classList.add('highlight-html');
        
        // Trova la posizione del testo nell'HTML
        const index = htmlContent.indexOf(text);
        if (index !== -1) {
          htmlEditor.setSelectionRange(index, index + text.length);
        }
      }
    }
    
    function highlightInVisual(htmlText) {
      // Evidenzia temporaneamente nell'editor visuale
      const editor = document.getElementById('editor');
      editor.classList.add('highlight-visual');
      
      setTimeout(() => {
        editor.classList.remove('highlight-visual');
      }, 2000);
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
    
    // Gestione tabelle migliorata
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
      controls.style.left = Math.min(e.pageX, window.innerWidth - 300) + 'px';
      controls.style.top = Math.min(e.pageY, window.innerHeight - 400) + 'px';
      
      if (selectedTable) {
        // Carica valori correnti
        const computedStyle = window.getComputedStyle(selectedTable);
        const currentWidth = selectedTable.style.width || selectedTable.getAttribute('width') || '';
        const currentHeight = selectedTable.style.height || '';
        
        // Imposta larghezza
        if (currentWidth.includes('%')) {
          document.getElementById('tableWidthType').value = '%';
          document.getElementById('tableWidthValue').value = parseInt(currentWidth);
        } else if (currentWidth.includes('px')) {
          document.getElementById('tableWidthType').value = 'px';
          document.getElementById('tableWidthValue').value = parseInt(currentWidth);
        } else {
          document.getElementById('tableWidthType').value = 'auto';
          document.getElementById('tableWidthValue').value = '';
        }
        
        // Imposta altezza
        if (currentHeight.includes('px')) {
          document.getElementById('tableHeightType').value = 'px';
          document.getElementById('tableHeightValue').value = parseInt(currentHeight);
        } else {
          document.getElementById('tableHeightType').value = 'auto';
          document.getElementById('tableHeightValue').value = '';
        }
        
        document.getElementById('tableBorder').value = selectedTable.getAttribute('border') || 1;
        document.getElementById('tableCellSpacing').value = selectedTable.getAttribute('cellspacing') || 0;
        document.getElementById('tableCellPadding').value = selectedTable.getAttribute('cellpadding') || 8;
      }
      
      toggleWidthInput();
    }
    
    function toggleWidthInput() {
      const widthType = document.getElementById('tableWidthType').value;
      const widthInput = document.getElementById('tableWidthValue');
      
      if (widthType === 'auto') {
        widthInput.style.display = 'none';
        widthInput.value = '';
      } else {
        widthInput.style.display = 'block';
        widthInput.placeholder = `Valore in ${widthType}`;
      }
    }
    
    function applyTableSettings() {
      if (!selectedTable) return;
      
      // Applica larghezza
      const widthType = document.getElementById('tableWidthType').value;
      const widthValue = document.getElementById('tableWidthValue').value;
      
      if (widthType === 'auto') {
        selectedTable.style.width = 'auto';
        selectedTable.removeAttribute('width');
      } else if (widthValue) {
        const width = widthValue + widthType;
        selectedTable.style.width = width;
        selectedTable.setAttribute('width', width);
      }
      
      // Applica altezza
      const heightType = document.getElementById('tableHeightType').value;
      const heightValue = document.getElementById('tableHeightValue').value;
      
      if (heightType === 'auto') {
        selectedTable.style.height = 'auto';
      } else if (heightValue) {
        selectedTable.style.height = heightValue + 'px';
      }
      
      // Applica altri attributi
      selectedTable.setAttribute('border', document.getElementById('tableBorder').value);
      selectedTable.setAttribute('cellspacing', document.getElementById('tableCellSpacing').value);
      selectedTable.setAttribute('cellpadding', document.getElementById('tableCellPadding').value);
      
      // Applica stili alle celle
      const cells = selectedTable.querySelectorAll('td, th');
      const padding = document.getElementById('tableCellPadding').value + 'px';
      cells.forEach(cell => {
        cell.style.padding = padding;
      });
      
      updateHTML();
      closeTableControls();
    }
    
    function addTableRow() {
      if (!selectedTable) return;
      
      const rows = selectedTable.querySelectorAll('tr');
      const lastRow = rows[rows.length - 1];
      const cellCount = lastRow.children.length;
      
      const newRow = document.createElement('tr');
      for (let i = 0; i < cellCount; i++) {
        const cell = document.createElement('td');
        cell.style.border = '1px solid #ccc';
        cell.style.padding = document.getElementById('tableCellPadding').value + 'px';
        cell.textContent = 'Nuova cella';
        newRow.appendChild(cell);
      }
      
      selectedTable.appendChild(newRow);
      updateHTML();
    }
    
    function addTableColumn() {
      if (!selectedTable) return;
      
      const rows = selectedTable.querySelectorAll('tr');
      rows.forEach(row => {
        const cell = document.createElement('td');
        cell.style.border = '1px solid #ccc';
        cell.style.padding = document.getElementById('tableCellPadding').value + 'px';
        cell.textContent = 'Nuova cella';
        row.appendChild(cell);
      });
      
      updateHTML();
    }
    
    function deleteTable() {
      if (!selectedTable) return;
      
      if (confirm('Sei sicuro di voler eliminare questa tabella?')) {
        selectedTable.remove();
        selectedTable = null;
        closeTableControls();
        updateHTML();
      }
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
      const isClickInsideControls = controls.contains(e.target);
      const isClickOnTable = e.target.closest('table');
      
      if (!isClickInsideControls && !isClickOnTable && controls.style.display === 'block') {
        closeTableControls();
      }
    });
    
    // Inizializza l'editor
    setTimeout(() => {
      updateHTML();
    }, 100);
  </script>
</body>
</html>
"""

# Inietta il componente HTML in Streamlit
components.html(html_content, height=800, scrolling=True)
