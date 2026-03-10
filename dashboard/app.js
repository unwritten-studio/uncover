'use strict';

// ── Config ──────────────────────────────────────────────────────────────────
const OWNER         = 'unwritten-studio';
const REPO          = 'uncover';
const CHAPTERS_PATH = 'chapters';
const READING_WPM   = 200;

// ── State ───────────────────────────────────────────────────────────────────
const state = {
  token:        localStorage.getItem('uncover_token') || '',
  chapters:     [],   // { name, path, sha, title, words, content }
  currentIndex: null,
  editor:       null,
  isDirty:      false,
  viewMode:     'editor',
  _previewTimer: null,
  _statsTimer:   null,
};

// ── GitHub API ───────────────────────────────────────────────────────────────
async function apiRequest(path, options = {}) {
  const headers = { 'Accept': 'application/vnd.github.v3+json' };
  if (state.token) headers['Authorization'] = `token ${state.token}`;
  if (options.body) headers['Content-Type'] = 'application/json';

  const res = await fetch(`https://api.github.com${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || `HTTP ${res.status}`);
  }
  return res.json();
}

async function fetchChapterList() {
  return apiRequest(`/repos/${OWNER}/${REPO}/contents/${CHAPTERS_PATH}`);
}

async function fetchChapterContent(filePath) {
  const data = await apiRequest(`/repos/${OWNER}/${REPO}/contents/${filePath}`);
  return { content: fromBase64(data.content), sha: data.sha };
}

async function saveChapter(filePath, content, sha, message) {
  return apiRequest(`/repos/${OWNER}/${REPO}/contents/${filePath}`, {
    method: 'PUT',
    body: JSON.stringify({ message, content: toBase64(content), sha }),
  });
}

// ── Encoding (UTF-8 safe) ────────────────────────────────────────────────────
function toBase64(str) {
  return btoa(unescape(encodeURIComponent(str)));
}
function fromBase64(str) {
  return decodeURIComponent(escape(atob(str.replace(/\n/g, ''))));
}

// ── Text utilities ───────────────────────────────────────────────────────────
function stripLatex(text) {
  return text
    .replace(/\\begin\{[^}]+\}[\s\S]*?\\end\{[^}]+\}/g, '')
    .replace(/\\[a-zA-Z]+\[[^\]]*\]\{[^}]*\}/g, '')
    .replace(/\\[a-zA-Z]+\{[^}]*\}/g, '')
    .replace(/\\[a-zA-Z]+/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function extractTitle(content) {
  const match = content.match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : null;
}

function wordCount(text) {
  return stripLatex(text).trim().split(/\s+/).filter(Boolean).length;
}

function readingTime(words) {
  const min = Math.ceil(words / READING_WPM);
  return `${min} Min.`;
}

function pageCount(words) {
  const WORDS_PER_PAGE = 165; // A5, 11pt, Linestretch 1.2 — kalibriert am tatsächlichen PDF (84 Seiten)
  const pages = Math.ceil(words / WORDS_PER_PAGE);
  return `~${pages} S.`;
}

// Derives a display name from filename: '01-begehbares-buch.md' → { num: '01', title: 'Begehbares Buch' }
function infoFromFilename(filename) {
  const base  = filename.replace('.md', '');
  const parts = base.split('-');
  const raw   = parts[0];
  const num   = parseInt(raw);

  // Special pages: only one label, no separate num
  if (num === 0)  return { num: '',   title: 'Titelseite' };
  if (num === 99) return { num: '',   title: 'Rückseite' };

  const title = parts.slice(1)
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');

  return { num: raw, title };
}

// ── Token management ─────────────────────────────────────────────────────────
function setToken(token) {
  state.token = token;
  token
    ? localStorage.setItem('uncover_token', token)
    : localStorage.removeItem('uncover_token');
  updateTokenUI();
}

function updateTokenUI() {
  const btn = document.getElementById('token-btn');
  btn.textContent = state.token ? '⚙ Token ✓' : '⚙ Token';
  btn.style.opacity = state.token ? '0.85' : '0.5';
}

// ── Sidebar ──────────────────────────────────────────────────────────────────
function renderChapterList() {
  const list = document.getElementById('chapter-list');
  list.innerHTML = '';

  state.chapters.forEach((chapter) => {
    const { num, title } = infoFromFilename(chapter.name);
    const isActive = state.currentIndex !== null &&
      state.chapters[state.currentIndex]?.name === chapter.name;

    const btn = document.createElement('button');
    btn.className = `chapter-item${isActive ? ' active' : ''}`;
    btn.innerHTML = `
      <div class="flex items-start gap-2">
        ${num ? `<span class="chapter-num pt-0.5">${num}</span>` : ''}
        <span class="chapter-name">${chapter.title || title}</span>
      </div>
      ${chapter.words ? `
        <div class="chapter-meta">
          ${chapter.words.toLocaleString('de')} Wörter · ${pageCount(chapter.words)} · ${readingTime(chapter.words)}
        </div>` : ''}
    `;
    btn.addEventListener('click', () => openChapter(chapter));
    list.appendChild(btn);
  });

  renderSidebarStats();
}

function renderSidebarStats() {
  const loaded      = state.chapters.filter(c => c.words != null);
  const totalWords  = loaded.reduce((sum, c) => sum + c.words, 0);
  const el          = document.getElementById('sidebar-stats');

  if (totalWords > 0) {
    el.innerHTML = `
      ${state.chapters.length} Kapitel<br>
      ${totalWords.toLocaleString('de')} Wörter · ${pageCount(totalWords)}<br>
      ca. ${readingTime(totalWords)} Lesezeit
    `;
  } else {
    el.textContent = `${state.chapters.length} Kapitel`;
  }
}

// ── Open chapter ─────────────────────────────────────────────────────────────
async function openChapter(chapter) {
  try {
    if (!chapter.content) {
      const { content, sha } = await fetchChapterContent(chapter.path);
      chapter.content = content;
      chapter.sha     = sha;
      chapter.title   = extractTitle(content) || infoFromFilename(chapter.name).title;
      chapter.words   = wordCount(content);
    }

    state.currentIndex = state.chapters.indexOf(chapter);
    state.isDirty      = false;

    // Show editor area
    document.getElementById('welcome-screen').classList.add('hidden');
    document.getElementById('editor-area').classList.remove('hidden');
    document.getElementById('editor-header').classList.remove('hidden');

    updateEditorContent(chapter.content);
    updatePreview(chapter.content);
    updateChapterHeader(chapter);
    updateSaveButton();
    renderChapterList();

  } catch (err) {
    alert(`Kapitel konnte nicht geladen werden:\n${err.message}`);
  }
}

// ── LaTeX line highlighting ───────────────────────────────────────────────────
// Adds a gray background to lines that are LaTeX (start with \ or are inside
// a \begin{...}...\end{...} block). Runs after content load and on change.
function applyLatexLineStyles() {
  const editor = state.editor;
  const lineCount = editor.lineCount();
  let insideBlock = false;

  for (let i = 0; i < lineCount; i++) {
    const text = editor.getLine(i).trim();
    const isLatex = text.startsWith('\\') || insideBlock;

    if (text.startsWith('\\begin{')) insideBlock = true;
    if (text.startsWith('\\end{'))   insideBlock = false;

    if (isLatex) {
      editor.addLineClass(i, 'background', 'cm-latex-line');
      editor.addLineClass(i, 'text',       'cm-latex-text');
    } else {
      editor.removeLineClass(i, 'background', 'cm-latex-line');
      editor.removeLineClass(i, 'text',       'cm-latex-text');
    }
  }
}

// ── Editor ───────────────────────────────────────────────────────────────────
function initEditor() {
  const textarea = document.getElementById('editor-textarea');

  state.editor = CodeMirror.fromTextArea(textarea, {
    mode:        'markdown',
    lineWrapping: true,
    lineNumbers:  false,
    autofocus:    false,
    theme:        'default',
    extraKeys: {
      'Ctrl-S': () => saveCurrentChapter(),
      'Cmd-S':  () => saveCurrentChapter(),
    },
  });

  state.editor.on('change', () => {
    if (state.currentIndex === null) return;

    if (!state.isDirty) {
      state.isDirty = true;
      updateSaveButton();
      // Mark chapter title with unsaved dot
      const titleEl = document.getElementById('chapter-title');
      titleEl.classList.add('dirty-dot');
    }

    // Debounced preview update (500ms)
    clearTimeout(state._previewTimer);
    state._previewTimer = setTimeout(() => {
      updatePreview(state.editor.getValue());
      applyLatexLineStyles();
    }, 500);

    // Debounced word count update (1.5s)
    clearTimeout(state._statsTimer);
    state._statsTimer = setTimeout(() => {
      const chapter = state.chapters[state.currentIndex];
      if (!chapter) return;
      chapter.words = wordCount(state.editor.getValue());
      updateChapterHeader(chapter);
      renderSidebarStats();
    }, 1500);
  });
}

function updateEditorContent(content) {
  state.editor.setValue(content);
  state.editor.clearHistory();
  state.editor.scrollTo(0, 0);
  setTimeout(() => { state.editor.refresh(); applyLatexLineStyles(); }, 50);
}

// ── Preview ──────────────────────────────────────────────────────────────────
function updatePreview(content) {
  const clean = stripLatex(content);
  document.getElementById('preview-content').innerHTML = marked.parse(clean);
}

// ── View modes ───────────────────────────────────────────────────────────────
function setViewMode(mode) {
  state.viewMode = mode;

  const editorPane  = document.getElementById('editor-pane');
  const previewPane = document.getElementById('preview-pane');
  const btnEditor   = document.getElementById('view-editor');
  const btnPreview  = document.getElementById('view-preview');
  const btnSplit    = document.getElementById('view-split');

  // Reset all buttons
  [btnEditor, btnPreview, btnSplit].forEach(b => b.classList.remove('active'));

  if (mode === 'editor') {
    editorPane.classList.remove('hidden');
    previewPane.classList.add('hidden');
    editorPane.style.flex = '1';
    btnEditor.classList.add('active');
  } else if (mode === 'preview') {
    editorPane.classList.add('hidden');
    previewPane.classList.remove('hidden');
    previewPane.style.flex = '1';
    btnPreview.classList.add('active');
  } else { // split
    editorPane.classList.remove('hidden');
    previewPane.classList.remove('hidden');
    editorPane.style.flex = '1';
    previewPane.style.flex = '1';
    btnSplit.classList.add('active');
  }

  setTimeout(() => state.editor?.refresh(), 50);
}

// ── Save ─────────────────────────────────────────────────────────────────────
async function saveCurrentChapter() {
  if (state.currentIndex === null || !state.isDirty) return;

  if (!state.token) {
    openTokenModal();
    return;
  }

  const chapter = state.chapters[state.currentIndex];
  const content = state.editor.getValue();
  const message = `Update: ${chapter.title || chapter.name}`;

  const btn = document.getElementById('save-btn');
  btn.textContent = 'Speichern…';
  btn.disabled = true;

  try {
    const result  = await saveChapter(chapter.path, content, chapter.sha, message);
    chapter.content = content;
    chapter.sha     = result.content.sha;
    chapter.words   = wordCount(content);
    state.isDirty   = false;

    document.getElementById('chapter-title').classList.remove('dirty-dot');
    btn.textContent = 'Gespeichert ✓';
    setTimeout(() => { btn.textContent = 'Speichern'; updateSaveButton(); }, 2500);

  } catch (err) {
    btn.textContent = 'Fehler';
    btn.disabled = false;
    alert(`Speichern fehlgeschlagen:\n${err.message}`);
    setTimeout(() => { btn.textContent = 'Speichern'; updateSaveButton(); }, 3000);
  }
}

function updateSaveButton() {
  const btn = document.getElementById('save-btn');
  const hasChapter = state.currentIndex !== null;
  btn.classList.toggle('hidden', !hasChapter);
  btn.disabled = !state.isDirty;
}

// ── Chapter header ────────────────────────────────────────────────────────────
function updateChapterHeader(chapter) {
  document.getElementById('chapter-title').textContent = chapter.title || chapter.name;
  const words = chapter.words || 0;
  document.getElementById('chapter-stats').textContent = words
    ? `${words.toLocaleString('de')} Wörter · ${pageCount(words)} · ${readingTime(words)}`
    : '';
}

// ── Token modal ───────────────────────────────────────────────────────────────
function openTokenModal() {
  document.getElementById('token-input').value = state.token;
  document.getElementById('token-modal').classList.remove('hidden');
  document.getElementById('token-input').focus();
}
function closeTokenModal() {
  document.getElementById('token-modal').classList.add('hidden');
}

// ── Background stats loader ───────────────────────────────────────────────────
async function fetchAllChapterStats() {
  const BATCH = 4;
  for (let i = 0; i < state.chapters.length; i += BATCH) {
    await Promise.all(
      state.chapters.slice(i, i + BATCH).map(async (chapter) => {
        if (chapter.content) return;
        try {
          const { content, sha } = await fetchChapterContent(chapter.path);
          chapter.content = content;
          chapter.sha     = sha;
          chapter.title   = extractTitle(content) || infoFromFilename(chapter.name).title;
          chapter.words   = wordCount(content);
          renderChapterList();
          updateBookStats();
        } catch (_) { /* silently skip */ }
      })
    );
  }
}

function updateBookStats() {
  const loaded     = state.chapters.filter(c => c.words != null);
  const totalWords = loaded.reduce((sum, c) => sum + c.words, 0);
  const el = document.getElementById('book-stats');
  el.textContent = totalWords > 0
    ? `${state.chapters.length} Kapitel · ${totalWords.toLocaleString('de')} Wörter · ${pageCount(totalWords)}`
    : `${state.chapters.length} Kapitel`;
}

// ── Init ──────────────────────────────────────────────────────────────────────
async function init() {
  updateTokenUI();
  initEditor();
  setViewMode('editor');

  // Event listeners
  document.getElementById('token-btn')   .addEventListener('click', openTokenModal);
  document.getElementById('token-cancel').addEventListener('click', closeTokenModal);
  document.getElementById('token-clear') .addEventListener('click', () => { setToken(''); closeTokenModal(); });
  document.getElementById('token-save')  .addEventListener('click', () => {
    setToken(document.getElementById('token-input').value.trim());
    closeTokenModal();
  });
  document.getElementById('token-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('token-save').click();
    if (e.key === 'Escape') closeTokenModal();
  });
  document.getElementById('token-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeTokenModal();
  });

  document.getElementById('save-btn')    .addEventListener('click', saveCurrentChapter);
  document.getElementById('view-editor') .addEventListener('click', () => setViewMode('editor'));
  document.getElementById('view-split')  .addEventListener('click', () => setViewMode('split'));
  document.getElementById('view-preview').addEventListener('click', () => setViewMode('preview'));

  // Load chapter list
  try {
    const files = await fetchChapterList();
    state.chapters = files
      .filter(f => f.name.endsWith('.md'))
      .sort((a, b) => a.name.localeCompare(b.name))
      .map(f => ({ name: f.name, path: f.path, sha: f.sha,
                   title: null, words: null, content: null }));

    renderChapterList();
    updateBookStats();

    // Fetch all chapters in background (word counts + real titles)
    fetchAllChapterStats();

  } catch (err) {
    document.getElementById('chapter-list').innerHTML =
      `<div class="p-4 text-sm text-red-500">Fehler beim Laden: ${err.message}</div>`;
  }
}

document.addEventListener('DOMContentLoaded', init);
