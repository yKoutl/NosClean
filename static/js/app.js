// State variables
let currentTab = 'advisor';
let systemOverviewData = null;
let junkData = null;
let installedAppsData = [];
let commonPaths = {};
let pendingModalAction = null;
let sidebarCollapsed = false;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    initSidebarState();
    await loadCommonPaths();
    loadAdvisor();
    loadOverview();
    // Auto-refresh metrics every 20 seconds
    setInterval(updateQuickMetrics, 20000);

    // Ocultar y remover suavemente el Splash Loader (Capa 4: Cero Pantallas Blancas)
    const splash = document.getElementById('nosclean-splash-loader');
    if (splash) {
        splash.style.opacity = '0';
        splash.style.pointerEvents = 'none';
        setTimeout(() => {
            if (splash.parentNode) splash.parentNode.removeChild(splash);
            checkWelcomeModal();
        }, 400);
    } else {
        checkWelcomeModal();
    }
}

// ======================== SIDEBAR TOGGLE & PERSISTENCE ========================
function initSidebarState() {
    const saved = localStorage.getItem('sidebar_collapsed');
    if (saved !== null) {
        sidebarCollapsed = (saved === 'true');
    } else {
        // Si la pantalla es mediana o pequeña (< 1150px), arranca plegado para ganar espacio
        sidebarCollapsed = (window.innerWidth < 1150);
    }
    applySidebarState();
}

function toggleSidebar() {
    sidebarCollapsed = !sidebarCollapsed;
    localStorage.setItem('sidebar_collapsed', sidebarCollapsed);
    applySidebarState();
}

function applySidebarState() {
    const sidebar = document.getElementById('main-sidebar');
    const toggleIcon = document.getElementById('sidebar-toggle-icon');
    const toggleBtn = document.getElementById('sidebar-toggle-btn');
    const mainContent = document.getElementById('main-content-scroll');
    const body = document.body;

    if (!sidebar) return;

    if (sidebarCollapsed) {
        sidebar.classList.add('collapsed');
        sidebar.classList.remove('manual-expanded');
        body.classList.add('sidebar-is-collapsed');
        if (mainContent) {
            mainContent.style.marginLeft = '68px';
            mainContent.style.width = 'calc(100vw - 68px)';
        }
        if (toggleIcon) toggleIcon.setAttribute('data-lucide', 'chevron-right');
        if (toggleBtn) toggleBtn.title = "Expandir menú lateral";
    } else {
        sidebar.classList.remove('collapsed');
        sidebar.classList.add('manual-expanded');
        body.classList.remove('sidebar-is-collapsed');
        if (mainContent) {
            mainContent.style.marginLeft = '250px';
            mainContent.style.width = 'calc(100vw - 250px)';
        }
        if (toggleIcon) toggleIcon.setAttribute('data-lucide', 'chevron-left');
        if (toggleBtn) toggleBtn.title = "Plegar menú lateral";
    }
    lucide.createIcons();
}

window.addEventListener('resize', () => {
    if (window.innerWidth < 1150 && !localStorage.getItem('sidebar_collapsed')) {
        sidebarCollapsed = true;
        applySidebarState();
    }
});

// ======================== TABS & NAVIGATION ========================
function switchTab(tabId) {
    currentTab = tabId;
    
    // Hide all tabs
    ['advisor', 'overview', 'cleaner', 'heavy', 'apps', 'organizer', 'startup', 'guide', 'about'].forEach(id => {
        const sec = document.getElementById(`tab-${id}`);
        const btn = document.getElementById(`tab-btn-${id}`);
        if (sec) sec.classList.add('hidden');
        if (btn) {
            if (id === 'guide') {
                btn.className = "nav-tab flex items-center space-x-3 w-full px-3 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all bg-amber-500/15 hover:bg-amber-500/25 text-amber-200 border border-amber-500/35 cursor-pointer";
            } else {
                btn.className = "nav-tab flex items-center space-x-3 w-full px-3 py-2 rounded-xl text-xs sm:text-sm font-medium transition-all text-slate-300 hover:text-white hover:bg-[#087A45]/30 border border-transparent";
            }
        }
    });

    // Show active tab
    const activeSec = document.getElementById(`tab-${tabId}`);
    const activeBtn = document.getElementById(`tab-btn-${tabId}`);
    if (activeSec) activeSec.classList.remove('hidden');
    if (activeBtn) {
        if (tabId === 'guide') {
            activeBtn.className = "nav-tab active flex items-center space-x-3 w-full px-3 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all text-white bg-amber-600 border border-amber-400 shadow-md shadow-amber-950/40";
        } else {
            activeBtn.className = "nav-tab active flex items-center space-x-3 w-full px-3 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all text-white bg-[#087A45] border border-[#16B84E]/50 shadow-md";
        }
    }

    // Lazy load tab contents if first time
    if (tabId === 'advisor') {
        loadAdvisor();
    } else if (tabId === 'cleaner' && !junkData) {
        scanJunk();
    } else if (tabId === 'apps' && installedAppsData.length === 0) {
        loadInstalledApps();
    } else if (tabId === 'organizer') {
        scanOrganizer();
    } else if (tabId === 'startup') {
        loadStartupAndProcs();
    }

    lucide.createIcons();
}

function switchGuideTab(subTab) {
    const secManual = document.getElementById('guide-section-manual');
    const secLegal = document.getElementById('guide-section-legal');
    const btnManual = document.getElementById('btn-guide-manual');
    const btnLegal = document.getElementById('btn-guide-legal');

    if (subTab === 'manual') {
        if (secManual) secManual.classList.remove('hidden');
        if (secLegal) secLegal.classList.add('hidden');
        if (btnManual) {
            btnManual.className = "px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all bg-white text-[#087A45] shadow-sm border border-slate-200 cursor-pointer";
        }
        if (btnLegal) {
            btnLegal.className = "px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all text-[#64748B] hover:text-[#102D25] cursor-pointer";
        }
    } else {
        if (secManual) secManual.classList.add('hidden');
        if (secLegal) secLegal.classList.remove('hidden');
        if (btnManual) {
            btnManual.className = "px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all text-[#64748B] hover:text-[#102D25] cursor-pointer";
        }
        if (btnLegal) {
            btnLegal.className = "px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all bg-white text-[#087A45] shadow-sm border border-slate-200 cursor-pointer";
        }
    }
    lucide.createIcons();
}

function refreshCurrentTab() {
    const icon = document.getElementById('refresh-icon');
    if (icon) {
        icon.style.transition = 'transform 0.6s ease';
        icon.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            const el = document.getElementById('refresh-icon');
            if (el) {
                el.style.transition = 'none';
                el.style.transform = '';
            }
        }, 600);
    }

    if (currentTab === 'advisor') loadAdvisor();
    else if (currentTab === 'overview') loadOverview();
    else if (currentTab === 'cleaner') scanJunk();
    else if (currentTab === 'heavy') scanHeavyFiles();
    else if (currentTab === 'apps') loadInstalledApps();
    else if (currentTab === 'organizer') scanOrganizer();
    else if (currentTab === 'startup') loadStartupAndProcs();
}

// ======================== API HELPERS ========================
async function apiGet(endpoint) {
    try {
        const res = await fetch(endpoint);
        if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
        return await res.json();
    } catch (err) {
        console.warn('API error:', err);
        return null;
    }
}

async function apiPost(endpoint, data = {}) {
    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json.detail || 'Error en la operación');
        return json;
    } catch (err) {
        showToast(err.message, 'error');
        return null;
    }
}

async function loadCommonPaths() {
    const data = await apiGet('/api/storage/common-paths');
    if (data) {
        commonPaths = data;
        const heavyInput = document.getElementById('heavy-path-input');
        if (heavyInput) heavyInput.value = data.user_profile || '';
    }
}

// ======================== TAB: ADVISOR (CONSEJOS) ========================
async function loadAdvisor() {
    const scoreEl = document.getElementById('advisor-score');
    const statusEl = document.getElementById('advisor-status');
    const grid = document.getElementById('advisor-recommendations-grid');

    if (scoreEl) scoreEl.textContent = "...";
    if (statusEl) statusEl.textContent = "Analizando estado de tu PC...";
    
    grid.innerHTML = `
        <div class="col-span-2 text-center py-12 text-slate-400">
            <i data-lucide="loader-2" class="w-6 h-6 text-amber-400 animate-spin mx-auto mb-2"></i>
            <span>Evaluando almacenamiento, arranque y programas...</span>
        </div>
    `;
    lucide.createIcons();

    const data = await apiGet('/api/advisor/recommendations');
    if (!data) {
        grid.innerHTML = `<div class="col-span-2 text-center py-8 text-rose-400">Error al recopilar el diagnóstico. Revisa que el servidor esté activo.</div>`;
        return;
    }

    if (scoreEl) scoreEl.textContent = data.health_score;
    if (statusEl) statusEl.textContent = `Estado: ${data.health_status}`;

    if (!data.recommendations || data.recommendations.length === 0) {
        grid.innerHTML = `
            <div class="col-span-2 glass-card rounded-2xl p-6 text-center text-[#087A45] border border-slate-200 bg-white shadow-sm">
                <i data-lucide="check-circle" class="w-10 h-10 mx-auto mb-2 text-[#16B84E]"></i>
                <h4 class="text-base font-bold text-[#102D25]">¡Tu equipo está en óptimas condiciones!</h4>
                <p class="text-xs text-[#64748B] mt-1">No se detectaron problemas críticos de almacenamiento ni saturación de inicio.</p>
            </div>
        `;
        lucide.createIcons();
        return;
    }

    grid.innerHTML = '';
    data.recommendations.forEach(rec => {
        const card = document.createElement('div');
        const badgeColors = {
            rose: 'bg-rose-50 text-rose-700 border-rose-200',
            amber: 'bg-amber-50 text-amber-700 border-amber-200',
            emerald: 'bg-[#16B84E]/15 text-[#087A45] border-[#16B84E]/30'
        };

        const btnColors = {
            rose: 'bg-rose-600 hover:bg-rose-500 text-white shadow-sm',
            amber: 'bg-amber-600 hover:bg-amber-500 text-white shadow-sm',
            emerald: 'bg-[#087A45] hover:bg-[#066237] text-white shadow-sm'
        };

        const actionCall = rec.action_type === 'windows_tool'
            ? `openWindowsTool('${rec.action_target}')`
            : `switchTab('${rec.action_target}')`;

        card.className = "glass-card rounded-2xl p-5 flex flex-col justify-between border border-slate-200 bg-white shadow-sm";
        card.innerHTML = `
            <div>
                <div class="flex items-center justify-between mb-2">
                    <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${badgeColors[rec.color] || badgeColors.amber}">
                        ${rec.badge}
                    </span>
                    <span class="text-[11px] uppercase font-bold text-[#64748B]">Prioridad ${rec.priority}</span>
                </div>
                <h4 class="text-base font-bold text-[#102D25] mt-1">${rec.title}</h4>
                <p class="text-xs text-[#64748B] mt-1.5 leading-relaxed">${rec.description}</p>
            </div>
            <div class="mt-4 pt-3 border-t border-slate-100 flex justify-end">
                <button onclick="${actionCall}" class="px-4 py-2 rounded-xl text-xs font-semibold shadow-sm flex items-center space-x-1.5 transition-all cursor-pointer ${btnColors[rec.color] || btnColors.amber}">
                    <span>${rec.action_label}</span>
                    <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
                </button>
            </div>
        `;
        grid.appendChild(card);
    });

    lucide.createIcons();
}

// ======================== TAB 1: OVERVIEW ========================
async function loadOverview() {
    const data = await apiGet('/api/system/overview');
    if (!data) return;
    systemOverviewData = data;

    // Header pills
    document.getElementById('pill-user').textContent = `${data.os.user} (${data.os.hostname})`;
    document.getElementById('pill-uptime').textContent = `Activo: ${data.os.uptime}`;

    // System banner
    document.getElementById('pc-hostname').textContent = `${data.os.hostname} - ${data.os.user}`;
    document.getElementById('os-badge').textContent = `${data.os.system} ${data.os.release}`;
    document.getElementById('os-arch').textContent = data.os.architecture;
    document.getElementById('os-details').textContent = `Compilación ${data.os.version} • Iniciado: ${data.os.boot_time}`;

    // CPU Card
    document.getElementById('cpu-name').textContent = data.cpu.name;
    document.getElementById('cpu-name').title = data.cpu.name;
    document.getElementById('cpu-usage').textContent = `${data.cpu.usage_percent}%`;
    document.getElementById('cpu-cores').textContent = `${data.cpu.physical_cores} núcleos / ${data.cpu.total_cores} hilos`;
    document.getElementById('cpu-bar').style.width = `${Math.min(data.cpu.usage_percent, 100)}%`;

    // RAM Card
    document.getElementById('ram-used').textContent = data.ram.used_formatted;
    document.getElementById('ram-total').textContent = `de ${data.ram.total_formatted}`;
    document.getElementById('ram-free').textContent = `Disponible: ${data.ram.free_formatted}`;
    document.getElementById('ram-bar').style.width = `${data.ram.percent_used}%`;

    // GPU Card
    if (data.gpus && data.gpus.length > 0) {
        const gpu = data.gpus[0];
        document.getElementById('gpu-name').textContent = gpu.name;
        document.getElementById('gpu-vram').textContent = `VRAM: ${gpu.vram}`;
        document.getElementById('gpu-driver').textContent = `Driver: ${gpu.driver_version}`;
    } else {
        document.getElementById('gpu-name').textContent = "Gráficos Integrados";
    }

    // Battery Card
    if (data.battery) {
        document.getElementById('battery-pct').textContent = `${data.battery.percent}%`;
        document.getElementById('battery-status').textContent = data.battery.power_plugged ? "Cargando (AC)" : "Batería";
        document.getElementById('battery-bar').style.width = `${data.battery.percent}%`;
        document.getElementById('battery-detail').textContent = data.battery.power_plugged ? "Conectado a la corriente" : "Modo Batería";
    } else {
        document.getElementById('battery-pct').textContent = "100%";
        document.getElementById('battery-status').textContent = "PC de Escritorio";
        document.getElementById('battery-detail').textContent = "Conectado a la corriente (AC)";
        document.getElementById('battery-bar').style.width = `100%`;
    }

    // Hard Drives Grid
    const drivesContainer = document.getElementById('drives-container');
    drivesContainer.innerHTML = '';
    data.drives.forEach(drive => {
        const isAlert = drive.percent_used > 85;
        const barColor = isAlert ? 'bg-rose-500' : 'bg-[#16B84E]';

        const card = document.createElement('div');
        card.className = "glass-card rounded-2xl p-5 border border-slate-200 bg-white shadow-sm";
        card.innerHTML = `
            <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-2.5">
                    <span class="p-2 rounded-xl bg-[#F4F7F5] text-[#102D25] font-black text-sm border border-slate-200">${drive.device}</span>
                    <div>
                        <h4 class="text-sm font-bold text-[#102D25]">Disco Local (${drive.mountpoint})</h4>
                        <span class="text-xs text-[#64748B] font-mono">${drive.fstype}</span>
                    </div>
                </div>
                <span class="px-2.5 py-1 rounded-full text-xs font-bold ${isAlert ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-[#F4F7F5] text-[#102D25] border border-slate-200'}">
                    ${drive.percent_used}% Usado
                </span>
            </div>

            <div class="mt-4">
                <div class="flex justify-between text-xs text-[#64748B] mb-1.5 font-medium">
                    <span>Libre: <strong class="text-[#087A45] font-bold">${drive.free_formatted}</strong></span>
                    <span>Total: ${drive.total_formatted}</span>
                </div>
                <div class="w-full bg-[#E2E8F0] rounded-full h-3 overflow-hidden">
                    <div class="${barColor} h-3 rounded-full transition-all duration-700" style="width: ${drive.percent_used}%"></div>
                </div>
            </div>

            <div class="mt-4 pt-3 border-t border-slate-100 flex justify-end space-x-2">
                <button onclick="scanDriveInHeavy('${drive.mountpoint.replace(/\\/g, '\\\\')}')" class="px-3 py-1.5 rounded-xl bg-white hover:bg-slate-50 text-xs font-semibold text-[#102D25] border border-slate-200 flex items-center space-x-1.5 transition-colors shadow-sm cursor-pointer">
                    <i data-lucide="search" class="w-3.5 h-3.5 text-[#087A45]"></i>
                    <span>Buscar Gigantes</span>
                </button>
                <button onclick="openFolderInExplorer('${drive.mountpoint.replace(/\\/g, '\\\\')}')" class="px-3 py-1.5 rounded-xl bg-white hover:bg-slate-50 text-xs font-semibold text-[#102D25] border border-slate-200 flex items-center space-x-1.5 transition-colors shadow-sm cursor-pointer">
                    <i data-lucide="folder" class="w-3.5 h-3.5 text-[#087A45]"></i>
                    <span>Abrir en Explorer</span>
                </button>
            </div>
        `;
        drivesContainer.appendChild(card);
    });

    lucide.createIcons();
}

async function updateQuickMetrics() {
    const data = await apiGet('/api/system/overview');
    if (!data) return;
    document.getElementById('cpu-usage').textContent = `${data.cpu.usage_percent}%`;
    document.getElementById('cpu-bar').style.width = `${Math.min(data.cpu.usage_percent, 100)}%`;
    document.getElementById('ram-used').textContent = data.ram.used_formatted;
    document.getElementById('ram-free').textContent = `Disponible: ${data.ram.free_formatted}`;
    document.getElementById('ram-bar').style.width = `${data.ram.percent_used}%`;
}

// ======================== TAB 2: JUNK CLEANER ========================
async function scanJunkAuto() {
    await scanJunk();
}

async function scanJunk() {
    const btn = document.getElementById('btn-scan-junk');
    const statusLabel = document.getElementById('junk-status-label');
    if (btn) btn.disabled = true;
    if (statusLabel) {
        statusLabel.className = "text-sm font-semibold text-[#087A45] mt-2 flex items-center space-x-1.5";
        statusLabel.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Escaneando carpetas temporales...</span>';
        lucide.createIcons();
    }

    const data = await apiGet('/api/junk/scan');
    if (btn) btn.disabled = false;
    if (!data) return;
    junkData = data;

    document.getElementById('junk-total-size').textContent = data.total_formatted;
    document.getElementById('junk-total-files').textContent = data.total_files.toLocaleString();
    
    if (statusLabel) {
        statusLabel.className = "text-sm font-semibold text-emerald-400 mt-2 flex items-center space-x-1.5";
        statusLabel.innerHTML = '<i data-lucide="check-circle" class="w-4 h-4"></i><span>Análisis finalizado</span>';
    }

    renderJunkCategories(data.categories);
    lucide.createIcons();
}

function renderJunkCategories(categories) {
    const container = document.getElementById('junk-categories-list');
    container.innerHTML = '';

    categories.forEach(cat => {
        const item = document.createElement('div');
        item.className = "flex items-center justify-between p-3.5 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 transition-colors shadow-sm";
        
        const hasItems = cat.size_bytes > 0 || cat.file_count > 0;
        const checked = hasItems ? 'checked' : 'disabled';
        const opacity = hasItems ? 'opacity-100' : 'opacity-40';

        item.innerHTML = `
            <div class="flex items-center space-x-3 ${opacity}">
                <input type="checkbox" id="chk-junk-${cat.id}" data-id="${cat.id}" ${checked} class="w-4 h-4 text-[#087A45] rounded border-slate-300 focus:ring-[#087A45] cursor-pointer">
                <div>
                    <h4 class="text-sm font-semibold text-[#102D25]">${cat.name}</h4>
                    <p class="text-xs text-[#64748B]">${cat.description}</p>
                </div>
            </div>
            <div class="text-right">
                <span class="text-sm font-bold ${hasItems ? 'text-[#087A45]' : 'text-slate-400'}">${cat.size_formatted}</span>
                <p class="text-xs text-[#64748B]">${cat.file_count.toLocaleString()} archivos</p>
            </div>
        `;
        container.appendChild(item);
    });
}

function toggleAllJunk(select) {
    const checkboxes = document.querySelectorAll('#junk-categories-list input[type="checkbox"]:not(:disabled)');
    checkboxes.forEach(chk => chk.checked = select);
}

function confirmCleanSelected() {
    const selected = [];
    const checkboxes = document.querySelectorAll('#junk-categories-list input[type="checkbox"]:checked');
    checkboxes.forEach(chk => selected.push(chk.getAttribute('data-id')));

    if (selected.length === 0) {
        showToast('No seleccionaste ninguna categoría para limpiar', 'warning');
        return;
    }

    openConfirmModal(
        'Confirmar Limpieza de Basura',
        `Se eliminarán los archivos temporales y cachés de ${selected.length} categorías seleccionadas. Los archivos que estén abiertos o en uso serán omitidos automáticamente de forma segura.`,
        () => executeJunkClean(selected)
    );
}

async function executeJunkClean(selectedCategories) {
    const btn = document.getElementById('btn-clean-junk');
    if (btn) btn.disabled = true;
    showToast('Iniciando limpieza...', 'info');

    const res = await apiPost('/api/junk/clean', { categories: selectedCategories });
    if (btn) btn.disabled = false;

    if (res && res.success) {
        showToast(`¡Limpieza completada! Se liberaron ${res.freed_formatted} (${res.total_files_deleted} archivos eliminados)`, 'success');
        await scanJunk();
        await loadOverview();
        if (currentTab === 'advisor') loadAdvisor();
    }
}

// ======================== TAB 3: HEAVY FILES ========================
function onHeavyPresetChange() {
    const select = document.getElementById('heavy-path-select');
    const input = document.getElementById('heavy-path-input');
    const val = select.value;

    if (val === 'custom') {
        input.focus();
    } else if (commonPaths[val]) {
        input.value = commonPaths[val];
    }
}

function scanDriveInHeavy(drivePath) {
    switchTab('heavy');
    const input = document.getElementById('heavy-path-input');
    const select = document.getElementById('heavy-path-select');
    if (input) input.value = drivePath;
    if (select) select.value = 'custom';
    scanHeavyFiles();
}

async function scanHeavyFiles() {
    const pathInput = document.getElementById('heavy-path-input');
    const minSizeSelect = document.getElementById('heavy-min-size');
    const btn = document.getElementById('btn-scan-heavy');
    const tbody = document.getElementById('heavy-files-tbody');

    const targetPath = pathInput.value.trim();
    if (!targetPath) {
        showToast('Debes ingresar o seleccionar una ruta para escanear', 'warning');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Buscando...</span>';
    lucide.createIcons();

    tbody.innerHTML = `
        <tr>
            <td colspan="5" class="text-center py-12 text-slate-400">
                <div class="flex flex-col items-center justify-center space-y-3">
                    <i data-lucide="loader-2" class="w-7 h-7 text-[#087A45] animate-spin"></i>
                    <span>Analizando carpetas y buscando archivos grandes... Esto puede tardar unos segundos.</span>
                </div>
            </td>
        </tr>
    `;
    lucide.createIcons();

    const minSize = parseInt(minSizeSelect.value) || 100;
    const url = `/api/storage/heavy-files?path=${encodeURIComponent(targetPath)}&min_size_mb=${minSize}&max_results=150`;
    const data = await apiGet(url);

    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="search" class="w-4 h-4"></i><span>Buscar Archivos</span>';
    lucide.createIcons();

    if (!data || data.error) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-8 text-rose-400">${data?.error || 'Error al buscar archivos'}</td></tr>`;
        return;
    }

    document.getElementById('heavy-results-badge').textContent = `${data.found_count} archivos`;
    document.getElementById('heavy-total-found-size').textContent = `Total: ${data.total_size_formatted}`;

    if (data.files.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-10 text-slate-400">No se encontraron archivos que superen los ${minSize} MB en esta ruta.</td></tr>`;
        return;
    }

    tbody.innerHTML = '';
    data.files.forEach(f => {
        const row = document.createElement('tr');
        row.className = "hover:bg-slate-50 transition-colors border-b border-slate-100";
        row.innerHTML = `
            <td class="px-4 py-3">
                <div class="flex items-center space-x-2">
                    <i data-lucide="file" class="w-4 h-4 text-[#087A45] flex-shrink-0"></i>
                    <span class="font-bold text-[#102D25] truncate max-w-xs" title="${f.name}">${f.name}</span>
                </div>
            </td>
            <td class="px-4 py-3 font-bold text-[#087A45]">${f.size_formatted}</td>
            <td class="px-4 py-3 text-xs text-slate-400 truncate max-w-sm" title="${f.path}">${f.folder}</td>
            <td class="px-4 py-3 text-xs text-[#64748B]">${f.modified}</td>
            <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end space-x-2">
                    <button onclick="openFolderInExplorer('${f.path.replace(/\\/g, '\\\\')}')" title="Mostrar en Explorador" class="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 transition-colors">
                        <i data-lucide="folder" class="w-4 h-4"></i>
                    </button>
                    <button onclick="confirmRecycleFile('${f.path.replace(/\\/g, '\\\\')}', '${f.name}')" title="Mover a Papelera" class="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-900/50 text-rose-400 transition-colors">
                        <i data-lucide="trash-2" class="w-4 h-4"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });

    lucide.createIcons();
}

function confirmRecycleFile(filePath, fileName) {
    openConfirmModal(
        'Mover a Papelera de Reciclaje',
        `¿Deseas enviar "${fileName}" a la Papelera de Reciclaje de Windows? Podrás restaurarlo desde la papelera si lo necesitas.`,
        async () => {
            const res = await apiPost('/api/actions/recycle', { path: filePath });
            if (res && res.success) {
                showToast(`"${fileName}" enviado a la papelera`, 'success');
                scanHeavyFiles();
            }
        }
    );
}

// ======================== TAB 4: INSTALLED APPS ========================
async function loadInstalledApps() {
    const tbody = document.getElementById('apps-tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center py-10 text-slate-400">
                <div class="flex flex-col items-center space-y-2">
                    <i data-lucide="loader-2" class="w-6 h-6 text-[#087A45] animate-spin"></i>
                    <span class="text-[#102D25] font-bold">Analizando registro de Windows...</span>
                </div>
            </td>
        </tr>
    `;
    lucide.createIcons();

    const data = await apiGet('/api/software/installed');
    if (!data) return;
    installedAppsData = data;
    renderAppsTable(data);
}

function renderAppsTable(apps) {
    const tbody = document.getElementById('apps-tbody');
    const badge = document.getElementById('apps-count-badge');
    badge.textContent = `${apps.length} programas`;

    if (apps.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-10 text-slate-400">No se encontraron programas con ese criterio.</td></tr>`;
        return;
    }

    tbody.innerHTML = '';
    apps.forEach(app => {
        const row = document.createElement('tr');
        row.className = "hover:bg-slate-50 transition-colors border-b border-slate-100";
        
        const googleSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(app.name)}`;

        row.innerHTML = `
            <td class="px-4 py-3">
                <div class="flex items-center space-x-2">
                    <i data-lucide="package" class="w-4 h-4 text-[#087A45] flex-shrink-0"></i>
                    <span class="font-semibold text-[#102D25] max-w-sm truncate" title="${app.name}">${app.name}</span>
                </div>
            </td>
            <td class="px-4 py-3 text-xs text-[#64748B] truncate max-w-xs" title="${app.publisher}">${app.publisher}</td>
            <td class="px-4 py-3 text-xs font-mono text-[#64748B]">${app.version}</td>
            <td class="px-4 py-3 text-xs font-bold text-[#087A45]">${app.size_formatted}</td>
            <td class="px-4 py-3 text-xs text-[#64748B]">${app.install_date}</td>
            <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end space-x-2">
                    <a href="${googleSearchUrl}" target="_blank" title="Buscar información en Google" class="p-1.5 rounded-xl bg-white hover:bg-slate-50 text-[#102D25] border border-slate-200 shadow-sm transition-colors cursor-pointer">
                        <i data-lucide="globe" class="w-3.5 h-3.5"></i>
                    </a>
                    <button onclick="openWindowsTool('appsfeatures')" title="Abrir en Desinstalador de Windows" class="p-1.5 rounded-lg bg-slate-800 hover:bg-blue-600/30 text-blue-400 transition-colors">
                        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });

    lucide.createIcons();
}

function filterApps() {
    const q = document.getElementById('apps-search-input').value.toLowerCase().trim();
    if (!q) {
        sortApps();
        return;
    }
    const filtered = installedAppsData.filter(a => 
        a.name.toLowerCase().includes(q) || 
        a.publisher.toLowerCase().includes(q)
    );
    renderAppsTable(filtered);
}

function sortApps() {
    const sortVal = document.getElementById('apps-sort-select').value;
    const q = document.getElementById('apps-search-input').value.toLowerCase().trim();
    
    let list = [...installedAppsData];
    if (q) {
        list = list.filter(a => a.name.toLowerCase().includes(q) || a.publisher.toLowerCase().includes(q));
    }

    if (sortVal === 'size_desc') {
        list.sort((a, b) => b.size_bytes - a.size_bytes);
    } else if (sortVal === 'name_asc') {
        list.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortVal === 'date_desc') {
        list.sort((a, b) => b.install_date.localeCompare(a.install_date));
    }

    renderAppsTable(list);
}

// ======================== TAB 5: ORGANIZER ========================
function onOrganizerPresetChange() {
    scanOrganizer();
}

async function scanOrganizer() {
    const preset = document.getElementById('organizer-preset-select').value;
    const targetPath = commonPaths[preset] || commonPaths.downloads;
    const tbody = document.getElementById('organizer-tbody');
    
    tbody.innerHTML = `
        <tr>
            <td colspan="5" class="text-center py-10 text-slate-400">
                <i data-lucide="loader-2" class="w-6 h-6 text-amber-400 animate-spin mx-auto mb-2"></i>
                <span>Escaneando archivos sueltos...</span>
            </td>
        </tr>
    `;
    lucide.createIcons();

    const data = await apiGet(`/api/organizer/scan?path=${encodeURIComponent(targetPath)}`);
    if (!data || !data.category_summary) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-8 text-rose-400">No se pudo escanear la carpeta seleccionada.</td></tr>`;
        return;
    }

    // Render categories stats grid
    const catGrid = document.getElementById('organizer-cat-grid');
    catGrid.innerHTML = '';
    
    const catIcons = {
        'Instaladores': 'package',
        'Comprimidos': 'archive',
        'Documentos': 'file-text',
        'Imágenes': 'image',
        'Videos': 'film',
        'Música y Audio': 'music',
        'Código y Scripts': 'code',
        'Otros': 'folder'
    };

    for (const [catName, catStat] of Object.entries(data.category_summary)) {
        if (catStat.count > 0 || ['Instaladores', 'Documentos', 'Comprimidos', 'Imágenes'].includes(catName)) {
            const card = document.createElement('div');
            card.className = "bg-white p-3 rounded-xl border border-slate-200 text-center shadow-sm";
            card.innerHTML = `
                <div class="flex items-center justify-center text-[#087A45] mb-1">
                    <i data-lucide="${catIcons[catName] || 'file'}" class="w-4 h-4"></i>
                </div>
                <p class="text-xs font-semibold text-[#102D25] truncate">${catName}</p>
                <p class="text-base font-extrabold text-[#087A45] mt-0.5">${catStat.count}</p>
                <p class="text-[10px] text-[#64748B]">${catStat.size_formatted}</p>
            `;
            catGrid.appendChild(card);
        }
    }

    // Render loose files
    document.getElementById('organizer-files-count').textContent = `${data.total_files} archivos sueltos (${data.total_size_formatted})`;

    if (!data.files || data.files.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-10">
            <div class="flex items-center justify-center space-x-2 text-[#087A45] font-bold text-sm">
                <i data-lucide="check-circle" class="w-5 h-5 text-[#087A45]"></i>
                <span>Carpeta limpia y ordenada. No hay archivos sueltos pendientes de organizar.</span>
            </div>
        </td></tr>`;
        lucide.createIcons();
        return;
    }

    tbody.innerHTML = '';
    data.files.forEach(f => {
        const row = document.createElement('tr');
        row.className = "hover:bg-slate-50 transition-colors border-b border-slate-100";
        
        let ageBadge = `<span class="px-2 py-0.5 rounded text-[11px] bg-[#F4F7F5] text-[#102D25] border border-slate-200">${f.age_days} días</span>`;
        if (f.age_days >= 90) {
            ageBadge = `<span class="px-2 py-0.5 rounded text-[11px] bg-rose-500/20 text-rose-700 font-semibold">${f.age_days} días (Antiguo)</span>`;
        }

        row.innerHTML = `
            <td class="px-4 py-3">
                <div class="flex items-center space-x-2">
                    <i data-lucide="file" class="w-4 h-4 text-emerald-600 flex-shrink-0"></i>
                    <span class="font-bold text-[#102D25] max-w-xs truncate" title="${f.name}">${f.name}</span>
                </div>
            </td>
            <td class="px-4 py-3">
                <span class="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-50 text-[#087A45] border border-emerald-200 inline-flex items-center space-x-1">
                    <i data-lucide="folder" class="w-3.5 h-3.5 text-[#087A45]"></i>
                    <span>${f.category}</span>
                </span>
            </td>
            <td class="px-4 py-3 text-xs font-bold text-[#102D25]">${f.size_formatted}</td>
            <td class="px-4 py-3 text-xs">${ageBadge}</td>
            <td class="px-4 py-3 text-right">
                <button onclick="openFolderInExplorer('${f.path.replace(/\\/g, '\\\\')}')" title="Ver archivo" class="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-[#087A45] border border-slate-300 transition-colors">
                    <i data-lucide="folder" class="w-4 h-4"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });

    lucide.createIcons();
}

async function organizeFiles(simulate) {
    const preset = document.getElementById('organizer-preset-select').value;
    const targetPath = commonPaths[preset] || commonPaths.downloads;

    if (simulate) {
        const res = await apiPost('/api/organizer/organize', { path: targetPath, simulate: true });
        if (res) {
            showToast(`Vista previa: Se clasificarán ${res.total_moved} archivos en sus respectivas subcarpetas`, 'info');
        }
    } else {
        openConfirmModal(
            'Confirmar Organización Automática',
            `Los archivos sueltos se moverán a carpetas clasificadas (ej: Descargas/Instaladores, Descargas/Documentos, etc.). Tus archivos quedarán totalmente ordenados.`,
            async () => {
                const res = await apiPost('/api/organizer/organize', { path: targetPath, simulate: false });
                if (res && res.success) {
                    showToast(`¡Excelente! Se organizaron ${res.total_moved} archivos correctamente`, 'success');
                    await scanOrganizer();
                }
            }
        );
    }
}

// ======================== TAB 6: STARTUP & TASKS ========================
async function loadStartupAndProcs() {
    loadStartupApps();
    loadProcesses();
}

async function loadStartupApps() {
    const tbody = document.getElementById('startup-tbody');
    const badge = document.getElementById('startup-count-badge');
    
    tbody.innerHTML = `<tr><td colspan="4" class="text-center py-8 text-slate-400"><i data-lucide="loader-2" class="w-5 h-5 animate-spin mx-auto"></i></td></tr>`;
    lucide.createIcons();

    const data = await apiGet('/api/software/startup');
    if (!data) return;

    badge.textContent = `${data.length} aplicaciones`;
    tbody.innerHTML = '';

    data.forEach(item => {
        const row = document.createElement('tr');
        row.className = "hover:bg-slate-50 transition-colors border-b border-slate-100";
        row.innerHTML = `
            <td class="px-4 py-3 font-bold text-[#102D25]">
                <div class="flex items-center space-x-2">
                    <i data-lucide="zap" class="w-4 h-4 text-emerald-400 flex-shrink-0"></i>
                    <span>${item.name}</span>
                </div>
            </td>
            <td class="px-4 py-3 text-xs text-slate-400 font-medium">${item.location}</td>
            <td class="px-4 py-3 text-xs font-mono text-slate-400 truncate max-w-md" title="${item.command}">${item.command}</td>
            <td class="px-4 py-3 text-right">
                <button onclick="openWindowsTool('startup')" title="Desactivar en Windows" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-emerald-400 border border-slate-700">
                    Administrar
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });

    lucide.createIcons();
}

async function loadProcesses() {
    const container = document.getElementById('top-procs-grid');
    container.innerHTML = '<div class="col-span-2 text-center py-6 text-slate-400">Cargando procesos activos...</div>';

    const data = await apiGet('/api/system/processes?limit=8');
    if (!data) return;

    container.innerHTML = '';
    data.by_memory.forEach(p => {
        const card = document.createElement('div');
        card.className = "flex items-center justify-between p-3 rounded-xl bg-white border border-slate-200 shadow-sm";
        card.innerHTML = `
            <div class="flex items-center space-x-2.5">
                <div class="p-2 rounded-lg bg-[#16B84E]/10 text-[#087A45]">
                    <i data-lucide="activity" class="w-4 h-4"></i>
                </div>
                <div>
                    <h5 class="text-sm font-semibold text-[#102D25] max-w-[180px] truncate" title="${p.name}">${p.name}</h5>
                    <span class="text-[11px] text-[#64748B]">PID: ${p.pid} • CPU: ${p.cpu_percent}%</span>
                </div>
            </div>
            <div class="text-right">
                <span class="text-sm font-bold text-[#087A45]">${p.memory_formatted}</span>
                <p class="text-[11px] text-[#64748B]">${p.memory_percent}% RAM</p>
            </div>
        `;
        container.appendChild(card);
    });

    lucide.createIcons();
}

// ======================== WINDOWS TOOLS & COMMON ACTIONS ========================
async function openWindowsTool(toolName) {
    const res = await apiPost('/api/actions/open-tool', { tool: toolName });
    if (res && res.success) {
        showToast(`Abriendo herramienta: ${toolName}`, 'info');
    }
}

async function openFolderInExplorer(path) {
    const res = await apiPost('/api/actions/open-explorer', { path: path });
    if (res && res.success) {
        showToast('Abierto en Explorador de Windows', 'info');
    }
}

// ======================== MODAL & TOASTS ========================
function openConfirmModal(title, message, onConfirm) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-message').textContent = message;
    pendingModalAction = onConfirm;

    const modal = document.getElementById('confirm-modal');
    modal.classList.remove('hidden');

    const confirmBtn = document.getElementById('modal-confirm-btn');
    confirmBtn.onclick = () => {
        closeConfirmModal(true);
    };
}

function closeConfirmModal(confirmed) {
    const modal = document.getElementById('confirm-modal');
    modal.classList.add('hidden');
    if (confirmed && typeof pendingModalAction === 'function') {
        pendingModalAction();
    }
    pendingModalAction = null;
}

// ======================== MODAL DE BIENVENIDA (ONBOARDING) ========================
function checkWelcomeModal() {
    const dismissed = localStorage.getItem('nosclean_welcome_dismissed');
    if (!dismissed) {
        setTimeout(() => {
            showWelcomeModal();
        }, 300);
    }
}

function showWelcomeModal() {
    const modal = document.getElementById('welcome-modal');
    if (modal) {
        modal.classList.remove('hidden');
        lucide.createIcons();
    }
}

function closeWelcomeModal() {
    const modal = document.getElementById('welcome-modal');
    const dontShow = document.getElementById('welcome-dont-show');
    if (dontShow && dontShow.checked) {
        localStorage.setItem('nosclean_welcome_dismissed', 'true');
    }
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Escuchar tecla ESC para cerrar cualquier modal abierto
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const welcomeModal = document.getElementById('welcome-modal');
        if (welcomeModal && !welcomeModal.classList.contains('hidden')) {
            closeWelcomeModal();
        }
        const confirmModal = document.getElementById('confirm-modal');
        if (confirmModal && !confirmModal.classList.contains('hidden')) {
            closeConfirmModal(false);
        }
    }
});

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    
    const colors = {
        success: 'border-[#16B84E] bg-white text-[#087A45] shadow-lg shadow-[#087A45]/10',
        error: 'border-rose-300 bg-white text-rose-700 shadow-lg shadow-rose-500/10',
        warning: 'border-amber-300 bg-white text-amber-700 shadow-lg shadow-amber-500/10',
        info: 'border-slate-300 bg-white text-[#102D25] shadow-lg'
    };

    const icons = {
        success: 'check-circle',
        error: 'alert-circle',
        warning: 'alert-triangle',
        info: 'info'
    };

    toast.className = `flex items-center space-x-2.5 px-4 py-3 rounded-xl border shadow-2xl backdrop-blur-md text-xs font-medium pointer-events-auto transition-all transform duration-300 ${colors[type] || colors.info}`;
    toast.innerHTML = `
        <i data-lucide="${icons[type] || 'info'}" class="w-4 h-4 flex-shrink-0"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
        toast.classList.add('opacity-0', 'scale-95');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ======================== OPTIMIZACIÓN RÁPIDA EN 1 CLIC ========================
async function quickOptimizePC() {
    const btn = document.getElementById('btn-quick-optimize');
    const label = document.getElementById('optimize-label');
    const icon = document.getElementById('optimize-icon');
    
    if (btn) {
        btn.disabled = true;
        btn.classList.add('opacity-75', 'cursor-wait');
    }
    if (label) label.innerText = 'Optimizando...';
    if (icon) icon.classList.add('animate-pulse');

    showToast('Iniciando optimización rápida (liberando RAM inactiva y cachés)...', 'info');

    try {
        const res = await fetch('/api/system/optimize', { method: 'POST' });
        const data = await res.json();

        if (data.success) {
            const ramText = data.ram_freed_formatted || '0 B';
            const diskText = data.disk_freed_formatted || '0 B';
            
            showToast(`Optimización completada. Se liberaron ${ramText} de RAM y ${diskText} de disco. Nueva RAM: ${data.new_ram_used_gb} GB (${data.new_ram_percent}%).`, 'success');
            
            // Refrescar métricas de inmediato
            await loadOverview();
            if (currentTab === 'cleaner') {
                await scanJunk();
            }
        } else {
            showToast('Ocurrió un error al optimizar el equipo.', 'error');
        }
    } catch (err) {
        showToast(`Error al optimizar: ${err.message}`, 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.classList.remove('opacity-75', 'cursor-wait');
        }
        if (label) label.innerText = 'Optimizar PC';
        if (icon) {
            icon.classList.remove('animate-pulse');
            icon.classList.remove('animate-spin');
        }
        lucide.createIcons();
    }
}

// ======================== APAGAR Y SALIR (0 MB DE CONSUMO - CERO VENTANAS NATIVAS) ========================
function shutdownApp() {
    openConfirmModal(
        'Apagar y Salir',
        '¿Deseas cerrar NosClean por completo? Dejará de consumir memoria y procesador en segundo plano (0 MB). Podrás volver a abrirla cuando quieras desde el acceso directo de tu Escritorio.',
        async () => {
            try {
                await fetch('/api/system/shutdown', { method: 'POST' });
            } catch {}
            document.body.innerHTML = `
                <div class="h-screen w-screen bg-[#F4F7F5] flex flex-col items-center justify-center text-[#102D25] p-6 text-center">
                    <div class="h-16 w-16 rounded-2xl bg-[#16B84E]/10 border border-[#16B84E]/30 flex items-center justify-center text-[#087A45] mb-4 shadow-sm">
                        <i data-lucide="power" class="w-8 h-8"></i>
                    </div>
                    <h1 class="text-2xl font-black text-[#102D25] mb-2">NosClean Apagado</h1>
                    <p class="text-[#64748B] text-sm max-w-md mb-6">El panel se ha cerrado por completo. Actualmente consume <span class="text-[#087A45] font-bold">0 MB de RAM y 0% de CPU</span>.</p>
                    <p class="text-slate-400 text-xs">Ya puedes cerrar esta pestaña del navegador de forma segura. Para volver a iniciar, abre el acceso directo en tu Escritorio.</p>
                </div>
            `;
            lucide.createIcons();
        }
    );
}
