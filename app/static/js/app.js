// Signal Stack - Executive Intelligence Dashboard Frontend (Light Coral Theme)

let currentCompanyId = null;
let currentCompanyData = null;
let currentInterviewState = null;
let currentStackData = null;

// Initialization on DOM Load
document.addEventListener("DOMContentLoaded", async () => {
    setupTabNavigation();
    setupEventHandlers();
    await loadCompanyList();
});

// Tab Navigation
function setupTabNavigation() {
    const tabButtons = document.querySelectorAll(".tab-btn");
    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-tab");
            switchTab(targetId);
        });
    });
}

function switchTab(tabId) {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-pane").forEach(p => p.classList.add("hidden"));

    const activeBtn = document.querySelector(`[data-tab="${tabId}"]`);
    if (activeBtn) activeBtn.classList.add("active");

    const targetPane = document.getElementById(tabId);
    if (targetPane) targetPane.classList.remove("hidden");

    if (window.lucide) lucide.createIcons();
}

// Setup Event Handlers
function setupEventHandlers() {
    // Company switcher dropdown
    const select = document.getElementById("companySelect");
    select.addEventListener("change", (e) => {
        currentCompanyId = e.target.value;
        refreshActiveCompany();
    });

    // New Company Modal
    document.getElementById("btnNewCompanyModal").addEventListener("click", () => {
        document.getElementById("modalNewCompany").classList.remove("hidden");
    });

    document.getElementById("btnSubmitNewCompany").addEventListener("click", async () => {
        const name = document.getElementById("inputNewCompanyName").value.trim();
        const url = document.getElementById("inputNewCompanyUrl").value.trim();
        const notes = document.getElementById("inputNewCompanyNotes").value.trim();
        if (!name || !url) {
            alert("Please enter company name and website URL.");
            return;
        }

        const btn = document.getElementById("btnSubmitNewCompany");
        btn.textContent = "Researching...";
        btn.disabled = true;

        try {
            const resp = await fetch("/api/companies/setup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, website: url, context_notes: notes })
            });
            const data = await resp.json();
            document.getElementById("modalNewCompany").classList.add("hidden");
            btn.textContent = "Start Research";
            btn.disabled = false;
            await loadCompanyList();
            if (data.company && data.company.id) {
                document.getElementById("companySelect").value = data.company.id;
                currentCompanyId = data.company.id;
                refreshActiveCompany();
            }
        } catch (e) {
            alert("Error researching company: " + e.message);
            btn.textContent = "Start Research";
            btn.disabled = false;
        }
    });

    // Interview Answer Submission
    document.getElementById("btnSubmitAnswer").addEventListener("click", submitInterviewAnswer);
    document.getElementById("btnSkipQuestion").addEventListener("click", () => {
        submitInterviewAnswer(true);
    });

    // Crawl Sources Button
    document.getElementById("btnRunCrawler").addEventListener("click", async () => {
        if (!currentCompanyId) return;
        const btn = document.getElementById("btnRunCrawler");
        const originalText = btn.innerHTML;
        btn.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Crawling...</span>`;
        if (window.lucide) lucide.createIcons();

        try {
            const resp = await fetch(`/api/crawler/${currentCompanyId}/run`, { method: "POST" });
            const data = await resp.json();
            alert(`Crawl completed! ${data.new_signals_collected || 0} new intelligence records collected.`);
            loadIntelligenceFeed();
            loadStackData();
        } catch (e) {
            alert("Error crawling sources: " + e.message);
        } finally {
            btn.innerHTML = originalText;
            if (window.lucide) lucide.createIcons();
        }
    });

    // Generate Monday Brief Button
    const genBriefHandler = async () => {
        if (!currentCompanyId) return;
        const btn = document.getElementById("btnGenerateBrief");
        const originalText = btn.innerHTML;
        btn.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Synthesizing...</span>`;
        if (window.lucide) lucide.createIcons();

        try {
            const resp = await fetch(`/api/briefs/${currentCompanyId}/generate`, { method: "POST" });
            const data = await resp.json();
            alert("Monday Morning Executive Brief generated!");
            switchTab("tab-brief");
            loadMondayBrief();
        } catch (e) {
            alert("Error generating brief: " + e.message);
        } finally {
            btn.innerHTML = originalText;
            if (window.lucide) lucide.createIcons();
        }
    };

    document.getElementById("btnGenerateBrief").addEventListener("click", genBriefHandler);
    document.getElementById("btnRegenerateBrief").addEventListener("click", genBriefHandler);

    // Rebuild Stack Button
    document.getElementById("btnRebuildStack").addEventListener("click", async () => {
        if (!currentCompanyId) return;
        try {
            await fetch(`/api/stack/${currentCompanyId}/build`, { method: "POST" });
            alert("Signal Stack rebuilt and justified.");
            loadStackData();
        } catch (e) {
            alert("Error building stack: " + e.message);
        }
    });

    // Add Custom Source Modal & Submit
    document.getElementById("btnAddSourceModal").addEventListener("click", () => {
        document.getElementById("modalAddSource").classList.remove("hidden");
    });

    document.getElementById("btnSubmitAddSource").addEventListener("click", async () => {
        if (!currentCompanyId) return;
        const cat = document.getElementById("inputSourceCategory").value;
        const name = document.getElementById("inputSourceName").value.trim();
        const url = document.getElementById("inputSourceUrl").value.trim();
        const reason = document.getElementById("inputSourceReason").value.trim();

        if (!name || !url || !reason) {
            alert("Please provide source name, URL, and a clear reason for inclusion.");
            return;
        }

        try {
            await fetch(`/api/stack/${currentCompanyId}/source`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ category: cat, name, url, source_type: "rss", reason_for_inclusion: reason })
            });
            document.getElementById("modalAddSource").classList.add("hidden");
            alert("Source added to Signal Stack.");
            loadStackData();
        } catch (e) {
            alert("Error adding source: " + e.message);
        }
    });

    // Internal File Ingestion (CSV, Excel, PDF, TXT)
    const fileInput = document.getElementById("internalFileInput");
    fileInput.addEventListener("change", async (e) => {
        const file = e.target.files[0];
        if (!file || !currentCompanyId) return;

        const statusDiv = document.getElementById("uploadStatusMessage");
        statusDiv.classList.remove("hidden");
        statusDiv.textContent = `Uploading and parsing ${file.name}...`;

        const formData = new FormData();
        formData.append("file", file);

        try {
            const resp = await fetch(`/api/stack/${currentCompanyId}/upload-internal`, {
                method: "POST",
                body: formData
            });
            const data = await resp.json();
            statusDiv.textContent = `Successfully parsed ${file.name}. Created ${data.signals_created} intelligence signals!`;
            setTimeout(() => statusDiv.classList.add("hidden"), 5000);
            loadIntelligenceFeed();
            loadStackData();
        } catch (err) {
            statusDiv.textContent = `Upload error: ${err.message}`;
        }
    });

    // Context Pivot Stress Test
    const pivotBtn = document.getElementById("btnTriggerPivotModal");
    if (pivotBtn) {
        pivotBtn.addEventListener("click", () => {
            document.getElementById("modalContextPivot").classList.remove("hidden");
        });
    }
    const pivotStressBtn = document.getElementById("btnStressTestPivot");
    if (pivotStressBtn) {
        pivotStressBtn.addEventListener("click", () => {
            document.getElementById("modalContextPivot").classList.remove("hidden");
        });
    }

    document.getElementById("btnExecutePivot").addEventListener("click", async () => {
        if (!currentCompanyId) return;
        const newContext = document.getElementById("inputPivotContext").value.trim();
        const execBtn = document.getElementById("btnExecutePivot");
        execBtn.textContent = "Analyzing Pivot...";
        execBtn.disabled = true;

        try {
            const resp = await fetch(`/api/stack/${currentCompanyId}/context-change`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ new_context: newContext })
            });
            const data = await resp.json();

            const preview = document.getElementById("pivotResultsPreview");
            preview.classList.remove("hidden");
            preview.innerHTML = `
                <div class="font-bold text-emerald-600">Context Pivot Completed:</div>
                <div class="text-gray-700">${data.context_change_summary || ''}</div>
                <div class="mt-2 text-rose-600 font-semibold">Sources Deprecated: ${data.sources_to_deprecate ? data.sources_to_deprecate.length : 0}</div>
                <div class="text-blue-600 font-semibold">New Sources Recommended: ${data.recommended_new_sources ? data.recommended_new_sources.length : 0}</div>
                <div class="text-gray-500 mt-1 italic">${data.strategic_impact_explanation || ''}</div>
            `;
            loadStackData();
            refreshActiveCompany();
        } catch (e) {
            alert("Pivot error: " + e.message);
        } finally {
            execBtn.textContent = "Re-Assess Signal Stack";
            execBtn.disabled = false;
        }
    });

    // Copy Markdown Brief
    document.getElementById("btnCopyBriefMarkdown").addEventListener("click", () => {
        const md = window._currentBriefMarkdown || "";
        if (!md) {
            alert("No brief generated yet.");
            return;
        }
        navigator.clipboard.writeText(md);
        alert("Monday Morning Brief copied to clipboard as Markdown!");
    });

    // Automation manual triggers
    document.getElementById("btnTriggerWeeklyNow").addEventListener("click", async () => {
        try {
            await fetch("/api/scheduler/trigger-brief", { method: "POST" });
            alert("Weekly brief automation triggered!");
            loadAutomationStatus();
        } catch (e) {
            alert("Error: " + e.message);
        }
    });

    document.getElementById("btnTriggerAuditNow").addEventListener("click", async () => {
        try {
            await fetch("/api/scheduler/trigger-audit", { method: "POST" });
            alert("Monthly audit executed!");
            loadAutomationStatus();
        } catch (e) {
            alert("Error: " + e.message);
        }
    });

    // Feed Filters
    document.getElementById("feedCategoryFilter").addEventListener("change", loadIntelligenceFeed);
    document.getElementById("feedImpactFilter").addEventListener("change", loadIntelligenceFeed);
    document.getElementById("feedUrgencyFilter").addEventListener("change", loadIntelligenceFeed);
}

// Load List of Companies
async function loadCompanyList() {
    try {
        const resp = await fetch("/api/companies");
        const list = await resp.json();
        const select = document.getElementById("companySelect");
        select.innerHTML = "";

        if (list.length === 0) {
            select.innerHTML = "<option>No companies configured</option>";
            return;
        }

        list.forEach(c => {
            const opt = document.createElement("option");
            opt.value = c.id;
            opt.textContent = `${c.name} (${c.industry || 'Business'})`;
            select.appendChild(opt);
        });

        if (!currentCompanyId && list.length > 0) {
            currentCompanyId = list[0].id;
        }
        if (currentCompanyId) {
            select.value = currentCompanyId;
            await refreshActiveCompany();
        }
    } catch (e) {
        console.error("Failed to load company list:", e);
    }
}

// Refresh all components for active company
async function refreshActiveCompany() {
    if (!currentCompanyId) return;

    await Promise.all([
        loadCompanyProfile(),
        loadInterviewState(),
        loadStackData(),
        loadIntelligenceFeed(),
        loadMondayBrief(),
        loadAutomationStatus()
    ]);
}

// 1. Load Company Profile
async function loadCompanyProfile() {
    try {
        const resp = await fetch(`/api/companies/${currentCompanyId}`);
        const c = await resp.json();
        currentCompanyData = c;

        document.getElementById("overviewCompanyName").textContent = c.name;
        document.getElementById("overviewIndustryBadge").textContent = c.industry || "General";
        document.getElementById("overviewDescription").textContent = c.description || "No description provided.";
        document.getElementById("activeCompanyLabel").textContent = c.name;
        document.getElementById("activeCompanyUrl").textContent = c.website;

        // Verified Facts
        const factsList = document.getElementById("factsList");
        factsList.innerHTML = "";
        const facts = c.verified_facts || [];
        if (facts.length === 0) {
            factsList.innerHTML = `<li class="p-2.5 rounded-lg bg-gray-50 text-gray-400">No verified facts recorded yet.</li>`;
        } else {
            facts.forEach(f => {
                const li = document.createElement("li");
                li.className = "p-2.5 rounded-lg bg-emerald-50/50 border border-emerald-100 text-gray-700 flex items-start space-x-2";
                li.innerHTML = `<span class="text-emerald-500 font-bold mt-0.5">•</span><span>${f}</span>`;
                factsList.appendChild(li);
            });
        }

        // Assumptions
        const assumptionsList = document.getElementById("assumptionsList");
        assumptionsList.innerHTML = "";
        const assumptions = c.assumptions || [];
        if (assumptions.length === 0) {
            assumptionsList.innerHTML = `<li class="p-2.5 rounded-lg bg-gray-50 text-gray-400">No strategic assumptions recorded yet.</li>`;
        } else {
            assumptions.forEach(a => {
                const li = document.createElement("li");
                li.className = "p-2.5 rounded-lg bg-amber-50/50 border border-amber-100 text-gray-700 flex items-start space-x-2";
                li.innerHTML = `<span class="text-amber-500 font-bold mt-0.5">•</span><span>${a}</span>`;
                assumptionsList.appendChild(li);
            });
        }

        // Target Customers, Revenue Streams, Growth Priorities
        renderPillarList("targetCustomersList", c.target_customers);
        renderPillarList("revenueStreamsList", c.revenue_streams);
        renderPillarList("growthPrioritiesList", c.growth_priorities);

    } catch (e) {
        console.error("Failed to load profile:", e);
    }
}

function renderPillarList(elementId, items) {
    const el = document.getElementById(elementId);
    el.innerHTML = "";
    if (!items || items.length === 0) {
        el.innerHTML = `<li class="text-gray-400 italic">None recorded</li>`;
        return;
    }
    items.forEach(it => {
        const li = document.createElement("li");
        li.className = "flex items-start space-x-2 text-gray-600";
        li.innerHTML = `<span class="text-coral-500 font-bold">›</span><span>${it}</span>`;
        el.appendChild(li);
    });
}

// 2. Load Interview State
async function loadInterviewState() {
    try {
        const resp = await fetch(`/api/interviews/${currentCompanyId}`);
        const state = await resp.json();
        currentInterviewState = state;

        const answered = state.answered_count || 0;
        const total = state.total_questions || 10;
        document.getElementById("interviewProgressText").textContent = answered;
        document.getElementById("interviewBadge").textContent = `${answered}/${total}`;

        const pct = Math.round((answered / total) * 100);
        document.getElementById("interviewProgressBar").style.width = `${pct}%`;

        // Render Active Question
        const activeContainer = document.getElementById("activeQuestionContainer");
        const currQ = state.current_question;

        if (currQ) {
            activeContainer.classList.remove("hidden");
            document.getElementById("currentQuestionBadge").textContent = `Question ${currQ.question_index} of ${total}`;
            document.getElementById("currentCategoryBadge").textContent = currQ.context_category || "Executive Context";
            document.getElementById("currentQuestionText").textContent = currQ.question_text;
            document.getElementById("currentQuestionHint").textContent = `Follow-Up Focus: ${currQ.follow_up_notes || 'Provide concrete operational or metric context.'}`;
            document.getElementById("interviewAnswerInput").value = "";
        } else {
            activeContainer.innerHTML = `
                <div class="text-center py-6 space-y-2">
                    <div class="w-10 h-10 rounded-full bg-emerald-50 text-emerald-500 flex items-center justify-center mx-auto">
                        <i data-lucide="check" class="w-5 h-5"></i>
                    </div>
                    <h3 class="text-base font-bold text-gray-800">Interview Completed</h3>
                    <p class="text-xs text-gray-400">All 10 questions answered. The Signal Stack is fully tailored to your business.</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
        }

        // Render Transcript & Past Answers
        const listContainer = document.getElementById("interviewQuestionsList");
        listContainer.innerHTML = "";
        (state.questions || []).forEach(q => {
            const card = document.createElement("div");
            card.className = "p-4 rounded-xl bg-white border border-gray-100 shadow-sm space-y-2";
            const isAnswered = Boolean(q.answer_text);
            const isSkipped = Boolean(q.is_skipped);

            card.innerHTML = `
                <div class="flex items-center justify-between">
                    <span class="text-xs font-bold text-coral-600">Q${q.question_index}. ${q.context_category}</span>
                    <span class="text-[10px] px-2 py-0.5 rounded-full ${isAnswered ? 'bg-emerald-50 text-emerald-600' : (isSkipped ? 'bg-gray-100 text-gray-500' : 'bg-amber-50 text-amber-600')}">
                        ${isAnswered ? 'Answered' : (isSkipped ? 'Skipped' : 'Pending')}
                    </span>
                </div>
                <div class="text-xs font-medium text-gray-800">${q.question_text}</div>
                <div class="text-xs text-gray-600 bg-gray-50 p-2.5 rounded-lg border border-gray-100">
                    <strong>Recorded:</strong> ${q.answer_text ? q.answer_text : (isSkipped ? '<em>Question skipped by founder.</em>' : '<em class="text-gray-400">Awaiting answer...</em>')}
                </div>
                <div class="flex justify-end">
                    <button class="btn-edit-answer text-[11px] text-coral-500 hover:text-coral-600 font-semibold" data-idx="${q.question_index}">
                        Edit Answer
                    </button>
                </div>
            `;
            listContainer.appendChild(card);
        });

        // Attach edit answer listeners
        document.querySelectorAll(".btn-edit-answer").forEach(btn => {
            btn.addEventListener("click", () => {
                const idx = parseInt(btn.getAttribute("data-idx"));
                const qObj = state.questions.find(x => x.question_index === idx);
                const newAns = prompt(`Edit Answer for Q${idx} (${qObj.question_text}):`, qObj.answer_text || "");
                if (newAns !== null) {
                    editInterviewAnswer(idx, newAns);
                }
            });
        });

    } catch (e) {
        console.error("Failed to load interview:", e);
    }
}

async function submitInterviewAnswer(isSkipped = false) {
    if (!currentCompanyId || !currentInterviewState || !currentInterviewState.current_question) return;

    const qIdx = currentInterviewState.current_question.question_index;
    const ans = document.getElementById("interviewAnswerInput").value.trim();

    if (!isSkipped && !ans) {
        alert("Please provide an answer or click 'Skip This Question'.");
        return;
    }

    try {
        await fetch(`/api/interviews/${currentCompanyId}/answer`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question_index: qIdx, answer_text: ans, is_skipped: isSkipped })
        });
        await loadInterviewState();
    } catch (e) {
        alert("Error submitting answer: " + e.message);
    }
}

async function editInterviewAnswer(questionIndex, newText) {
    try {
        await fetch(`/api/interviews/${currentCompanyId}/answer`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question_index: questionIndex, answer_text: newText, is_skipped: false })
        });
        await loadInterviewState();
    } catch (e) {
        alert("Error updating answer: " + e.message);
    }
}

// 3. Load Signal Stack & Competitors
async function loadStackData() {
    try {
        const resp = await fetch(`/api/stack/${currentCompanyId}`);
        const data = await resp.json();
        currentStackData = data;

        document.getElementById("sourceCountBadge").textContent = data.total_sources || 0;
        document.getElementById("competitorCountBadge").textContent = `${(data.competitors || []).length} Competitors`;

        // Render Competitors Table
        const compTbody = document.getElementById("competitorsTableBody");
        compTbody.innerHTML = "";
        const comps = data.competitors || [];
        if (comps.length === 0) {
            compTbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-gray-400">No competitors configured.</td></tr>`;
        } else {
            comps.forEach(c => {
                const tr = document.createElement("tr");
                tr.className = "hover:bg-gray-50/50 transition";
                const threatColor = c.threat_level === 'High' ? 'text-rose-600 bg-rose-50' : (c.threat_level === 'Medium' ? 'text-amber-600 bg-amber-50' : 'text-gray-500 bg-gray-100');
                tr.innerHTML = `
                    <td class="p-3 font-bold text-gray-800">${c.name}</td>
                    <td class="p-3 text-gray-600">${c.relationship}</td>
                    <td class="p-3 text-gray-600 max-w-xs truncate">${c.core_offerings || 'Direct competitor'}</td>
                    <td class="p-3"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${threatColor}">${c.threat_level}</span></td>
                    <td class="p-3 text-gray-500 max-w-sm text-[11px] leading-tight">${c.reason_it_matters}</td>
                `;
                compTbody.appendChild(tr);
            });
        }

        // Render 4 Stack Categories
        const cats = data.categories || {};
        renderCategoryCards("sourcesCustomersList", cats.customers || [], "custSourceCount");
        renderCategoryCards("sourcesCompetitorsList", cats.competitors || [], "compSourceCount");
        renderCategoryCards("sourcesMarketList", cats.market || [], "mktSourceCount");
        renderCategoryCards("sourcesInternalList", cats.internal || [], "intSourceCount");

        // Render All Sources Table in Manager Tab
        renderManagerSourcesTable(data);

    } catch (e) {
        console.error("Failed to load stack:", e);
    }
}

function renderCategoryCards(containerId, sources, countId) {
    const container = document.getElementById(containerId);
    document.getElementById(countId).textContent = `${sources.length} sources`;
    container.innerHTML = "";

    if (sources.length === 0) {
        container.innerHTML = `<div class="p-3 text-center text-gray-400 text-xs">No sources in this category.</div>`;
        return;
    }

    sources.forEach(s => {
        const card = document.createElement("div");
        card.className = "p-3 rounded-xl bg-gray-50 border border-gray-100 hover:border-coral-200 transition space-y-1.5 text-xs";
        card.innerHTML = `
            <div class="flex items-center justify-between">
                <span class="font-bold text-gray-800 truncate max-w-[200px]">${s.name}</span>
                <span class="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">${s.source_type}</span>
            </div>
            <div class="text-[11px] text-gray-500 italic">
                <strong>Justification:</strong> ${s.reason_for_inclusion}
            </div>
            <div class="flex items-center justify-between text-[10px] text-gray-400 pt-1">
                <span>Tier: <strong class="text-coral-500">${s.credibility_tier}</strong></span>
                <span class="${s.health_score > 70 ? 'text-emerald-500' : 'text-amber-500'}">Health: ${s.health_score}%</span>
            </div>
        `;
        container.appendChild(card);
    });
}

function renderManagerSourcesTable(data) {
    const tbody = document.getElementById("allSourcesTableBody");
    tbody.innerHTML = "";
    const allSources = [];
    Object.values(data.categories || {}).forEach(arr => allSources.push(...arr));

    if (allSources.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-gray-400">No sources configured.</td></tr>`;
        return;
    }

    allSources.forEach(s => {
        const tr = document.createElement("tr");
        tr.className = "hover:bg-gray-50/50 transition";
        const isHealthy = s.last_status === 'healthy';
        tr.innerHTML = `
            <td class="p-3">
                <div class="font-bold text-gray-800">${s.name}</div>
                <div class="text-[10px] text-gray-400 font-mono truncate max-w-xs">${s.url}</div>
            </td>
            <td class="p-3 capitalize font-semibold text-gray-600">${s.category}</td>
            <td class="p-3 uppercase text-gray-400 text-[10px]">${s.source_type}</td>
            <td class="p-3">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${isHealthy ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'}">
                    ${s.last_status} (${s.health_score}%)
                </span>
            </td>
            <td class="p-3 text-[11px] text-gray-500 max-w-xs truncate">${s.reason_for_inclusion}</td>
            <td class="p-3 text-right">
                <button class="btn-delete-source text-rose-500 hover:text-rose-600 font-semibold text-[11px]" data-id="${s.id}">
                    Remove
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    document.querySelectorAll(".btn-delete-source").forEach(btn => {
        btn.addEventListener("click", async () => {
            const sid = btn.getAttribute("data-id");
            if (confirm("Remove this source from Signal Stack?")) {
                await fetch(`/api/stack/source/${sid}`, { method: "DELETE" });
                loadStackData();
            }
        });
    });
}

// 4. Load Intelligence Feed (Ranked Leaderboard Cards)
async function loadIntelligenceFeed() {
    try {
        const cat = document.getElementById("feedCategoryFilter").value;
        const imp = document.getElementById("feedImpactFilter").value;
        const urg = document.getElementById("feedUrgencyFilter").value;

        const resp = await fetch(`/api/intelligence/${currentCompanyId}/feed?category=${cat}&impact_type=${imp}&urgency=${urg}`);
        const items = await resp.json();

        const container = document.getElementById("intelligenceFeedContainer");
        container.innerHTML = "";

        if (items.length === 0) {
            container.innerHTML = `<div class="p-12 text-center text-gray-400 text-sm">No intelligence signals match the current filters.</div>`;
            return;
        }

        items.forEach((item, index) => {
            const card = document.createElement("div");
            card.className = "glass-panel rounded-2xl p-5 space-y-3 hover:shadow-md transition flex";

            const impactColor = item.impact_type === 'opportunity' ? 'badge-opportunity' : (item.impact_type === 'threat' ? 'badge-threat' : 'badge-neutral');
            const urgencyColor = item.urgency === 'high' ? 'text-rose-600' : (item.urgency === 'medium' ? 'text-amber-600' : 'text-gray-500');
            const rankClass = index < 3 ? `rank-${index + 1}` : '';

            card.innerHTML = `
                <div class="rank-number ${rankClass} flex-shrink-0 self-start mt-1">#${index + 1}</div>
                <div class="flex-1 ml-4 space-y-3">
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-gray-100 pb-3">
                        <div class="flex items-center space-x-2">
                            <span class="text-xs font-bold text-gray-800">${item.title || item.what_happened}</span>
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${impactColor}">${item.impact_type}</span>
                        </div>
                        <div class="flex items-center space-x-3 text-xs text-gray-400">
                            <span>Rank: <strong class="text-coral-500">${item.composite_rank}/100</strong></span>
                            <span>Urgency: <strong class="${urgencyColor} uppercase">${item.urgency}</strong></span>
                            <span class="text-gray-400">${item.publication_date || 'Recent'}</span>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                        <div class="space-y-1.5">
                            <div><strong class="text-gray-400">What Happened:</strong> <span class="text-gray-700">${item.what_happened}</span></div>
                            <div><strong class="text-gray-400">Why It Matters:</strong> <span class="text-gray-700">${item.why_it_matters}</span></div>
                            <div><strong class="text-gray-400">Business Area:</strong> <span class="text-coral-600">${item.business_area_affected}</span></div>
                        </div>
                        <div class="space-y-1.5">
                            <div><strong class="text-gray-400">Interpretation:</strong> <span class="text-gray-600 italic">${item.strategic_interpretation}</span></div>
                            <div><strong class="text-gray-400">Recommendation:</strong> <span class="text-emerald-600">${item.recommended_consideration}</span></div>
                            <div class="text-[11px] text-gray-400"><strong>Verification:</strong> <span class="text-emerald-600">${item.is_verified ? 'Verified' : 'Unconfirmed'}</span> via <em>${item.source_name || 'Public feed'}</em></div>
                        </div>
                    </div>

                    <div class="p-2.5 rounded-xl bg-gray-50 border border-gray-100 text-xs text-gray-600 flex items-center justify-between">
                        <div class="truncate max-w-2xl">
                            <strong>Evidence:</strong> "${item.evidence_snippet || item.what_happened}"
                        </div>
                        ${item.url && item.url !== '#' ? `<a href="${item.url}" target="_blank" class="text-coral-500 hover:text-coral-600 font-semibold flex items-center space-x-1 ml-3 shrink-0"><span>Source</span><i data-lucide="external-link" class="w-3 h-3"></i></a>` : ''}
                    </div>
                </div>
            `;
            container.appendChild(card);
        });

        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error("Failed to load feed:", e);
    }
}

// 5. Load Monday Morning Brief
async function loadMondayBrief() {
    try {
        const resp = await fetch(`/api/briefs/${currentCompanyId}/latest`);
        const res = await resp.json();
        const container = document.getElementById("briefContentContainer");

        if (!res.has_brief) {
            container.innerHTML = `
                <div class="text-center py-16 space-y-4">
                    <div class="w-12 h-12 rounded-2xl bg-coral-50 text-coral-500 flex items-center justify-center mx-auto">
                        <i data-lucide="file-text" class="w-6 h-6"></i>
                    </div>
                    <h3 class="text-base font-bold text-gray-800">No Brief Generated Yet</h3>
                    <p class="text-xs text-gray-400 max-w-md mx-auto">Click 'Generate Monday Brief' to synthesize intelligence into an executive report.</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        const b = res.brief;
        window._currentBriefMarkdown = b.markdown_content;
        document.getElementById("briefPeriodBadge").textContent = b.period_label || "Current Week";

        let html = "";

        // Section 1: Executive Summary
        html += `
            <div class="glass-panel rounded-2xl p-6 space-y-4 border-l-4 border-l-coral-400">
                <div class="flex items-center space-x-2">
                    <i data-lucide="award" class="w-5 h-5 text-coral-500"></i>
                    <h2 class="text-base font-bold uppercase tracking-wider text-gray-800">1. Executive Summary — Top 5</h2>
                </div>
                <div class="space-y-3">
        `;
        (b.executive_summary || []).slice(0, 5).forEach((item, idx) => {
            html += `
                <div class="p-3.5 rounded-xl bg-gray-50 border border-gray-100 space-y-1 text-xs">
                    <div class="flex items-center justify-between">
                        <span class="font-bold text-gray-800 text-sm">${idx + 1}. ${item.headline}</span>
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${item.priority === 'High' ? 'bg-rose-50 text-rose-600' : 'bg-gray-100 text-gray-600'}">${item.priority || 'Medium'}</span>
                    </div>
                    <div class="text-gray-600"><strong>Evidence:</strong> ${item.evidence}</div>
                    <div class="text-coral-600"><strong>Implication:</strong> ${item.implication}</div>
                </div>
            `;
        });
        html += `</div></div>`;

        // Section 2: Customer Signals
        html += `
            <div class="glass-panel rounded-2xl p-6 space-y-3">
                <h2 class="text-sm font-bold uppercase tracking-wider text-blue-600 flex items-center space-x-2">
                    <i data-lucide="messages-square" class="w-4 h-4"></i>
                    <span>2. Customer Signals</span>
                </h2>
                <div class="space-y-2 text-xs">
        `;
        (b.customer_signals || []).forEach(s => {
            html += `
                <div class="p-3 rounded-xl bg-gray-50 border border-gray-100 space-y-1">
                    <div class="font-bold text-gray-800">${s.problem}</div>
                    <div class="text-gray-500 italic">"${s.quote_or_evidence}"</div>
                    <div class="text-gray-400 text-[11px]">Sentiment: <strong class="text-amber-600">${s.sentiment}</strong> | ${s.implication}</div>
                </div>
            `;
        });
        html += `</div></div>`;

        // Section 3: Competitor Intelligence
        html += `
            <div class="glass-panel rounded-2xl p-6 space-y-3">
                <h2 class="text-sm font-bold uppercase tracking-wider text-rose-600 flex items-center space-x-2">
                    <i data-lucide="target" class="w-4 h-4"></i>
                    <span>3. Competitor Intelligence</span>
                </h2>
                <div class="space-y-2 text-xs">
        `;
        (b.competitor_signals || []).forEach(c => {
            html += `
                <div class="p-3 rounded-xl bg-gray-50 border border-gray-100 space-y-1">
                    <div class="flex items-center justify-between font-bold text-gray-800">
                        <span>${c.competitor}</span>
                        <span class="text-gray-500 font-normal">${c.what_changed}</span>
                    </div>
                    <div class="text-gray-600"><strong>Evidence:</strong> ${c.evidence}</div>
                    <div class="text-rose-600"><strong>Why It Matters:</strong> ${c.why_it_matters}</div>
                </div>
            `;
        });
        html += `</div></div>`;

        // Section 4: Market Intelligence
        html += `
            <div class="glass-panel rounded-2xl p-6 space-y-3">
                <h2 class="text-sm font-bold uppercase tracking-wider text-amber-600 flex items-center space-x-2">
                    <i data-lucide="scale" class="w-4 h-4"></i>
                    <span>4. Market & Regulatory Intelligence</span>
                </h2>
                <div class="space-y-2 text-xs">
        `;
        (b.market_signals || []).forEach(m => {
            html += `
                <div class="p-3 rounded-xl bg-gray-50 border border-gray-100 space-y-1">
                    <div class="font-bold text-gray-800">${m.development} <span class="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500 ml-2">${m.category}</span></div>
                    <div class="text-gray-600"><strong>Evidence:</strong> ${m.evidence}</div>
                    <div class="text-amber-600"><strong>Business Impact:</strong> ${m.business_impact}</div>
                </div>
            `;
        });
        html += `</div></div>`;

        // Section 5: Internal Business Intelligence
        html += `
            <div class="glass-panel rounded-2xl p-6 space-y-3">
                <h2 class="text-sm font-bold uppercase tracking-wider text-emerald-600 flex items-center space-x-2">
                    <i data-lucide="database" class="w-4 h-4"></i>
                    <span>5. Internal Intelligence</span>
                </h2>
                <div class="space-y-2 text-xs">
        `;
        (b.internal_signals || []).forEach(ins => {
            html += `
                <div class="p-3 rounded-xl bg-gray-50 border border-gray-100 space-y-1">
                    <div class="font-bold text-gray-800">${ins.pattern} <span class="text-gray-400 font-normal">(${ins.source_data})</span></div>
                    <div class="text-gray-600"><strong>Signal:</strong> ${ins.sales_objection_or_risk}</div>
                    <div class="text-emerald-600"><strong>Action:</strong> ${ins.action}</div>
                </div>
            `;
        });
        html += `</div></div>`;

        // Section 6: Opportunities
        html += `
            <div class="glass-panel rounded-2xl p-6 space-y-3 border-l-4 border-l-emerald-400">
                <h2 class="text-sm font-bold uppercase tracking-wider text-emerald-600 flex items-center space-x-2">
                    <i data-lucide="lightbulb" class="w-4 h-4"></i>
                    <span>6. Opportunities Identified</span>
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        `;
        (b.opportunities || []).forEach(opp => {
            html += `
                <div class="p-4 rounded-xl bg-emerald-50/50 border border-emerald-100 space-y-2">
                    <div class="font-bold text-gray-800 text-sm flex items-center justify-between">
                        <span>💡 ${opp.opportunity}</span>
                        <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-600">${opp.priority}</span>
                    </div>
                    <div class="text-gray-600"><strong>Evidence:</strong> ${opp.evidence}</div>
                    <div class="text-emerald-600"><strong>Impact:</strong> ${opp.projected_impact}</div>
                    <div class="text-coral-600 font-semibold"><strong>Next Step:</strong> ${opp.recommended_next_step}</div>
                </div>
            `;
        });
        html += `</div></div>`;

        // Section 7: Risks & Threats
        html += `
            <div class="glass-panel rounded-2xl p-6 space-y-3 border-l-4 border-l-rose-400">
                <h2 class="text-sm font-bold uppercase tracking-wider text-rose-600 flex items-center space-x-2">
                    <i data-lucide="alert-octagon" class="w-4 h-4"></i>
                    <span>7. Risks & Threats</span>
                </h2>
                <div class="space-y-2 text-xs">
        `;
        (b.risks_threats || []).forEach(r => {
            html += `
                <div class="p-3 rounded-xl bg-rose-50/50 border border-rose-100 space-y-1">
                    <div class="flex items-center justify-between font-bold text-gray-800">
                        <span>⚠️ ${r.risk}</span>
                        <span class="text-[10px] px-2 py-0.5 rounded bg-rose-100 text-rose-600 font-bold">${r.severity} | ${r.urgency}</span>
                    </div>
                    <div class="text-gray-600"><strong>Impact:</strong> ${r.possible_impact}</div>
                </div>
            `;
        });
        html += `</div></div>`;

        // Section 8: Recommended Actions
        html += `
            <div class="glass-panel rounded-2xl p-6 space-y-3">
                <h2 class="text-sm font-bold uppercase tracking-wider text-coral-600 flex items-center space-x-2">
                    <i data-lucide="check-square" class="w-4 h-4"></i>
                    <span>8. Recommended Actions This Week</span>
                </h2>
                <div id="briefActionsList" class="space-y-2 text-xs">
                </div>
            </div>
        `;

        // Section 9: What We Should Watch
        html += `
            <div class="glass-panel rounded-2xl p-6 space-y-3">
                <h2 class="text-sm font-bold uppercase tracking-wider text-purple-600 flex items-center space-x-2">
                    <i data-lucide="eye" class="w-4 h-4"></i>
                    <span>9. What We Should Watch</span>
                </h2>
                <div class="space-y-2 text-xs">
        `;
        (b.what_to_watch || []).forEach(w => {
            html += `
                <div class="p-3 rounded-xl bg-purple-50/50 border border-purple-100 space-y-1">
                    <div class="font-bold text-gray-800">👁️ ${w.trend}</div>
                    <div class="text-gray-600"><strong>Trigger:</strong> ${w.trigger_threshold}</div>
                    <div class="text-purple-600"><strong>Why Monitor:</strong> ${w.why_monitor}</div>
                </div>
            `;
        });
        html += `</div></div>`;

        // Section 10: Source Appendix
        html += `
            <div class="glass-panel rounded-2xl p-6 space-y-3">
                <h2 class="text-sm font-bold uppercase tracking-wider text-gray-500 flex items-center space-x-2">
                    <i data-lucide="paperclip" class="w-4 h-4"></i>
                    <span>10. Source Appendix</span>
                </h2>
                <div class="overflow-x-auto text-xs">
                    <table class="w-full text-left">
                        <thead class="text-gray-400 uppercase bg-gray-50 border-b border-gray-100">
                            <tr>
                                <th class="p-2.5">Source</th>
                                <th class="p-2.5">Date</th>
                                <th class="p-2.5">Snippet</th>
                                <th class="p-2.5">Verification</th>
                                <th class="p-2.5 text-right">Link</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-50">
        `;
        (b.source_appendix || []).forEach(appx => {
            html += `
                <tr class="hover:bg-gray-50/50">
                    <td class="p-2.5 font-bold text-gray-800">${appx.source}</td>
                    <td class="p-2.5 text-gray-500">${appx.pub_date}</td>
                    <td class="p-2.5 text-gray-600 max-w-sm truncate">"${appx.snippet}"</td>
                    <td class="p-2.5"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-600">${appx.status}</span></td>
                    <td class="p-2.5 text-right">
                        <a href="${appx.direct_link}" target="_blank" class="text-coral-500 hover:underline">Open</a>
                    </td>
                </tr>
            `;
        });
        html += `</tbody></table></div></div>`;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();

        // Load interactive action items for Section 8
        await loadBriefActionItems();

    } catch (e) {
        console.error("Failed to load brief:", e);
    }
}

async function loadBriefActionItems() {
    try {
        const resp = await fetch(`/api/briefs/${currentCompanyId}/actions`);
        const actions = await resp.json();
        const container = document.getElementById("briefActionsList");
        if (!container) return;

        container.innerHTML = "";
        actions.forEach(a => {
            const row = document.createElement("div");
            row.className = "p-3 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-between text-xs";
            const isDone = a.status === 'completed';

            row.innerHTML = `
                <div class="flex items-center space-x-3">
                    <button class="btn-toggle-action w-5 h-5 rounded-md border ${isDone ? 'bg-emerald-500 border-emerald-400 text-white' : 'border-gray-300 text-transparent hover:border-coral-400'} flex items-center justify-center transition" data-id="${a.id}" data-status="${a.status}">
                        ✓
                    </button>
                    <div>
                        <div class="font-bold ${isDone ? 'line-through text-gray-400' : 'text-gray-800'}">
                            [${a.priority}] ${a.action_text}
                        </div>
                        <div class="text-[11px] text-gray-500">
                            Reason: ${a.reason} | Owner: <strong class="text-coral-500">${a.suggested_owner}</strong>
                        </div>
                    </div>
                </div>
                <span class="text-[10px] px-2 py-0.5 rounded-full uppercase font-bold ${isDone ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'}">
                    ${a.status}
                </span>
            `;
            container.appendChild(row);
        });

        document.querySelectorAll(".btn-toggle-action").forEach(btn => {
            btn.addEventListener("click", async () => {
                const aid = btn.getAttribute("data-id");
                const curr = btn.getAttribute("data-status");
                const nextStatus = curr === 'completed' ? 'pending' : 'completed';
                await fetch(`/api/briefs/actions/${aid}`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ status: nextStatus })
                });
                await loadBriefActionItems();
            });
        });

    } catch (e) {
        console.error("Failed to load actions:", e);
    }
}

// 6. Load Automation & Audit Status
async function loadAutomationStatus() {
    try {
        const resp = await fetch("/api/scheduler/status");
        const s = await resp.json();

        document.getElementById("schedTimezone").textContent = s.timezone || "Asia/Kolkata";
        document.getElementById("lastWeeklyRun").textContent = s.last_weekly_brief_run || "Pending";
        document.getElementById("nextWeeklyRun").textContent = s.next_weekly_brief_run || "Calculating...";
        document.getElementById("lastMonthlyRun").textContent = s.last_monthly_audit_run || "Pending";
        document.getElementById("nextMonthlyRun").textContent = s.next_monthly_audit_run || "Calculating...";

        // Audit History
        const histResp = await fetch(`/api/audit/${currentCompanyId}/history`);
        const logs = await histResp.json();
        const tbody = document.getElementById("auditHistoryTableBody");
        tbody.innerHTML = "";

        if (logs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-gray-400">No audit logs recorded yet.</td></tr>`;
            return;
        }

        logs.forEach(log => {
            const tr = document.createElement("tr");
            tr.className = "hover:bg-gray-50/50";
            tr.innerHTML = `
                <td class="p-3 text-gray-600">${log.run_date}</td>
                <td class="p-3 uppercase font-bold text-gray-800">${log.run_type}</td>
                <td class="p-3">
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold ${log.status === 'success' ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'}">
                        ${log.status}
                    </span>
                </td>
                <td class="p-3 text-gray-600">${log.dead_urls_count || 0}</td>
                <td class="p-3 text-gray-600">${log.declining_relevance_count || 0}</td>
                <td class="p-3 text-gray-500 text-[11px] max-w-xs truncate">${JSON.stringify(log.report_details || {})}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (e) {
        console.error("Failed to load automation status:", e);
    }
}
