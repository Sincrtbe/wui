const apiBase = "/api";

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

function showSection(sectionId) {
  document.querySelectorAll(".page").forEach((section) => {
    section.classList.toggle("active", section.id === sectionId);
  });
  document.querySelectorAll("nav button").forEach((button) => {
    button.classList.toggle("active", button.dataset.section === sectionId);
  });

  switch (sectionId) {
    case "dashboard":
      loadDashboardChannelFilter();
      loadDashboard();
      break;
    case "channels":
      loadChannels();
      break;
    case "scripts":
      loadScripts();
      break;
    case "videos":
      loadVideos();
      break;
    case "publications":
      loadPublications();
      break;
    case "automation":
      loadAutomation();
      loadAutomationRuns();
      break;
  }
}

function init() {
  document.querySelectorAll("nav button").forEach((button) => {
    button.addEventListener("click", () => showSection(button.dataset.section));
  });

  dom("channel-form").addEventListener("submit", handleChannelCreate);
  dom("script-form").addEventListener("submit", handleScriptCreate);
  dom("video-form").addEventListener("submit", handleVideoCreate);
  dom("publication-form").addEventListener("submit", handlePublicationCreate);
  dom("automation-form").addEventListener("submit", handleAutomationCreate);

  const dashboardFilter = dom("dashboard-channel-filter");
  if (dashboardFilter) {
    dashboardFilter.addEventListener("change", loadDashboard);
  }

  showSection("dashboard");
}

function setContent(targetId, html) {
  dom(targetId).innerHTML = html;
}

function loadDashboardChannelFilter() {
  fetchJson(`${apiBase}/channels`)
    .then((channels) => {
      const filter = dom("dashboard-channel-filter");
      if (!filter) return;
      filter.innerHTML = `<option value="">Todos los canales</option>` +
        channels
          .map(
            (channel) =>
              `<option value="${channel.id}">${channel.name} (${channel.email || "sin email"})</option>`
          )
          .join("");
    })
    .catch((error) => {
      console.warn("No se pudo cargar filtro de canales:", error);
    });
}

function buildPublicationCalendar(events) {
  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const weekdayStart = firstDay.getDay();
  const days = [];

  for (let i = 0; i < weekdayStart; i += 1) {
    days.push("<div class=\"calendar-cell empty\"></div>");
  }

  for (let day = 1; day <= lastDay.getDate(); day += 1) {
    const date = new Date(year, month, day);
    const dateKey = date.toISOString().slice(0, 10);
    const dayEvents = events.filter((event) => event.date.slice(0, 10) === dateKey);
    const isToday = dateKey === today.toISOString().slice(0, 10);
    const eventLabels = dayEvents
      .map(
        (event) =>
          `<div class="calendar-event" style="background:${event.channel_color};">${event.channel_name}: ${event.title}</div>`
      )
      .join("");

    days.push(
      `<div class="calendar-cell ${isToday ? "today" : ""}">
          <div class="calendar-day">${day}</div>
          ${eventLabels}
        </div>`
    );
  }

  return `
    <div class="calendar-grid">
      ${days.join("")}
    </div>
  `;
}

function loadDashboard() {
  setContent("dashboard-content", "Cargando...");
  const channelId = dom("dashboard-channel-filter")?.value || "";
  const channelQuery = channelId ? `?channel_id=${channelId}` : "";
  fetchJson(`${apiBase}/dashboard/summary${channelQuery}`)
    .then((data) => {
      const scriptRows = Object.entries(data.scripts_by_status)
        .map(([status, count]) => `<li>${status}: ${count}</li>`)
        .join("\n") || "<li>Sin datos</li>";
      const videoRows = Object.entries(data.videos_by_status)
        .map(([status, count]) => `<li>${status}: ${count}</li>`)
        .join("\n") || "<li>Sin datos</li>";
      const channelRows = data.channels_overview
        .map(
          (channel) =>
            `<div class="channel-summary" style="border-left: 5px solid ${channel.channel_color};">
              <strong>${channel.channel_name}</strong>
              <div>Email: ${channel.email || "Sin email"}</div>
              <div>Redes: ${channel.social_links ? Object.entries(channel.social_links).map(([k,v]) => `${k}: <a href='${v}' target='_blank'>${v}</a>`).join(" | ") : "Sin redes"}</div>
              <div>Checkpoints: ${channel.checkpoints ? Object.entries(channel.checkpoints).map(([k,v]) => `${k}=${v}`).join(", ") : "Sin checkpoints"}</div>
              <div>Guiones: ${channel.total_scripts} | Vídeos: ${channel.total_videos} | Próximas publicaciones: ${channel.upcoming_publications}</div>
              <div>Último scrape: ${channel.last_scraped_at ? new Date(channel.last_scraped_at).toLocaleString() : "Nunca"} (${channel.last_scrape_status || "-"})</div>
            </div>`
        )
        .join("\n") || "<p>No hay canales cargados.</p>";
      const calendarHtml = buildPublicationCalendar(data.publication_calendar || []);
      const activeRuns = data.active_automation_runs
        .map(
          (run) =>
            `<li>${run.task_name} - ${run.status} - ${run.started_at ? new Date(run.started_at).toLocaleString() : "Sin iniciar"}</li>`
        )
        .join("\n") || "<li>No hay ejecuciones activas</li>";

      setContent(
        "dashboard-content",
        `
          <div class="dashboard-grid">
            <div class="dashboard-card small">
              <h3>Guiones por estado</h3>
              <ul>${scriptRows}</ul>
            </div>
            <div class="dashboard-card small">
              <h3>Vídeos por estado</h3>
              <ul>${videoRows}</ul>
            </div>
            <div class="dashboard-card small">
              <h3>Ejecuciones activas</h3>
              <ul>${activeRuns}</ul>
            </div>
          </div>
          <div class="dashboard-card">
            <h3>Calendario de publicaciones</h3>
            ${calendarHtml}
          </div>
          <div class="dashboard-card">
            <h3>Resumen por canal</h3>
            ${channelRows}
          </div>
        `
      );
    })
    .catch((error) => {
      setContent("dashboard-content", `<p class="preformatted">${error.message}</p>`);
    });
}

function createList(items, renderItem) {
  if (!items.length) {
    return `<p>No hay elementos registrados.</p>`;
  }
  return items.map(renderItem).join("");
}

function loadChannels() {
  setContent("channel-list", "Cargando...");
  fetchJson(`${apiBase}/channels`)
    .then((channels) => {
      setContent(
        "channel-list",
        createList(channels, (channel) => {
          return `
            <div class="item-row">
              <div>
                <strong>${channel.name}</strong>
                <div>Color: <span style="font-weight:700;color:${channel.color}">${channel.color}</span></div>
                <div>Email: ${channel.email || "Sin email"}</div>
                <div>Redes: ${channel.social_links ? Object.entries(channel.social_links).map(([k,v]) => `${k}: <a href='${v}' target='_blank'>${v}</a>`).join(" | ") : "Sin redes"}</div>
                <div>Checkpoints: ${channel.checkpoints ? Object.entries(channel.checkpoints).map(([k,v]) => `${k}=${v}`).join(", ") : "Sin checkpoints"}</div>
                <div>Último scrape: ${channel.last_scraped_at ? new Date(channel.last_scraped_at).toLocaleString() : "Nunca"} (${channel.last_scrape_status || "-"})</div>
                <div>ID: ${channel.id}</div>
              </div>
              <button class="inline-button" onclick="deleteChannel(${channel.id})">Eliminar</button>
            </div>
          `;
        })
      );
    })
    .catch((error) => {
      setContent("channel-list", `<p class="preformatted">${error.message}</p>`);
    });
}

function handleChannelCreate(event) {
  event.preventDefault();
  const form = event.target;
  const parsePairs = (value) =>
    value
      .split(",")
      .map((pair) => pair.trim())
      .filter(Boolean)
      .reduce((acc, pair) => {
        const [key, ...rest] = pair.split("=");
        if (!key || rest.length === 0) return acc;
        acc[key.trim()] = rest.join("=").trim();
        return acc;
      }, {});

  const data = {
    name: form.name.value,
    color: form.color.value,
    email: form.email.value || null,
    social_links: parsePairs(form.social_links.value),
    checkpoints: parsePairs(form.checkpoints.value),
  };
  fetchJson(`${apiBase}/channels`, {
    method: "POST",
    body: JSON.stringify(data),
  })
    .then(() => {
      form.reset();
      loadChannels();
    })
    .catch((error) => alert(error.message));
}

function deleteChannel(id) {
  if (!confirm("Eliminar canal?")) return;
  fetchJson(`${apiBase}/channels/${id}`, { method: "DELETE" })
    .then(() => loadChannels())
    .catch((error) => alert(error.message));
}

function loadScripts() {
  setContent("script-list", "Cargando...");
  fetchJson(`${apiBase}/scripts`)
    .then((scripts) => {
      setContent(
        "script-list",
        createList(scripts, (script) => {
          return `
            <div class="item-row">
              <div>
                <strong>${script.title}</strong>
                <div>ID: ${script.id} | Canal: ${script.channel_id} | Estado: ${script.status}</div>
                <div>${script.description || "Sin descripción"}</div>
                <div>Tags: ${script.tags.join(", ")}</div>
              </div>
            </div>
          `;
        })
      );
    })
    .catch((error) => {
      setContent("script-list", `<p class="preformatted">${error.message}</p>`);
    });
}

function handleScriptCreate(event) {
  event.preventDefault();
  const form = event.target;
  const data = {
    channel_id: Number(form.channel_id.value),
    title: form.title.value,
    description: form.description.value,
    voice_script: form.voice_script.value,
    graphic_script: form.graphic_script.value,
    tags: form.tags.value
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean),
  };
  fetchJson(`${apiBase}/scripts`, {
    method: "POST",
    body: JSON.stringify(data),
  })
    .then(() => {
      form.reset();
      loadScripts();
    })
    .catch((error) => alert(error.message));
}

function loadVideos() {
  setContent("video-list", "Cargando...");
  fetchJson(`${apiBase}/videos`)
    .then((videos) => {
      setContent(
        "video-list",
        createList(videos, (video) => {
          return `
            <div class="item-row">
              <div>
                <strong>${video.title}</strong>
                <div>ID: ${video.id} | Canal: ${video.channel_id} | Guion: ${video.script_id || "-"}</div>
                <div>Duración: ${video.duration || "-"} seg | Estado: ${video.status}</div>
              </div>
            </div>
          `;
        })
      );
    })
    .catch((error) => {
      setContent("video-list", `<p class="preformatted">${error.message}</p>`);
    });
}

function handleVideoCreate(event) {
  event.preventDefault();
  const form = event.target;
  const data = {
    channel_id: Number(form.channel_id.value),
    script_id: form.script_id.value ? Number(form.script_id.value) : null,
    title: form.title.value,
    duration: form.duration.value ? Number(form.duration.value) : null,
  };
  fetchJson(`${apiBase}/videos`, {
    method: "POST",
    body: JSON.stringify(data),
  })
    .then(() => {
      form.reset();
      loadVideos();
    })
    .catch((error) => alert(error.message));
}

function loadPublications() {
  setContent("publication-list", "Cargando...");
  fetchJson(`${apiBase}/publications`)
    .then((publications) => {
      setContent(
        "publication-list",
        createList(publications, (pub) => {
          return `
            <div class="item-row">
              <div>
                <strong>ID ${pub.id}</strong>
                <div>Canal: ${pub.channel_id} | Guion: ${pub.script_id || "-"}</div>
                <div>${new Date(pub.scheduled_datetime).toLocaleString()} | Estado: ${pub.status}</div>
                <div>${pub.notes || "Sin notas"}</div>
              </div>
            </div>
          `;
        })
      );
    })
    .catch((error) => {
      setContent("publication-list", `<p class="preformatted">${error.message}</p>`);
    });
}

function handlePublicationCreate(event) {
  event.preventDefault();
  const form = event.target;
  const data = {
    channel_id: Number(form.channel_id.value),
    script_id: form.script_id.value ? Number(form.script_id.value) : null,
    scheduled_datetime: new Date(form.scheduled_datetime.value).toISOString(),
    notes: form.notes.value,
  };
  fetchJson(`${apiBase}/publications`, {
    method: "POST",
    body: JSON.stringify(data),
  })
    .then(() => {
      form.reset();
      loadPublications();
    })
    .catch((error) => alert(error.message));
}

function loadAutomation() {
  setContent("automation-tasks", "Cargando...");
  fetchJson(`${apiBase}/automation/tasks`)
    .then((tasks) => {
      setContent(
        "automation-tasks",
        createList(tasks, (task) => {
          return `
            <div class="item-row">
              <div>
                <strong>${task.name}</strong>
                <div>ID: ${task.id} | Canal: ${task.channel_id} | Activa: ${task.is_active}</div>
                <div>${task.description || "Sin descripción"}</div>
                <div>CRON: ${task.schedule_expression || "No programada"}</div>
                <div><pre class="preformatted">${JSON.stringify(task.workflow_definition, null, 2)}</pre></div>
              </div>
              <div>
                <button class="inline-button" onclick="runAutomation(${task.id})">Ejecutar</button>
              </div>
            </div>
          `;
        })
      );
    })
    .catch((error) => {
      setContent("automation-tasks", `<p class="preformatted">${error.message}</p>`);
    });
}

function handleAutomationCreate(event) {
  event.preventDefault();
  const form = event.target;
  const data = {
    channel_id: Number(form.channel_id.value),
    name: form.name.value,
    description: form.description.value,
    schedule_expression: form.schedule_expression.value || null,
    workflow_definition: JSON.parse(form.workflow_definition.value),
  };
  fetchJson(`${apiBase}/automation/tasks`, {
    method: "POST",
    body: JSON.stringify(data),
  })
    .then(() => {
      form.reset();
      loadAutomation();
      loadAutomationRuns();
    })
    .catch((error) => alert(error.message));
}

function runAutomation(id) {
  fetchJson(`${apiBase}/automation/tasks/${id}/run`, { method: "POST" })
    .then(() => {
      alert("Tarea iniciada");
      loadAutomationRuns();
    })
    .catch((error) => alert(error.message));
}

function loadAutomationRuns() {
  setContent("automation-runs", "Cargando...");
  fetchJson(`${apiBase}/automation/runs`)
    .then((runs) => {
      setContent(
        "automation-runs",
        createList(runs, (run) => {
          return `
            <div class="item-row">
              <div>
                <strong>Ejecución ${run.id}</strong>
                <div>Tarea: ${run.task_id}</div>
                <div>Estado: ${run.status}</div>
                <div>Inicio: ${run.started_at ? new Date(run.started_at).toLocaleString() : "-"}</div>
                <div>Fin: ${run.finished_at ? new Date(run.finished_at).toLocaleString() : "-"}</div>
              </div>
              <div>
                <button class="inline-button" onclick="retryRun(${run.id})">Reintentar</button>
              </div>
            </div>
          `;
        })
      );
    })
    .catch((error) => {
      setContent("automation-runs", `<p class="preformatted">${error.message}</p>`);
    });
}

function retryRun(runId) {
  fetchJson(`${apiBase}/automation/runs/${runId}/retry`, { method: "POST" })
    .then(() => {
      alert("Reintento iniciado");
      loadAutomationRuns();
    })
    .catch((error) => alert(error.message));
}

window.init = init;
window.deleteChannel = deleteChannel;
window.runAutomation = runAutomation;
window.retryRun = retryRun;

init();
