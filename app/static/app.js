const apiBase = "/";

function dom(id) {
  return document.getElementById(id);
}

function fetchJson(path, opts = {}) {
  return fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  }).then(async (response) => {
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Error ${response.status}: ${text}`);
    }
    return response.json();
  });
}

// NAVEGACIÓN PRINCIPAL
function showSection(sectionId) {
  document.querySelectorAll(".page").forEach((section) => {
    section.classList.toggle("active", section.id === sectionId);
  });
  document.querySelectorAll("nav button").forEach((button) => {
    button.classList.toggle("active", button.dataset.section === sectionId);
  });

  switch (sectionId) {
    case "dashboard":
      loadDashboard();
      break;
    case "contenido":
      initContenido();
      break;
    case "analisis":
      initAnalisis();
      break;
    case "automatizacion":
      loadAutomation();
      loadAutomationRuns();
      break;
    case "configuracion":
      loadConfig();
      break;
    case "channels":
      loadChannels();
      break;
  }
}

// DASHBOARD
function loadDashboard() {
  const filter = dom("dashboard-channel-filter");
  const channelId = filter ? filter.value : "";
  
  if (filter && filter.options.length <= 1) {
    loadChannelSelectors();
  }

  fetchJson(`${apiBase}/api/dashboard/summary${channelId ? `?channel_id=${channelId}` : ""}`)
    .then((data) => {
      renderSummary(data);
      renderCalendar(data.publication_calendar || []);
      renderChannelsOverview(data.channels_overview || []);
    })
    .catch((err) => console.error("Error dashboard:", err));
}

function renderSummary(data) {
  const content = dom("summary-content");
  if (!content) return;
  
  content.innerHTML = `
    <div class="summary-stats">
      <p><strong>Guiones:</strong> ${Object.entries(data.scripts_by_status || {}).map(([s, c]) => `${s}: ${c}`).join(", ")}</p>
      <p><strong>Videos:</strong> ${Object.entries(data.videos_by_status || {}).map(([s, c]) => `${s}: ${c}`).join(", ")}</p>
      <p><strong>Automatizaciones activas:</strong> ${data.active_automation_runs?.length || 0}</p>
    </div>
  `;
}

function renderCalendar(events) {
  const grid = dom("calendar-grid");
  const monthYear = dom("calendar-month-year");
  if (!grid) return;

  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth(); // 0-11
  const today = now.getDate();
  
  const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
  monthYear.innerText = `${monthNames[month]} ${year}`;

  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  let html = "";
  for (let i = 0; i < (firstDay === 0 ? 6 : firstDay - 1); i++) {
    html += `<div class="calendar-cell empty"></div>`;
  }

  for (let d = 1; d <= daysInMonth; d++) {
    const isToday = d === today;
    const isMarked = d <= today;
    // Usar parsing directo de la cadena ISO para evitar problemas de zona horaria
    const dayEvents = events.filter(e => {
      const dateStr = typeof e.date === 'string' ? e.date : e.date?.toISOString?.().split('T')[0] || '';
      const parts = dateStr.split('-');
      if (parts.length !== 3) return false;
      const eventYear = parseInt(parts[0]);
      const eventMonth = parseInt(parts[1]) - 1; // Mes en formato 0-11
      const eventDay = parseInt(parts[2]);
      return eventDay === d && eventMonth === month && eventYear === year;
    });

    html += `
      <div class="calendar-cell ${isToday ? 'today' : ''} ${isMarked ? 'marked' : ''}">
        <span class="calendar-day">${d}</span>
        ${dayEvents.map(e => `<div class="calendar-event" style="background:${e.color}">${e.title}</div>`).join("")}
      </div>
    `;
  }
  grid.innerHTML = html;
}

function renderChannelsOverview(channels) {
  const container = dom("channels-overview");
  if (!container) return;
  
  container.innerHTML = channels.map(c => `
    <div class="card channel-summary-card">
      <div class="flex-header">
        <img src="${apiBase}/api/channels/${c.channel_id}/thumbnail" class="channel-img" onerror="this.src='https://via.placeholder.com/50'">
        <div>
          <strong>${c.channel_name}</strong>
          <div class="text-small">${c.customUrl || ''}</div>
        </div>
      </div>
      <div class="mt-10">
        <span class="badge" style="background:${c.channel_color || '#eee'}">Canal</span>
        <p class="text-small">${c.description ? c.description.substring(0, 60) + '...' : 'Sin descripción'}</p>
      </div>
    </div>
  `).join("");
}

// CONTENIDO
function initContenido() {
  loadChannelSelectors();
  const filter = dom("content-channel-filter");
  filter.onchange = () => {
    if (filter.value) {
      dom("content-display").classList.remove("hidden");
      dom("content-placeholder").classList.add("hidden");
      loadChannelContent(filter.value);
    } else {
      dom("content-display").classList.add("hidden");
      dom("content-placeholder").classList.remove("hidden");
    }
  };

  document.querySelectorAll(".content-tab").forEach(tab => {
    tab.onclick = () => {
      document.querySelectorAll(".content-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      tab.classList.add("active");
      dom(`tab-${tab.dataset.tab}`).classList.add("active");
    };
  });
}

function loadChannelContent(channelId) {
  const stages = ["idea", "script", "developed", "video"];
  const containers = {
    idea: "ideas-list",
    script: "content-scripts-list",
    developed: "developed-list",
    video: "content-videos-list"
  };

  stages.forEach(stage => {
    fetchJson(`${apiBase}/api/content/${channelId}?stage=${stage}`)
      .then(items => {
        const list = dom(containers[stage]);
        if (!list) return;
        list.innerHTML = items.map(item => `
          <div class="item-row">
            <div>
              <strong>${item.title}</strong>
              <div class="text-small">${item.status} | ${new Date(item.created_at).toLocaleDateString()}</div>
            </div>
            <button onclick="openWorkflowModal(${item.id})" class="btn-outline btn-sm">Gestionar</button>
          </div>
        `).join("") || `<p class="text-muted">No hay contenido en esta etapa</p>`;
      });
  });
}

// FLUJO DE TRABAJO MANUAL
function openNewIdeaModal() {
  dom("idea-form").reset();
  dom("idea-modal").showModal();
}

dom("idea-form").onsubmit = (e) => {
  e.preventDefault();
  const channelId = dom("content-channel-filter").value;
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());
  data.channel_id = parseInt(channelId);
  data.stage = "idea";

  fetchJson(`${apiBase}/api/content/`, {
    method: "POST",
    body: JSON.stringify(data)
  }).then(() => {
    dom("idea-modal").close();
    loadChannelContent(channelId);
  });
};

let currentItem = null;

async function openWorkflowModal(itemId) {
  const channelId = dom("content-channel-filter").value;
  const items = await fetchJson(`${apiBase}/api/content/${channelId}`);
  currentItem = items.find(i => i.id === itemId);
  
  if (!currentItem) return;

  dom("workflow-item-id").value = itemId;
  dom("workflow-modal-title").innerText = `${currentItem.title} (${currentItem.stage})`;
  
  const fields = dom("workflow-fields");
  const genBtn = dom("btn-generate-script");
  fields.innerHTML = "";

  if (currentItem.stage === "idea") {
    fields.innerHTML = `
      <label>Título: <input type="text" name="title" value="${currentItem.title}"></label>
      <label>Notas de la Idea: <textarea name="idea_notes" rows="5">${currentItem.idea_notes || ""}</textarea></label>
    `;
    genBtn.classList.remove("hidden");
  } else if (currentItem.stage === "script") {
    fields.innerHTML = `
      <label>Título: <input type="text" name="title" value="${currentItem.title}"></label>
      <label>Contenido del Guión: <textarea name="script_content" rows="10">${currentItem.script_content || ""}</textarea></label>
      <label>Contenido del Artículo: <textarea name="article_content" rows="5">${currentItem.article_content || ""}</textarea></label>
    `;
    genBtn.classList.add("hidden");
  } else if (currentItem.stage === "developed") {
    fields.innerHTML = `
      <label>Título: <input type="text" name="title" value="${currentItem.title}"></label>
      <label>Datos de Desarrollo (JSON): <textarea name="developed_data" rows="5">${JSON.stringify(currentItem.developed_data || {}, null, 2)}</textarea></label>
    `;
    genBtn.classList.add("hidden");
  } else if (currentItem.stage === "video") {
    fields.innerHTML = `
      <label>Título: <input type="text" name="title" value="${currentItem.title}"></label>
      <p>Etapa final del video. Aquí se gestionaría la exportación.</p>
    `;
    genBtn.classList.add("hidden");
  }

  dom("workflow-modal").showModal();
}

dom("btn-generate-script").onclick = () => {
  if (!currentItem || currentItem.stage !== "idea") return;
  
  const btn = dom("btn-generate-script");
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';
  
  fetchJson(`${apiBase}/api/content/${currentItem.id}/generate-script`, { method: "POST" })
    .then(result => {
      alert("Guión generado exitosamente con IA");
      loadChannelContent(dom("content-channel-filter").value);
      dom("workflow-modal").close();
    })
    .catch(err => {
      alert("Error al generar guión: " + err.message);
    })
    .finally(() => {
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> Generar Guión con IA';
    });
}

dom("workflow-form").onsubmit = (e) => {
  e.preventDefault();
  const itemId = dom("workflow-item-id").value;
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());
  
  if (data.developed_data) {
    try { data.developed_data = JSON.parse(data.developed_data); } catch(e) {}
  }

  fetchJson(`${apiBase}/api/content/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify(data)
  }).then(() => {
    alert("Cambios guardados");
    loadChannelContent(dom("content-channel-filter").value);
  });
};

dom("btn-advance-stage").onclick = () => {
  if (!currentItem) return;
  const stages = ["idea", "script", "developed", "video"];
  const currentIndex = stages.indexOf(currentItem.stage);
  
  if (currentIndex < stages.length - 1) {
    const nextStage = stages[currentIndex + 1];
    if (confirm(`¿Avanzar a la etapa de ${nextStage}?`)) {
      fetchJson(`${apiBase}/api/content/${currentItem.id}`, {
        method: "PATCH",
        body: JSON.stringify({ stage: nextStage })
      }).then(() => {
        dom("workflow-modal").close();
        loadChannelContent(dom("content-channel-filter").value);
      });
    }
  } else {
    alert("Ya está en la etapa final");
  }
};

// ANÁLISIS
function initAnalisis() {
  loadChannelSelectors();
  const filter = dom("analytics-channel-filter");
  const checkBtn = dom("check-today-btn");
  const refreshBtn = dom("refresh-analytics");
  
  filter.onchange = () => {
    if (filter.value) {
      dom("analytics-display").classList.remove("hidden");
      dom("analytics-placeholder").classList.add("hidden");
      checkBtn.classList.remove("hidden");
      refreshBtn.classList.remove("hidden");
      loadChannelAnalytics(filter.value);
    } else {
      dom("analytics-display").classList.add("hidden");
      dom("analytics-placeholder").classList.remove("hidden");
      checkBtn.classList.add("hidden");
      refreshBtn.classList.add("hidden");
    }
  };

  checkBtn.onclick = () => {
    const id = filter.value;
    if (!id) return;
    
    checkBtn.disabled = true;
    checkBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Comprobando...';
    const statusEl = dom("today-data-status");
    statusEl.classList.remove("hidden");
    statusEl.className = "status-message info";
    statusEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Comprobando datos de hoy...';
    
    fetchJson(`${apiBase}/api/analytics/check-today/${id}`, { method: "POST" })
      .then(res => {
        if (res.has_today_data) {
          const fetched = res.fetched ? ' (recién descargados)' : ' (ya existían)';
          statusEl.className = "status-message success";
          statusEl.innerHTML = `<i class="fas fa-check-circle"></i> Datos de hoy encontrados${fetched} — Vistas: ${res.data?.view_count || 0}, Suscriptores: ${res.data?.subscriber_count || 0}, Videos: ${res.data?.video_count || 0}`;
          loadChannelAnalytics(id);
        } else {
          statusEl.className = "status-message error";
          statusEl.innerHTML = `<i class="fas fa-exclamation-circle"></i> No se pudieron obtener los datos: ${res.error || 'Error desconocido'}`;
        }
      })
      .catch(err => {
        statusEl.className = "status-message error";
        statusEl.innerHTML = `<i class="fas fa-exclamation-circle"></i> Error: ${err.message}`;
      })
      .finally(() => {
        checkBtn.disabled = false;
        checkBtn.innerHTML = '<i class="fas fa-check-circle"></i> Comprobar Datos de Hoy';
      });
  };

  refreshBtn.onclick = () => {
    const id = filter.value;
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Actualizando...';
    fetchJson(`${apiBase}/api/analytics/import/${id}`, { method: "POST" })
      .then(() => loadChannelAnalytics(id))
      .finally(() => {
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Actualizar Datos';
      });
  };
}

function loadChannelAnalytics(channelId) {
  // Mostrar estado de carga
  dom("views-chart").innerHTML = '<p class="chart-placeholder">Cargando gráfico...</p>';
  dom("subscribers-chart").innerHTML = '<p class="chart-placeholder">Cargando gráfico...</p>';
  dom("publications-history-list").innerHTML = 'Cargando...';
  dom("stat-subscribers").innerText = '...';
  dom("stat-views").innerText = '...';
  dom("stat-video-count").innerText = '...';

  // Cargar estadísticas diarias
  fetchJson(`${apiBase}/api/analytics/daily-stats/${channelId}`)
    .then(stats => {
      console.log("Analytics stats received:", stats);
      if (stats && stats.length > 0) {
        const last = stats[stats.length - 1];
        dom("stat-subscribers").innerText = last.subscriber_count.toLocaleString();
        dom("stat-views").innerText = last.view_count.toLocaleString();
        dom("stat-video-count").innerText = last.video_count.toLocaleString();
        
        // Render charts with real data
        renderViewsChart(stats);
        renderSubscribersChart(stats);
      } else {
        dom("views-chart").innerHTML = '<p class="chart-placeholder" style="color:#888;">No hay datos de rendimiento disponibles. Ejecuta "Comprobar Datos de Hoy" para obtener estadísticas.</p>';
        dom("subscribers-chart").innerHTML = '<p class="chart-placeholder" style="color:#888;">No hay datos de rendimiento disponibles. Ejecuta "Comprobar Datos de Hoy" para obtener estadísticas.</p>';
      }
    })
    .catch(err => {
      console.error("Error cargando analytics:", err);
      dom("views-chart").innerHTML = '<p class="chart-placeholder" style="color:#ef4444;">Error al cargar datos: ' + err.message + '</p>';
      dom("subscribers-chart").innerHTML = '<p class="chart-placeholder" style="color:#ef4444;">Error al cargar datos: ' + err.message + '</p>';
    });

  // Cargar historial de publicaciones
  fetchJson(`${apiBase}/api/analytics/publications-history/${channelId}`)
    .then(history => {
      console.log("Publications history received:", history);
      if (history && history.length > 0) {
        dom("publications-history-list").innerHTML = history.map(h => `
          <div class="item-row">
            <span>${h.date ? new Date(h.date).toLocaleDateString() : 'N/A'}</span>
            <strong>${h.title || 'Sin título'}</strong>
            <span class="badge">${h.content_type || h.platform || 'unknown'}</span>
          </div>
        `).join("");
      } else {
        dom("publications-history-list").innerHTML = '<p class="text-muted">Sin historial de publicaciones</p>';
      }
    })
    .catch(err => {
      console.error("Error cargando publicaciones:", err);
      dom("publications-history-list").innerHTML = '<p class="text-error">Error al cargar historial: ' + err.message + '</p>';
    });
}

function renderViewsChart(stats) {
  const sorted = stats.slice().sort((a, b) => new Date(a.stat_date) - new Date(b.stat_date));
  if (sorted.length === 0) return;

  // Compute differences per point. First point shows the absolute value.
  let html = '<div class="evolution-chart">';
  html += '<div class="evolution-points">';
  sorted.forEach((s, i) => {
    const dateShort = s.stat_date ? s.stat_date.slice(5) : 'N/A'; // MM-DD
    const dateFull = s.stat_date || 'N/A';
    let valueLabel;
    if (i === 0) {
      valueLabel = s.view_count.toLocaleString();
    } else {
      const diff = s.view_count - sorted[i - 1].view_count;
      valueLabel = (diff >= 0 ? '+' : '') + diff.toLocaleString();
    }
    const cssClass = i === 0 ? 'point-first' : (diff >= 0 ? 'point-up' : 'point-down');
    const displayDiff = i === 0 ? s.view_count : (s.view_count - sorted[i - 1].view_count);
    const maxView = Math.max(...sorted.map(x => x.view_count), 1);
    const heightPct = Math.max(5, (displayDiff >= 0 ? displayDiff : 0) / maxView * 80 + 10);
    html += `<div class="evolution-point ${cssClass}" title="${dateFull}: ${s.view_count} vistas (total)">
      <span class="point-value">${valueLabel}</span>
      <span class="point-date">${dateShort}</span>
    </div>`;
  });
  html += '</div>';

  // Bars row
  html += '<div class="evolution-bars">';
  sorted.forEach((s, i) => {
    const dateShort = s.stat_date ? s.stat_date.slice(5) : 'N/A';
    const maxView = Math.max(...sorted.map(x => x.view_count), 1);
    const barH = Math.max(4, s.view_count / maxView * 100);
    html += `<div class="bar-item" title="${s.stat_date}: ${s.view_count} vistas">
      <div class="bar-fill" style="height:${barH}%"></div>
      <span class="bar-label">${dateShort}</span>
    </div>`;
  });
  html += '</div></div>';

  dom("views-chart").innerHTML = html;
}

function renderSubscribersChart(stats) {
  const sorted = stats.slice().sort((a, b) => new Date(a.stat_date) - new Date(b.stat_date));
  if (sorted.length === 0) return;

  let html = '<div class="evolution-chart">';
  html += '<div class="evolution-points">';
  sorted.forEach((s, i) => {
    const dateShort = s.stat_date ? s.stat_date.slice(5) : 'N/A';
    const dateFull = s.stat_date || 'N/A';
    let valueLabel;
    if (i === 0) {
      valueLabel = s.subscriber_count.toLocaleString();
    } else {
      const diff = s.subscriber_count - sorted[i - 1].subscriber_count;
      valueLabel = (diff >= 0 ? '+' : '') + diff.toLocaleString();
    }
    const cssClass = i === 0 ? 'point-first' : (diff >= 0 ? 'point-up' : 'point-down');
    html += `<div class="evolution-point ${cssClass}" title="${dateFull}: ${s.subscriber_count} suscriptores (total)">
      <span class="point-value">${valueLabel}</span>
      <span class="point-date">${dateShort}</span>
    </div>`;
  });
  html += '</div>';

  html += '<div class="evolution-bars">';
  sorted.forEach((s, i) => {
    const dateShort = s.stat_date ? s.stat_date.slice(5) : 'N/A';
    const maxSub = Math.max(...sorted.map(x => x.subscriber_count), 1);
    const barH = Math.max(4, s.subscriber_count / maxSub * 100);
    html += `<div class="bar-item" title="${s.stat_date}: ${s.subscriber_count} suscriptores">
      <div class="bar-fill" style="height:${barH}%"></div>
      <span class="bar-label">${dateShort}</span>
    </div>`;
  });
  html += '</div></div>';

  dom("subscribers-chart").innerHTML = html;
}

// CONFIGURACIÓN
let youtubeKeyVisible = false;

function toggleYoutubeKeyVisibility() {
  const input = dom("youtube_api_key");
  const icon = document.querySelector("#btn-toggle-youtube-key i");
  youtubeKeyVisible = !youtubeKeyVisible;
  
  if (youtubeKeyVisible) {
    input.type = "text";
    icon.className = "fas fa-eye-slash";
  } else {
    input.type = "password";
    icon.className = "fas fa-eye";
  }
}

function loadYoutubeKeyStatus() {
  fetchJson(`${apiBase}/api/config/youtube-key`)
    .then(data => {
      const status = dom("youtube-key-status");
      const input = dom("youtube_api_key");
      
      if (data.configured) {
        status.innerHTML = `<span class="badge badge-success" style="font-size: 10px;">✓ Configurada</span>`;
        // Mostrar enmascarado: primeros 2 y últimos 2 caracteres
        const realKey = data.masked_key;
        input.value = realKey;
      } else {
        status.innerHTML = `<span class="badge badge-secondary" style="font-size: 10px;">No configurada</span>`;
        input.value = "";
      }
    })
    .catch(err => console.error("Error cargando YouTube API Key:", err));
}

function saveYoutubeKey() {
  const input = dom("youtube_api_key");
  const key = input.value.trim();
  const status = dom("youtube-key-status");
  
  if (!key) {
    status.innerHTML = `<span class="badge badge-secondary" style="font-size: 10px;">No configurada</span>`;
    return;
  }
  
  fetchJson(`${apiBase}/api/config/youtube-key`, {
    method: "POST",
    body: JSON.stringify({ api_key: key })
  })
    .then(data => {
      status.innerHTML = `<span class="badge badge-success" style="font-size: 10px;">✓ Configurada</span>`;
      alert("YouTube API Key guardada correctamente");
    })
    .catch(err => alert("Error al guardar: " + err.message));
}

function loadConfig() {
  // Cargar config general
  fetchJson(`${apiBase}/api/config`)
    .then(configs => {
      configs.forEach(c => {
        const input = dom(c.key);
        if (input && c.key !== "youtube_api_key") input.value = c.value;
      });
    })
    .catch(err => console.error("Error cargando config:", err))
    .finally(() => {
      // Cargar estado de YouTube API Key
      loadYoutubeKeyStatus();
    });

  dom("config-form").onsubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const promises = [];
    
    for (let [key, value] of formData.entries()) {
      if (key !== "youtube_api_key") {
        promises.push(fetchJson(`${apiBase}/api/config`, {
          method: "POST",
          body: JSON.stringify({ key, value })
        }));
      }
    }

    Promise.all(promises)
      .then(() => alert("Configuración guardada"))
      .catch(err => alert("Error al guardar: " + err.message));
  };

  // Tabs de configuración
  document.querySelectorAll(".config-tab").forEach(tab => {
    tab.onclick = () => {
      document.querySelectorAll(".config-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".config-tab-content").forEach(c => c.classList.add("hidden"));
      tab.classList.add("active");
      const tabName = tab.dataset.configTab;
      dom(`config-${tabName}`).classList.remove("hidden");
      if (tabName === "prompts") {
        loadCategoryFilter();
        loadPromptsList();
      }
    };
  });
}

// ===================== BIBLIOTECA DE PROMPTS =====================

// Cargar lista de prompts en la tabla de configuración
function loadPromptsList() {
  const categoryFilter = dom("prompt-category-filter");
  const searchInput = dom("prompt-search");
  const listContainer = dom("prompts-list");
  
  function fetchAndRender() {
    const category = categoryFilter.value;
    let url = `${apiBase}/api/prompts`;
    if (category) {
      url += `?category=${encodeURIComponent(category)}`;
    }
    
    fetchJson(url)
      .then(prompts => {
        let filtered = prompts;
        if (searchInput && searchInput.value) {
          const search = searchInput.value.toLowerCase();
          filtered = prompts.filter(p => 
            p.title.toLowerCase().includes(search) ||
            (p.description && p.description.toLowerCase().includes(search)) ||
            p.content.toLowerCase().includes(search) ||
            p.category.toLowerCase().includes(search)
          );
        }
        
        if (!listContainer) return;
        
        if (filtered.length === 0) {
          listContainer.innerHTML = `<p style="text-align:center; padding: 2rem; color: #888;">No hay prompts${category ? " en esta categoría" : ""}</p>`;
          return;
        }
        
        listContainer.innerHTML = filtered.map(p => {
          const cat = p.category || "otro";
          const safeId = p.id;
          const safeCategory = p.category || "otro";
          const safeTitle = (p.title || "").replace(/'/g, "\\'").replace(/"/g, '\\"');
          return `
          <div class="prompt-card card" data-category="${cat}" style="margin-bottom:1rem;">
            <div class="prompt-header">
              <h4>${p.title}</h4>
              <span class="badge" style="background:#6366f1;">${cat}</span>
            </div>
            <p class="text-small" style="margin: 0.5rem 0;">${p.description || "Sin descripción"}</p>
            <div class="prompt-meta" style="display:flex; gap:1rem; font-size:12px; margin: 0.5rem 0;">
              <span><i class="fas fa-star" style="color:#f59e0b;"></i> ${parseFloat(p.rating || 0).toFixed(1)}/5</span>
              <span><i class="fas fa-check-circle" style="color:#10b981;"></i> ${p.usage_count || 0} usos</span>
              <span><i class="fas fa-code" style="color:#8b5cf6;"></i> v${p.version || 1}</span>
            </div>
            <div class="prompt-variables" style="font-size:12px;">
              ${p.variables && p.variables.length > 0 
                ? `<strong>Variables:</strong> ${p.variables.join(", ")}` 
                : "Sin variables"}
            </div>
            <div class="prompt-actions" style="margin-top:0.75rem; display:flex; gap:0.5rem; flex-wrap:wrap;">
              <button class="btn-sm btn-view-prompt" onclick="openPromptDetail(${safeId})"><i class="fas fa-eye"></i> Ver Prompt</button>
              <button class="btn-outline btn-sm" onclick="editPrompt(${safeId}, '${safeCategory}', '${safeTitle}')"><i class="fas fa-edit"></i> Editar</button>
              <button class="btn-outline btn-sm" style="color:#ef4444;" onclick="deletePromptConfirm(${safeId}, '${safeCategory}', '${safeTitle}')"><i class="fas fa-trash"></i> Eliminar</button>
            </div>
          </div>
        `}).join("");
      })
      .catch(err => {
        if (listContainer) {
          listContainer.innerHTML = `<p class="text-error">Error al cargar prompts: ${err.message}</p>`;
        }
      });
  }
  
  if (categoryFilter) categoryFilter.onchange = fetchAndRender;
  if (searchInput) searchInput.onkeyup = fetchAndRender;
  
  fetchAndRender();
}

// Cargar categorías en el filtro
function loadCategoryFilter() {
  const select = dom("prompt-category-filter");
  if (!select) return;
  
  fetchJson(`${apiBase}/api/prompts/categories`)
    .then(data => {
      const categories = data.categories || [];
      select.innerHTML = `<option value="">Todas las categorías</option>` + 
        categories.map(c => `<option value="${c.name}">${c.name.replace(/_/g, " ")}</option>`).join("");
    })
    .catch(err => console.error("Error cargando categorías:", err));
}

// Abrir modal para crear prompt
function openPromptCreateModal() {
  const modal = dom("prompt-create-modal");
  if (!modal) return;
  
  // Cargar categorías en el select
  loadCategorySelect();
  
  // Resetear formulario
  const form = dom("prompt-form");
  if (form) {
    form.reset();
    dom("prompt-title-count").innerText = "0/100";
    dom("prompt-description-count").innerText = "0/500";
    dom("prompt-content-count").innerText = "0/5000";
    dom("detected-variables").innerHTML = "";
  }
  
  modal.showModal();
}

// Cargar categorías en el select del formulario
function loadCategorySelect() {
  fetchJson(`${apiBase}/api/prompts/categories`)
    .then(data => {
      const categories = data.categories || [];
      const select = dom("prompt-category");
      if (!select) return;
      
      select.innerHTML = `<option value="">Selecciona una categoría</option>` + 
        categories.map(c => `<option value="${c.name}">${c.name.replace(/_/g, " ")}</option>`).join("");
      
      // Añadir opción para crear nueva categoría
      select.innerHTML += `<option value="__new__">+ Crear nueva categoría...</option>`;
    })
    .catch(err => {
      const select = dom("prompt-category");
      if (select) {
        select.innerHTML = `<option value="otro">otro</option><option value="__new__">+ Crear nueva categoría...</option>`;
      }
    });
}

// Manejar creación/edición de prompt
function handlePromptCreate(event) {
  event.preventDefault();
  
  const form = dom("prompt-form");
  const editId = form.dataset.editId;
  
  const title = dom("prompt-title").value.trim();
  const category = dom("prompt-category").value;
  const description = dom("prompt-description").value.trim();
  const content = dom("prompt-content").value.trim();
  
  if (!title) return alert("El título es obligatorio");
  if (!content) return alert("El contenido del prompt es obligatorio");
  
  // Si estamos editando
  if (editId) {
    // Si el usuario quiere cambiar a una nueva categoría
    if (category === "__new__") {
      const newCat = prompt("Introduce el nombre para la nueva categoría:");
      if (!newCat || !newCat.trim()) return;
      
      updateCategoryAsync(newCat.trim(), editId, title, content, description);
      return;
    }
    
    if (!category) return alert("Debes seleccionar una categoría");
    
    const data = {
      title: title,
      content: content,
      category: category,
      description: description || null
    };
    
    fetchJson(`${apiBase}/api/prompts/by-id/${editId}`, {
      method: "PATCH",
      body: JSON.stringify(data)
    })
      .then(() => {
        alert("Prompt actualizado exitosamente");
        dom("prompt-create-modal").close();
        loadPromptsList();
        loadCategoryFilter();
      })
      .catch(err => alert("Error al actualizar prompt: " + err.message));
    return;
  }
  
  // Si el usuario quiere crear una nueva categoría
  if (category === "__new__") {
    const newCat = prompt("Introduce el nombre para la nueva categoría:");
    if (!newCat || !newCat.trim()) return;
    
    createCategoryAsync(newCat.trim(), title, content, description);
    return;
  }
  
  if (!category) return alert("Debes seleccionar una categoría");
  
  const data = {
    title: title,
    content: content,
    category: category,
    description: description || null,
    prompt_type: category
  };
  
  fetchJson(`${apiBase}/api/prompts/`, {
    method: "POST",
    body: JSON.stringify(data)
  })
    .then(() => {
      alert("Prompt creado exitosamente");
      dom("prompt-create-modal").close();
      loadPromptsList();
      loadCategoryFilter();
    })
    .catch(err => alert("Error al crear prompt: " + err.message));
}

// Actualizar categoría asíncronamente
function updateCategoryAsync(catName, promptId, title, content, description) {
  // Primero crear la categoría
  fetchJson(`${apiBase}/api/prompts/categories`, {
    method: "POST",
    body: JSON.stringify({ name: catName })
  })
    .then(() => {
      // Ahora actualizar el prompt con la nueva categoría
      const data = {
        title: title,
        content: content,
        category: catName,
        description: description || null
      };
      
      return fetchJson(`${apiBase}/api/prompts/by-id/${promptId}`, {
        method: "PATCH",
        body: JSON.stringify(data)
      });
    })
    .then(() => {
      alert("Prompt actualizado exitosamente");
      dom("prompt-create-modal").close();
      loadPromptsList();
      loadCategoryFilter();
    })
    .catch(err => alert("Error: " + err.message));
}

// Crear categoría asíncronamente
function createCategoryAsync(catName, title, content, description) {
  fetchJson(`${apiBase}/api/prompts/categories`, {
    method: "POST",
    body: JSON.stringify({ name: catName })
  })
    .then(() => {
      // Ahora crear el prompt con la nueva categoría
      const data = {
        title: title,
        content: content,
        category: catName,
        description: description || null,
        prompt_type: catName
      };
      
      return fetchJson(`${apiBase}/api/prompts/`, {
        method: "POST",
        body: JSON.stringify(data)
      });
    })
    .then(() => {
      alert("Prompt creado exitosamente");
      dom("prompt-create-modal").close();
      loadPromptsList();
      loadCategoryFilter();
    })
    .catch(err => alert("Error: " + err.message));
}

// Actualizar contador de caracteres
function updateCharCounter(inputId, counterId, maxLength) {
  const input = dom(inputId);
  const counter = dom(counterId);
  if (!input || !counter) return;
  
  const currentLength = input.value.length;
  counter.innerText = `${currentLength}/${maxLength}`;
  
  // Cambiar color si se acerca al límite
  if (currentLength > maxLength * 0.9) {
    counter.style.color = "#ef4444";
  } else if (currentLength > maxLength * 0.7) {
    counter.style.color = "#f59e0b";
  } else {
    counter.style.color = "";
  }
}

// Actualizar variables detectadas
function updateDetectedVariables() {
  const content = dom("prompt-content").value;
  const variables = content.match(/\{\{(\w+)\}\}/g) || [];
  const unique = [...new Set(variables.map(v => v.slice(2, -2)))];
  
  const container = dom("detected-variables");
  if (!container) return;
  
  if (unique.length > 0) {
    container.innerHTML = `<i class="fas fa-code"></i> <strong>Variables detectadas:</strong> ${unique.map(v => `<code>${v}</code>`).join(", ")}`;
  } else {
    container.innerHTML = "No se detectaron variables. Usa el formato <code>{{variable}}</code> en el contenido.";
  }
}

// Mostrar modal de gestión de categorías
function showManageCategories() {
  const modal = dom("category-manage-modal");
  if (!modal) return;
  
  loadCategoriesList();
  modal.showModal();
}

// Cargar lista de categorías
function loadCategoriesList() {
  fetchJson(`${apiBase}/api/prompts/categories`)
    .then(data => {
      const categories = data.categories || [];
      const container = dom("categories-list");
      if (!container) return;
      
      if (categories.length === 0) {
        container.innerHTML = "<p>No hay categorías creadas</p>";
        return;
      }
      
      container.innerHTML = categories.map(c => `
        <div class="flex-header" style="padding:0.5rem 0; border-bottom:1px solid #eee;">
          <div>
            <strong>${c.name.replace(/_/g, " ")}</strong>
            <span class="text-small" style="color:#888;"> (${c.prompt_count || 0} prompts)</span>
          </div>
          <button class="btn-danger btn-sm" onclick="deleteCategoryConfirm('${c.name}', '${c.name.replace(/_/g, " ")}')" style="padding:0.25rem 0.5rem;">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      `).join("");
    })
    .catch(err => {
      const container = dom("categories-list");
      if (container) container.innerHTML = `<p class="text-error">Error: ${err.message}</p>`;
    });
}

// Crear nueva categoría
function createNewCategory() {
  const input = dom("new-category-name");
  if (!input) return;
  
  const name = input.value.trim();
  if (!name) return alert("Introduce un nombre para la categoría");
  
  fetchJson(`${apiBase}/api/prompts/categories`, {
    method: "POST",
    body: JSON.stringify({ name: name })
  })
    .then(() => {
      alert("Categoría creada exitosamente");
      input.value = "";
      loadCategoriesList();
      loadCategoryFilter();
    })
    .catch(err => alert("Error al crear categoría: " + err.message));
}

// ============================================
// OVERLAY BIBLIOTECA DE PROMPTS
// ============================================

// Abrir overlay de prompts
function openPromptsOverlay() {
  const overlay = dom("prompts-overlay");
  if (!overlay) return;
  
  overlay.classList.remove("hidden");
  
  // Cargar datos iniciales
  loadOverlayPromptsList();
  loadOverlayCategoryFilter();
  loadOverlayCategoriesList();
}

// Cerrar overlay de prompts
function closePromptsOverlay() {
  const overlay = dom("prompts-overlay");
  if (!overlay) return;
  
  overlay.classList.add("hidden");
  
  // Volver a la vista de lista
  showOverlayListView();
}

// Cargar lista de prompts en el overlay
function loadOverlayPromptsList() {
  const search = dom("overlay-prompt-search")?.value || "";
  const category = dom("overlay-prompt-category-filter")?.value || "";
  
  let url = `${apiBase}/api/prompts?page_size=100`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  if (category) url += `&category=${encodeURIComponent(category)}`;
  
  fetchJson(url)
    .then(data => {
      const prompts = data.prompts || data || [];
      const container = dom("overlay-prompts-list");
      if (!container) return;
      
      if (prompts.length === 0) {
        container.innerHTML = "<p class='text-muted'>No se encontraron prompts</p>";
        return;
      }
      
      container.innerHTML = prompts.map((p, idx) => `
        <div class="prompt-list-item" onclick="showOverlayPromptDetail('${p.id || idx}')">
          <div class="prompt-item-title">${p.title || "Sin título"}</div>
          <div class="prompt-item-category badge">${p.category || "Sin categoría"}</div>
          ${p.description ? `<div class="prompt-item-desc">${p.description}</div>` : ''}
        </div>
      `).join("");
    })
    .catch(err => {
      const container = dom("overlay-prompts-list");
      if (container) container.innerHTML = `<p class="text-error">Error: ${err.message}</p>`;
    });
}

// Cargar filtro de categorías en el overlay
function loadOverlayCategoryFilter() {
  fetchJson(`${apiBase}/api/prompts/categories`)
    .then(data => {
      const categories = data.categories || [];
      const select = dom("overlay-prompt-category-filter");
      const categorySelect = dom("overlay-prompt-category");
      
      if (select) {
        select.innerHTML = '<option value="">Todas las categorías</option>' +
          categories.map(c => `<option value="${c.name}">${c.name.replace(/_/g, " ")}</option>`).join("");
      }
      
      if (categorySelect) {
        categorySelect.innerHTML = '<option value="">Selecciona una categoría</option>' +
          categories.map(c => `<option value="${c.name}">${c.name.replace(/_/g, " ")}</option>`).join("");
      }
    })
    .catch(err => console.error("Error cargando categorías:", err));
}

// Cambiar vistas del overlay
function showOverlayListView() {
  hideAllOverlayViews();
  dom("overlay-view-list")?.classList.add("active");
}

function showOverlayPromptCreate() {
  hideAllOverlayViews();
  dom("overlay-view-edit")?.classList.add("active");
  dom("overlay-edit-title").innerText = "Nuevo Prompt";
  dom("overlay-edit-id").value = "";
  dom("overlay-prompt-form").reset();
  dom("overlay-prompt-title-count").innerText = "0/100";
  dom("overlay-prompt-description-count").innerText = "0/500";
  dom("overlay-prompt-content-count").innerText = "0/5000";
  dom("overlay-detected-variables").innerHTML = "";
}

function showOverlayEditFromDetail() {
  const promptId = dom("overlay-detail-content")?.dataset?.promptId;
  if (!promptId) return;
  
  fetchJson(`${apiBase}/api/prompts/${promptId}`)
    .then(prompt => {
      hideAllOverlayViews();
      dom("overlay-view-edit")?.classList.add("active");
      dom("overlay-edit-title").innerText = "Editar Prompt";
      dom("overlay-edit-id").value = prompt.id;
      dom("overlay-prompt-title").value = prompt.title || "";
      dom("overlay-prompt-category").value = prompt.category || "";
      dom("overlay-prompt-description").value = prompt.description || "";
      dom("overlay-prompt-content").value = prompt.content || "";
      
      updateCharCounter('overlay-prompt-title', 'overlay-prompt-title-count', 100);
      updateCharCounter('overlay-prompt-description', 'overlay-prompt-description-count', 500);
      updateCharCounter('overlay-prompt-content', 'overlay-prompt-content-count', 5000);
      updateDetectedVariables();
    })
    .catch(err => alert("Error al cargar prompt: " + err.message));
}

function showOverlayPromptDetail(promptId) {
  fetchJson(`${apiBase}/api/prompts/${promptId}`)
    .then(prompt => {
      hideAllOverlayViews();
      dom("overlay-view-detail")?.classList.add("active");
      dom("overlay-detail-title").innerText = prompt.title || "Sin título";
      
      const variablesHtml = prompt.variables && prompt.variables.length > 0
        ? prompt.variables.map(v => `<code style="background:#f3f4f6; padding:2px 6px; border-radius:4px;">${v}</code>`).join(", ")
        : "Ninguna";
      
      const detailContent = dom("overlay-detail-content");
      detailContent.innerHTML = `
        <div class="detail-section">
          <div class="detail-label">Categoría</div>
          <div class="detail-value"><span class="badge">${prompt.category}</span></div>
        </div>
        <div class="detail-section">
          <div class="detail-label">Descripción</div>
          <div class="detail-value">${prompt.description || "N/A"}</div>
        </div>
        <div class="detail-section">
          <div class="detail-label">Versión</div>
          <div class="detail-value">${prompt.version || 1}</div>
        </div>
        <div class="detail-section">
          <div class="detail-label">Puntuación</div>
          <div class="detail-value">${parseFloat(prompt.rating || 0).toFixed(1)}/5</div>
        </div>
        <div class="detail-section">
          <div class="detail-label">Usos</div>
          <div class="detail-value">${prompt.usage_count || 0}</div>
        </div>
        <div class="detail-section">
          <div class="detail-label">Variables</div>
          <div class="detail-value">${variablesHtml}</div>
        </div>
        <div class="detail-section">
          <div class="detail-label">Contenido</div>
          <div class="prompt-content-box">
            <pre>${prompt.content}</pre>
          </div>
        </div>
      `;
      detailContent.dataset.promptId = prompt.id;
    })
    .catch(err => alert("Error al cargar prompt: " + err.message));
}

function showOverlayCategories() {
  hideAllOverlayViews();
  dom("overlay-view-categories")?.classList.add("active");
  loadOverlayCategoriesList();
}

function hideAllOverlayViews() {
  document.querySelectorAll(".overlay-view").forEach(v => v.classList.remove("active"));
}

// Crear prompt desde el overlay
function handleOverlayPromptCreate(event) {
  event.preventDefault();
  
  const editId = dom("overlay-edit-id").value;
  const title = dom("overlay-prompt-title").value.trim();
  const category = dom("overlay-prompt-category").value;
  const description = dom("overlay-prompt-description").value.trim();
  const content = dom("overlay-prompt-content").value.trim();
  
  if (!title) return alert("El título es obligatorio");
  if (!content) return alert("El contenido del prompt es obligatorio");
  if (!category) return alert("Debes seleccionar una categoría");
  
  const data = {
    title: title,
    content: content,
    category: category,
    description: description || null
  };
  
  if (editId) {
    // Actualizar prompt existente
    fetchJson(`${apiBase}/api/prompts/by-id/${editId}`, {
      method: "PATCH",
      body: JSON.stringify(data)
    })
      .then(() => {
        alert("Prompt actualizado exitosamente");
        closePromptsOverlay();
        loadPromptsList();
        loadCategoryFilter();
      })
      .catch(err => alert("Error al actualizar prompt: " + err.message));
  } else {
    // Crear nuevo prompt
    fetchJson(`${apiBase}/api/prompts`, {
      method: "POST",
      body: JSON.stringify(data)
    })
      .then(() => {
        alert("Prompt creado exitosamente");
        closePromptsOverlay();
        loadPromptsList();
        loadCategoryFilter();
      })
      .catch(err => alert("Error al crear prompt: " + err.message));
  }
}

// Eliminar prompt desde el overlay
function deleteOverlayPrompt() {
  const detailContent = dom("overlay-detail-content");
  const promptId = detailContent?.dataset?.promptId;
  
  if (!promptId) return alert("No hay prompt seleccionado");
  
  if (confirm("¿Estás seguro de eliminar este prompt?")) {
    fetchJson(`${apiBase}/api/prompts/by-id/${promptId}`, {
      method: "DELETE"
    })
      .then(() => {
        alert("Prompt eliminado");
        showOverlayListView();
        loadOverlayPromptsList();
        loadCategoryFilter();
      })
      .catch(err => alert("Error: " + err.message));
  }
}

// Copiar prompt desde el overlay
function copyOverlayPrompt() {
  const detailContent = dom("overlay-detail-content");
  const content = detailContent?.querySelector("pre")?.innerText;
  const title = dom("overlay-detail-title")?.innerText;
  
  if (!content) return alert("No hay contenido para copiar");
  
  navigator.clipboard.writeText(content)
    .then(() => alert("Contenido copiado al portapapeles"))
    .catch(() => alert("Error al copiar"));
}

// Gestionar categorías desde el overlay
function createOverlayCategory() {
  const input = dom("overlay-new-category-name");
  if (!input) return;
  
  const name = input.value.trim();
  if (!name) return alert("Introduce un nombre para la categoría");
  
  fetchJson(`${apiBase}/api/prompts/categories`, {
    method: "POST",
    body: JSON.stringify({ name: name })
  })
    .then(() => {
      alert("Categoría creada exitosamente");
      input.value = "";
      loadOverlayCategoriesList();
      loadOverlayCategoryFilter();
    })
    .catch(err => alert("Error al crear categoría: " + err.message));
}

function loadOverlayCategoriesList() {
  fetchJson(`${apiBase}/api/prompts/categories`)
    .then(data => {
      const categories = data.categories || [];
      const container = dom("overlay-categories-list");
      if (!container) return;
      
      if (categories.length === 0) {
        container.innerHTML = "<p class='text-muted'>No hay categorías creadas</p>";
        return;
      }
      
      container.innerHTML = categories.map(c => `
        <div class="category-item">
          <div class="category-name">
            <i class="fas fa-folder"></i>
            ${c.name.replace(/_/g, " ")}
            <span class="category-count">(${c.prompt_count || 0} prompts)</span>
          </div>
          <div class="category-actions">
            <button class="btn-danger btn-sm" onclick="deleteOverlayCategory('${c.name}')">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      `).join("");
    })
    .catch(err => {
      const container = dom("overlay-categories-list");
      if (container) container.innerHTML = `<p class="text-error">Error: ${err.message}</p>`;
    });
}

function deleteOverlayCategory(name) {
  if (confirm(`¿Estás seguro de eliminar la categoría "${name}" y todos sus prompts?`)) {
    fetchJson(`${apiBase}/api/prompts/categories`, {
      method: "DELETE",
      body: JSON.stringify({ name: name })
    })
      .then(() => {
        alert("Categoría eliminada");
        loadOverlayCategoriesList();
        loadOverlayCategoryFilter();
        loadOverlayPromptsList();
      })
      .catch(err => alert("Error: " + err.message));
  }
}

// ============================================
// FIN OVERLAY BIBLIOTECA DE PROMPTS
// ============================================

// Confirmar eliminación de categoría
function deleteCategoryConfirm(id, name) {
  if (confirm(`¿Estás seguro de eliminar la categoría "${name}" y todos sus prompts?`)) {
    fetchJson(`${apiBase}/api/prompts/categories`, {
      method: "DELETE",
      body: JSON.stringify({ name: id })
    })
      .then(() => {
        alert("Categoría eliminada");
        loadCategoriesList();
        loadCategoryFilter();
        loadPromptsList();
      })
      .catch(err => alert("Error: " + err.message));
  }
}

// Abrir detalle de prompt
function openPromptDetail(promptId) {
  fetchJson(`${apiBase}/api/prompts/${promptId}`)
    .then(prompt => {
      dom("prompt-detail-title").innerText = prompt.title;
      
      const variablesHtml = prompt.variables && prompt.variables.length > 0 
        ? prompt.variables.map(v => `<code style="background:#f3f4f6; padding:2px 6px; border-radius:4px;">${v}</code>`).join(", ")
        : "Ninguna";
      
      dom("prompt-detail-content").innerHTML = `
        <div class="prompt-detail" style="padding:1rem;">
          <p><strong>Categoría:</strong> <span class="badge">${prompt.category}</span></p>
          <p><strong>Descripción:</strong> ${prompt.description || "N/A"}</p>
          <p><strong>Versión:</strong> v${prompt.version || 1}</p>
          <p><strong>Puntuación:</strong> ${parseFloat(prompt.rating || 0).toFixed(1)}/5</p>
          <p><strong>Usos:</strong> ${prompt.usage_count || 0}</p>
          <p><strong>Variables:</strong> ${variablesHtml}</p>
          <div class="prompt-content-box" style="background:#f9fafb; padding:1rem; border-radius:8px; margin:1rem 0;">
            <strong>Contenido:</strong>
            <pre style="white-space:pre-wrap; font-family:monospace; background:#fff; padding:0.5rem; border-radius:4px;">${prompt.content}</pre>
          </div>
        </div>
      `;
      
      // Configurar botones de acción
      const editBtn = dom("btn-edit-prompt");
      const deleteBtn = dom("btn-delete-prompt");
      
      if (editBtn) {
        editBtn.onclick = () => {
          dom("prompt-detail-modal").close();
          editPrompt(prompt.id, prompt.category, prompt.title);
        };
      }
      
      if (deleteBtn) {
        deleteBtn.onclick = () => {
          deletePromptConfirm(prompt.id, prompt.category, prompt.title);
        };
      }
      
      dom("prompt-detail-modal").showModal();
    })
    .catch(err => alert("Error al cargar prompt: " + err.message));
}

// Editar prompt
function editPrompt(promptId, category, title) {
  fetchJson(`${apiBase}/api/prompts/${promptId}`)
    .then(prompt => {
      // Abrir modal de creación y rellenar datos
      openPromptCreateModal();
      
      // Rellenar formulario
      dom("prompt-title").value = prompt.title || "";
      dom("prompt-category").value = prompt.category || "";
      dom("prompt-description").value = prompt.description || "";
      dom("prompt-content").value = prompt.content || "";
      
      // Actualizar contadores
      updateCharCounter("prompt-title", "prompt-title-count", 100);
      updateCharCounter("prompt-description", "prompt-description-count", 500);
      updateCharCounter("prompt-content", "prompt-content-count", 5000);
      updateDetectedVariables();
      
      // Guardar ID para actualización
      dom("prompt-form").dataset.editId = promptId;
      dom("prompt-form").dataset.editCategory = category;
      
      // Cambiar texto del botón
      const submitBtn = dom("prompt-form").querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.innerText = "Guardar Cambios";
    })
    .catch(err => alert("Error al cargar prompt: " + err.message));
}

// Guardar cambios de prompt (actualización)
function handlePromptUpdate() {
  const form = dom("prompt-form");
  if (!form || !form.dataset.editId) return;
  
  const promptId = form.dataset.editId;
  const title = dom("prompt-title").value.trim();
  const category = dom("prompt-category").value;
  const description = dom("prompt-description").value.trim();
  const content = dom("prompt-content").value.trim();
  
  if (!title) return alert("El título es obligatorio");
  if (!content) return alert("El contenido del prompt es obligatorio");
  if (!category) return alert("Debes seleccionar una categoría");
  
  const data = {
    title: title,
    content: content,
    category: category,
    description: description || null
  };
  
  fetchJson(`${apiBase}/api/prompts/by-id/${promptId}`, {
    method: "PATCH",
    body: JSON.stringify(data)
  })
    .then(() => {
      alert("Prompt actualizado exitosamente");
      dom("prompt-create-modal").close();
      loadPromptsList();
      loadCategoryFilter();
    })
    .catch(err => alert("Error al actualizar prompt: " + err.message));
}

// Confirmar eliminación de prompt (usando endpoint por ID)
function deletePromptConfirm(promptId, category, title) {
  if (confirm(`¿Estás seguro de eliminar el prompt "${title}"?`)) {
    fetchJson(`${apiBase}/api/prompts/by-id/${promptId}`, {
      method: "DELETE"
    })
      .then(() => {
        alert("Prompt eliminado");
        dom("prompt-detail-modal").close();
        loadPromptsList();
        loadCategoryFilter();
      })
      .catch(err => alert("Error: " + err.message));
  }
}

// Cerrar modal de creación
function closePromptCreateModal() {
  const modal = dom("prompt-create-modal");
  if (modal) modal.close();
  
  // Resetear formulario
  const form = dom("prompt-form");
  if (form) {
    form.reset();
    delete form.dataset.editId;
    delete form.dataset.editCategory;
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.innerText = "Crear Prompt";
    dom("prompt-title-count").innerText = "0/100";
    dom("prompt-description-count").innerText = "0/500";
    dom("prompt-content-count").innerText = "0/5000";
    dom("detected-variables").innerHTML = "";
  }
}

// ===================== FIN BIBLIOTECA DE PROMPTS =====================

// CANALES Y HERRAMIENTAS
let currentChannelId = null;

function loadChannels() {
  fetchJson(`${apiBase}/api/channels`)
    .then(channels => {
      dom("channel-list").innerHTML = channels.map(c => `
        <div class="channel-card-item" onclick="showChannelDetail(${c.id})" style="cursor:pointer">
          <div class="flex-header">
            <img src="${apiBase}/api/channels/${c.id}/thumbnail" class="channel-img" onerror="this.src='https://via.placeholder.com/50'">
            <div>
              <strong>${c.title}</strong>
              <div class="text-small">${c.customUrl || 'Sin URL'}</div>
            </div>
          </div>
          <button onclick="event.stopPropagation(); deleteChannel(${c.id})" class="btn-outline text-danger"><i class="fas fa-trash"></i></button>
        </div>
      `).join("") || "No hay canales registrados";
    });
}

function showChannelDetail(channelId) {
  currentChannelId = channelId;
  
  // Ocultar lista y mostrar detalle
  dom("channel-list").classList.add("hidden");
  dom("channel-detail-section").classList.remove("hidden");
  
  // Cargar toda la información del canal
  loadChannelDetailInfo(channelId);
  loadChannelStats(channelId);
  loadChannelSchedule(channelId);
  loadChannelCalendar(channelId);
  loadUpcomingPublications(channelId);
}

function closeChannelDetail() {
  dom("channel-detail-section").classList.add("hidden");
  dom("channel-list").classList.remove("hidden");
  currentChannelId = null;
}

function loadChannelDetailInfo(channelId) {
  fetchJson(`${apiBase}/api/channels`)
    .then(channels => {
      const channel = channels.find(c => c.id === channelId);
      if (!channel) return;
      
      dom("channel-detail-title").innerText = channel.title;
      
      dom("channel-info-content").innerHTML = `
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">Nombre:</span>
            <span class="info-value">${channel.title}</span>
          </div>
          <div class="info-item">
            <span class="info-label">URL Personalizada:</span>
            <span class="info-value">${channel.customUrl || 'N/A'}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Publicación:</span>
            <span class="info-value">${channel.publishedAt ? new Date(channel.publishedAt).toLocaleDateString() : 'N/A'}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Color:</span>
            <span class="info-value"><span class="color-badge" style="background:${channel.color || '#3b82f6'}">${channel.color || '#3b82f6'}</span></span>
          </div>
          <div class="info-item info-full">
            <span class="info-label">Descripción:</span>
            <span class="info-value description">${channel.description || 'Sin descripción'}</span>
          </div>
          ${channel.scrape_data ? `
          <div class="info-item">
            <span class="info-label">Último Scraping:</span>
            <span class="info-value">${channel.last_scraped_at ? new Date(channel.last_scraped_at).toLocaleString() : 'N/A'}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Estado:</span>
            <span class="info-value"><span class="badge ${channel.last_scrape_status === 'success' ? 'badge-success' : ''}">${channel.last_scrape_status || 'N/A'}</span></span>
          </div>
          ` : ''}
        </div>
      `;
    })
    .catch(err => {
      dom("channel-info-content").innerHTML = `<p class="text-error">Error al cargar información: ${err.message}</p>`;
    });
}

function loadChannelStats(channelId) {
  // Cargar estadísticas diarias
  fetchJson(`${apiBase}/api/analytics/daily-stats/${channelId}`)
    .then(stats => {
      if (stats.length > 0) {
        const last = stats[stats.length - 1];
        dom("channel-stats-content").innerHTML = `
          <div class="stats-grid">
            <div class="stat-mini">
              <span class="stat-mini-value">${last.subscriber_count.toLocaleString()}</span>
              <span class="stat-mini-label">Suscriptores</span>
            </div>
            <div class="stat-mini">
              <span class="stat-mini-value">${last.view_count.toLocaleString()}</span>
              <span class="stat-mini-label">Vistas</span>
            </div>
            <div class="stat-mini">
              <span class="stat-mini-value">${last.video_count.toLocaleString()}</span>
              <span class="stat-mini-label">Videos</span>
            </div>
            <div class="stat-mini">
              <span class="stat-mini-value">${last.stat_date || 'N/A'}</span>
              <span class="stat-mini-label">Fecha</span>
            </div>
          </div>
        `;
      } else {
        dom("channel-stats-content").innerHTML = `<p class="text-muted">No hay estadísticas disponibles</p>`;
      }
    })
    .catch(err => {
      dom("channel-stats-content").innerHTML = `<p class="text-error">Error al cargar estadísticas: ${err.message}</p>`;
    });
}

function selectChannel(channelId) {
  showChannelDetail(channelId);
}

function loadChannelSchedule(channelId) {
  fetchJson(`${apiBase}/api/schedules/channel/${channelId}`)
    .then(schedule => {
      dom("schedule-status").innerText = schedule.is_active ? "Programación activa" : "Programación inactiva";
      dom("schedule-status").className = schedule.is_active ? "badge-success" : "badge";
      
      // Videos largos
      dom("long-video-enabled").checked = schedule.long_video_enabled;
      dom("long-video-frequency").value = schedule.long_video_frequency;
      dom("long-video-info").innerText = schedule.long_video_enabled 
        ? `Videos largos cada ${schedule.long_video_frequency} días` 
        : "Desactivado";
      
      // Shorts
      dom("short-video-enabled").checked = schedule.short_video_enabled;
      dom("short-video-frequency").value = schedule.short_video_frequency;
      dom("short-video-info").innerText = schedule.short_video_enabled 
        ? `Shorts cada ${schedule.short_video_frequency} días` 
        : "Desactivado";
      
      // Artículos
      dom("article-enabled").checked = schedule.article_enabled;
      dom("article-frequency").value = schedule.article_frequency;
      dom("article-info").innerText = schedule.article_enabled 
        ? `Artículos cada ${schedule.article_frequency} días` 
        : "Desactivado";
      
      dom("start-date").value = schedule.start_date ? schedule.start_date.split("T")[0] : "";
    })
    .catch(err => console.error("Error cargando programación:", err));
}

function saveChannelSchedule(channelId) {
  const data = {
    long_video_enabled: dom("long-video-enabled").checked,
    long_video_frequency: parseInt(dom("long-video-frequency").value),
    short_video_enabled: dom("short-video-enabled").checked,
    short_video_frequency: parseInt(dom("short-video-frequency").value),
    article_enabled: dom("article-enabled").checked,
    article_frequency: parseInt(dom("article-frequency").value),
    start_date: dom("start-date").value + "T00:00:00",
    is_active: dom("schedule-active").checked
  };
  
  fetchJson(`${apiBase}/api/schedules/channel/${channelId}`, {
    method: "PUT",
    body: JSON.stringify(data)
  })
    .then(() => {
      alert("Programación guardada");
      loadChannelSchedule(channelId);
    })
    .catch(err => alert("Error al guardar: " + err.message));
}

function generateSchedule(channelId, year, month) {
  fetchJson(`${apiBase}/api/schedules/channel/${channelId}/generate?year=${year}&month=${month}`, {
    method: "POST"
  })
    .then(res => {
      alert(`Se crearon ${res.created} programaciones`);
      loadChannelCalendar(channelId);
    })
    .catch(err => alert("Error al generar: " + err.message));
}

function loadChannelCalendar(channelId) {
  fetchJson(`${apiBase}/api/schedules/channel/${channelId}/calendar/months`)
    .then(data => {
      renderCalendarView(channelId, data);
    })
    .catch(err => console.error("Error cargando calendario:", err));
}

function renderCalendarView(channelId, data) {
  const container = dom("channel-calendar-container");
  if (!container) return;
  
  const scheduleInfo = data.schedule_info;
  let html = '<div class="schedule-info-box">';
  
  if (scheduleInfo) {
    html += `
      <div class="flex-header" style="margin-bottom: 10px;">
        <strong>Programación actual:</strong>
        <span class="${scheduleInfo.is_active ? 'badge-success' : 'badge'}">${scheduleInfo.is_active ? 'Activa' : 'Inactiva'}</span>
      </div>
      <div class="text-small">
        ${scheduleInfo.long_video_enabled ? `🎬 Videos largos: cada ${scheduleInfo.long_video_frequency} días | ` : ''}
        ${scheduleInfo.short_video_enabled ? `📱 Shorts: cada ${scheduleInfo.short_video_frequency} días | ` : ''}
        ${scheduleInfo.article_enabled ? `📄 Artículos: cada ${scheduleInfo.article_frequency} días` : ''}
      </div>
    `;
  }
  html += '</div>';
  
  // Mes actual
  html += '<h4>📅 Mes Actual</h4>';
  const currentMonth = data.current_month;
  const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
  html += `<div class="calendar-header">${monthNames[currentMonth.month - 1]} ${currentMonth.year}</div>`;
  html += '<div class="calendar-weekdays"><div>Lu</div><div>Ma</div><div>Mi</div><div>Ju</div><div>Vu</div><div>Sá</div><div>Do</div></div>';
  html += '<div class="calendar-grid">';
  
  // Eventos del mes actual
  const eventsCurrent = currentMonth.events || [];
  const daysInMonth = new Date(currentMonth.year, currentMonth.month, 0).getDate();
  const firstDay = (new Date(currentMonth.year, currentMonth.month - 1, 1).getDay() + 6) % 7;
  
  let currentDay = 1;
  for (let i = 0; i < 42; i++) {
    if (i < firstDay || currentDay > daysInMonth) {
      html += '<div class="calendar-cell empty"></div>';
    } else {
      const dayEvents = eventsCurrent.filter(e => {
        const parts = e.date.split('-');
        return parseInt(parts[2]) === currentDay;
      });
      const isToday = currentDay === new Date().getDate() && currentMonth.month === new Date().getMonth() + 1;
      
      html += `<div class="calendar-cell ${isToday ? 'today' : ''}">`;
      html += `<span class="calendar-day">${currentDay}</span>`;
      dayEvents.forEach(e => {
        const icon = e.content_type === 'long_video' ? '🎬' : e.content_type === 'short' ? '📱' : '📄';
        const statusColor = e.status === 'published' ? '#10b981' : e.status === 'cancelled' ? '#ef4444' : '#3b82f6';
        html += `<div class="calendar-event" style="background:${statusColor}; font-size: 10px;" title="${e.content_type} - ${e.notes || ''}">${icon}</div>`;
      });
      html += '</div>';
      currentDay++;
    }
  }
  html += '</div>';
  
  // Mes siguiente
  html += '<h4 style="margin-top: 1.5rem;">📅 Mes Siguiente</h4>';
  const nextMonth = data.next_month;
  html += `<div class="calendar-header">${monthNames[nextMonth.month - 1]} ${nextMonth.year}</div>`;
  html += '<div class="calendar-weekdays"><div>Lu</div><div>Ma</div><div>Mi</div><div>Ju</div><div>Vu</div><div>Sá</div><div>Do</div></div>';
  html += '<div class="calendar-grid">';
  
  const eventsNext = nextMonth.events || [];
  const daysInNextMonth = new Date(nextMonth.year, nextMonth.month, 0).getDate();
  const firstDayNext = (new Date(nextMonth.year, nextMonth.month - 1, 1).getDay() + 6) % 7;
  
  let nextDay = 1;
  for (let i = 0; i < 42; i++) {
    if (i < firstDayNext || nextDay > daysInNextMonth) {
      html += '<div class="calendar-cell empty"></div>';
    } else {
      const dayEvents = eventsNext.filter(e => {
        const parts = e.date.split('-');
        return parseInt(parts[2]) === nextDay;
      });
      
      html += `<div class="calendar-cell">`;
      html += `<span class="calendar-day">${nextDay}</span>`;
      dayEvents.forEach(e => {
        const icon = e.content_type === 'long_video' ? '🎬' : e.content_type === 'short' ? '📱' : '📄';
        const statusColor = e.status === 'published' ? '#10b981' : e.status === 'cancelled' ? '#ef4444' : '#3b82f6';
        html += `<div class="calendar-event" style="background:${statusColor}; font-size: 10px;" title="${e.content_type}">${icon}</div>`;
      });
      html += '</div>';
      nextDay++;
    }
  }
  html += '</div>';
  
  // Botón para generar programaciones
  html += `
    <div style="margin-top: 15px;">
      <button onclick="generateSchedule(${channelId}, ${currentMonth.year}, ${currentMonth.month})" class="btn-outline">
        📅 Generar Mes Actual
      </button>
      <button onclick="generateSchedule(${channelId}, ${nextMonth.year}, ${nextMonth.month})" class="btn-outline">
        📅 Generar Mes Siguiente
      </button>
    </div>
  `;
  
  container.innerHTML = html;
}

function loadUpcomingPublications(channelId) {
  fetchJson(`${apiBase}/api/schedules/channel/${channelId}/upcoming?limit=10`)
    .then(publications => {
      const container = dom("upcoming-publications");
      if (!container) return;
      
      container.innerHTML = publications.map(p => {
        const icon = p.content_type === 'long_video' ? '🎬' : p.content_type === 'short' ? '📱' : '📄';
        return `
          <div class="item-row">
            <span>${icon} ${new Date(p.date).toLocaleDateString()}</span>
            <span class="badge">${p.content_type}</span>
            <span class="badge ${p.status === 'published' ? 'badge-success' : ''}">${p.status}</span>
            ${p.has_script ? '<span class="badge" style="background:#10b981">✓ Guión</span>' : '<span class="badge" style="background:#f59e0b">Sin guión</span>'}
          </div>
        `;
      }).join("") || "<p class='text-muted'>No hay publicaciones próximas</p>";
    })
    .catch(err => console.error("Error cargando publicaciones:", err));
}

function assignScriptToPublication(publicationId, scriptId) {
  fetchJson(`${apiBase}/api/schedules/publication/${publicationId}/assign-script?script_id=${scriptId}`, {
    method: "POST"
  })
    .then(() => {
      alert("Guión asociado correctamente");
      if (currentChannelId) loadUpcomingPublications(currentChannelId);
    })
    .catch(err => alert("Error al asociar: " + err.message));
}

function deleteChannel(id) {
  if (!confirm("¿Eliminar canal?")) return;
  fetchJson(`${apiBase}/api/channels/${id}`, { method: "DELETE" })
    .then(() => loadChannels());
}

dom("btn-create-files").onclick = () => {
  const name = dom("channel-name").value;
  if (!name) return alert("Introduce el nombre del canal");
  
  const status = dom("creation-status");
  const btn = dom("btn-create-files");
  const saveBtn = dom("btn-save-channel");
  
  status.classList.remove("hidden", "status-success", "status-error");
  status.innerText = "Ejecutando script de creación...";
  btn.disabled = true;

  fetchJson(`${apiBase}/api/channels/tools/create-files?name=${encodeURIComponent(name)}`, { method: "POST" })
    .then(res => {
      status.classList.add("status-success");
      status.innerText = "¡Correcto! Ficheros generados en channels_data. Ahora puedes guardar en la BD.";
      saveBtn.disabled = false;
    })
    .catch(err => {
      status.classList.add("status-error");
      status.innerText = "Error: " + err.message;
    })
    .finally(() => btn.disabled = false);
};

dom("channel-form").onsubmit = (e) => {
  e.preventDefault();
  const name = dom("channel-name").value;
  const color = dom("channel-color").value;
  
  fetchJson(`${apiBase}/api/channels`, {
    method: "POST",
    body: JSON.stringify({ title: name, color: color })
  })
    .then(() => {
      alert("Canal guardado en base de datos");
      dom("channel-form").reset();
      dom("btn-save-channel").disabled = true;
      dom("creation-status").classList.add("hidden");
      loadChannels();
    })
    .catch(err => alert("Error al guardar: " + err.message));
};

// HELPERS
function loadChannelSelectors() {
  fetchJson(`${apiBase}/api/channels`)
    .then(channels => {
      const selectors = ["dashboard-channel-filter", "content-channel-filter", "analytics-channel-filter", "modal-automation-channel-id"];
      selectors.forEach(id => {
        const el = dom(id);
        if (!el) return;
        const currentVal = el.value;
        el.innerHTML = (id.includes("modal") ? "" : '<option value="">Selecciona un canal</option>') + 
          channels.map(c => `<option value="${c.id}">${c.title}</option>`).join("");
        el.value = currentVal;
      });
    });
}

// AUTOMATIZACIÓN
function loadAutomation() {
  fetchJson(`${apiBase}/api/automation/tasks`)
    .then(tasks => {
      dom("automation-list").innerHTML = tasks.map(t => `
        <div class="item-row">
          <div>
            <strong>${t.name}</strong>
            <div class="text-small">${t.schedule_expression || 'Manual'} | ${t.is_active ? 'Activa' : 'Inactiva'}</div>
          </div>
          <button onclick="runAutomation(${t.id})" class="btn-primary btn-sm">Ejecutar</button>
        </div>
      `).join("") || "No hay tareas";
    });
}

function loadAutomationRuns() {
  fetchJson(`${apiBase}/api/automation/runs`)
    .then(runs => {
      dom("automation-runs-list").innerHTML = runs.slice(0, 5).map(r => `
        <div class="item-row">
          <span>${new Date(r.started_at).toLocaleString()}</span>
          <span class="badge">${r.status}</span>
        </div>
      `).join("") || "No hay ejecuciones";
    });
}

function runAutomation(id) {
  fetchJson(`${apiBase}/api/automation/tasks/${id}/run`, { method: "POST" })
    .then(() => {
      alert("Ejecución lanzada");
      loadAutomationRuns();
    });
}

// INICIALIZACIÓN
document.querySelectorAll("nav button").forEach(btn => {
  btn.onclick = () => showSection(btn.dataset.section);
});

dom("automation-form").onsubmit = (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());
  data.channel_id = parseInt(data.channel_id);
  data.workflow_definition = JSON.parse(data.workflow_definition);
  
  fetchJson(`${apiBase}/api/automation/tasks`, {
    method: "POST",
    body: JSON.stringify(data)
  }).then(() => {
    dom("automation-modal").close();
    loadAutomation();
  });
};

showSection("dashboard");
