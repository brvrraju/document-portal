document.addEventListener('DOMContentLoaded', () => {
    
    // API Base URL (Assumes frontend is served by FastAPI or runs on same host, update if needed)
    const API_BASE = "http://127.0.0.1:8000";

    // --- Tab Switching Logic ---
    const tabs = document.querySelectorAll('.tab-btn');
    const panels = document.querySelectorAll('.tab-panel');

    tabs.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active classes
            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding panel
            btn.classList.add('active');
            const targetId = `tab-${btn.dataset.tab}`;
            document.getElementById(targetId).classList.add('active');
        });
    });

    // --- File Input UI Updates ---
    function setupFileInput(inputId, statusId) {
        const input = document.getElementById(inputId);
        const status = document.getElementById(statusId);
        
        input.addEventListener('change', (e) => {
            const files = e.target.files;
            if (files.length === 0) {
                status.textContent = 'No file chosen';
                status.style.color = 'var(--text-secondary)';
            } else if (files.length === 1) {
                status.textContent = files[0].name;
                status.style.color = '#F3F4F6';
            } else {
                status.textContent = `${files.length} files selected`;
                status.style.color = '#F3F4F6';
            }
        });
    }

    setupFileInput('an-file', 'an-status');
    setupFileInput('cmp-ref', 'cmp-ref-status');
    setupFileInput('cmp-act', 'cmp-act-status');
    setupFileInput('chat-files', 'chat-files-status');


    // ==========================================
    // 1. ANALYZE TAB
    // ==========================================
    document.getElementById('btn-analyze').addEventListener('click', async () => {
        const file = document.getElementById('an-file').files[0];
        const out = document.getElementById('an-json');
        const btn = document.getElementById('btn-analyze');
        
        if (!file) {
            out.textContent = "Please upload a document to analyze.";
            return;
        }

        try {
            out.textContent = "Running analysis... ⏳";
            btn.disabled = true;

            const fd = new FormData();
            fd.append("file", file);

            const res = await fetch(`${API_BASE}/analyze`, { method: "POST", body: fd });
            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: res.statusText }));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            const json = await res.json();
            out.textContent = JSON.stringify(json, null, 2);
        } catch (e) {
            out.textContent = "Error: " + (e.message || e);
            out.style.color = "#EF4444"; // Red for error
        } finally {
            btn.disabled = false;
        }
    });


    // ==========================================
    // 2. COMPARE TAB
    // ==========================================
    document.getElementById('btn-compare').addEventListener('click', async () => {
        const ref = document.getElementById('cmp-ref').files[0];
        const act = document.getElementById('cmp-act').files[0];
        const tbody = document.querySelector('#cmp-table tbody');
        const btn = document.getElementById('btn-compare');

        if (!ref || !act) {
            tbody.innerHTML = `<tr><td colspan="2" class="muted center">Please upload both reference and actual files.</td></tr>`;
            return;
        }

        try {
            tbody.innerHTML = `<tr><td colspan="2" class="center">Comparing documents... ⏳</td></tr>`;
            btn.disabled = true;

            const fd = new FormData();
            fd.append("reference", ref);
            fd.append("actual", act);

            const res = await fetch(`${API_BASE}/compare`, { method: "POST", body: fd });
            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: res.statusText }));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            const json = await res.json();
            
            const rows = json.rows || [];
            if (!rows.length) {
                tbody.innerHTML = `<tr><td colspan="2" class="muted center">No differences found. Documents are identical.</td></tr>`;
                return;
            }
            
            tbody.innerHTML = rows.map(r => {
                const page = r.Page ?? r.page ?? "";
                const chg = r.Changes ?? r.changes ?? "";
                return `<tr><td>${page}</td><td>${chg}</td></tr>`;
            }).join("");

        } catch (e) {
            tbody.innerHTML = `<tr><td colspan="2" style="color: #EF4444;" class="center">Error: ${e.message || e}</td></tr>`;
        } finally {
            btn.disabled = false;
        }
    });


    // ==========================================
    // 3. CHAT TAB
    // ==========================================
    let currentSession = null;

    document.getElementById('btn-build').addEventListener('click', async () => {
        const files = document.getElementById('chat-files').files;
        const sessionId = document.getElementById('chat-session').value.trim();
        const useSess = document.getElementById('chat-sessionized').checked;
        const k = document.getElementById('chat-k').value || 5;
        const chunk = document.getElementById('chat-chunk').value || 1000;
        const overlap = document.getElementById('chat-overlap').value || 200;
        const meta = document.getElementById('chat-meta');
        const btn = document.getElementById('btn-build');

        if (!files.length) {
            meta.textContent = "Please upload at least one file to build the index.";
            meta.style.color = "#EF4444";
            return;
        }

        try {
            meta.textContent = "Building FAISS index... ⏳";
            meta.style.color = "var(--text-secondary)";
            const originalText = btn.textContent;
            btn.disabled = true;
            btn.textContent = 'Building Index...';

            const fd = new FormData();
            [...files].forEach(f => fd.append("files", f));
            if (sessionId) fd.append("session_id", sessionId);
            fd.append("use_session_dirs", useSess ? "true" : "false");
            fd.append("chunk_size", String(chunk));
            fd.append("chunk_overlap", String(overlap));
            fd.append("k", String(k));

            const res = await fetch(`${API_BASE}/chat/index`, { method: "POST", body: fd });
            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: res.statusText }));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            const json = await res.json();
            
            currentSession = json.session_id || sessionId || null;
            meta.textContent = `✅ Index Built Successfully! Session: ${currentSession || "(none)"}, Top-K: ${json.k}`;
            meta.style.color = "var(--logo-green)";
            
            btn.textContent = 'Index Built ✓';
            setTimeout(() => { btn.textContent = originalText; }, 2000);

        } catch (e) {
            meta.textContent = "Indexing failed: " + (e.message || e);
            meta.style.color = "#EF4444";
        } finally {
            btn.disabled = false;
        }
    });

    document.getElementById('btn-ask').addEventListener('click', async () => {
        const qInput = document.getElementById('chat-q');
        const q = qInput.value.trim();
        const ans = document.getElementById('chat-answer');
        const useSess = document.getElementById('chat-sessionized').checked;
        const k = document.getElementById('chat-k').value || 5;
        const btn = document.getElementById('btn-ask');

        if (!q) {
            ans.innerHTML = `<span style="color: #EF4444;">Please enter a question.</span>`;
            return;
        }
        
        if (useSess && !currentSession) {
            ans.innerHTML = `<span style="color: #EF4444;">You must build the index first (Session-based mode is ON).</span>`;
            return;
        }

        try {
            ans.innerHTML = `<span style="color: var(--accent-blue);">Thinking and retrieving context... ⏳</span>`;
            btn.disabled = true;

            const fd = new FormData();
            fd.append("question", q);
            fd.append("use_session_dirs", useSess ? "true" : "false");
            fd.append("k", String(k));
            if (useSess && currentSession) fd.append("session_id", currentSession);

            const res = await fetch(`${API_BASE}/chat/query`, { method: "POST", body: fd });
            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: res.statusText }));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            
            const json = await res.json();
            ans.innerHTML = json.answer || "No answer.";
            ans.style.color = "var(--text-primary)";
            
            qInput.value = ''; // Clear input on success
            
        } catch (e) {
            ans.innerHTML = `<span style="color: #EF4444;">Query failed: ${e.message || e}</span>`;
        } finally {
            btn.disabled = false;
        }
    });

    // Allow hitting Enter to send question
    document.getElementById('chat-q').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            document.getElementById('btn-ask').click();
        }
    });
});
