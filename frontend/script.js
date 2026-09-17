const LINKS_IA = {
  Claude: "https://claude.ai",
  GPT: "https://chatgpt.com",
  Gemini: "https://gemini.google.com",
  DeepSeek: "https://chat.deepseek.com",
};

const messagesEl = document.getElementById("messages");
const composerEl = document.getElementById("composer");
const inputEl = document.getElementById("consultaInput");
const sendBtn = document.getElementById("sendBtn");
const attachBtn = document.getElementById("attachBtn");
const fileInput = document.getElementById("fileInput");
const previewEl = document.getElementById("preview");
const previewList = document.getElementById("previewList");
const menuBtn = document.getElementById("menuBtn");
const sidebar = document.getElementById("sidebar");
const themeBtn = document.getElementById("themeBtn");
const themeIcon = document.getElementById("themeIcon");
const chips = document.querySelectorAll(".chip");

const MAX_IMAGENES = 4;
let imagenesSeleccionadas = [];

const imageModal = document.getElementById("imageModal");
const imageModalImg = document.getElementById("imageModalImg");
const imageModalClose = document.getElementById("imageModalClose");
const imageModalBackdrop = document.getElementById("imageModalBackdrop");

const sourceModal = document.getElementById("sourceModal");
const sourceModalClose = document.getElementById("sourceModalClose");
const sourceModalBackdrop = document.getElementById("sourceModalBackdrop");
const cameraSourceBtn = document.getElementById("cameraSourceBtn");
const fileSourceBtn = document.getElementById("fileSourceBtn");

const cameraModal = document.getElementById("cameraModal");
const cameraModalClose = document.getElementById("cameraModalClose");
const cameraModalBackdrop = document.getElementById("cameraModalBackdrop");
const cameraVideo = document.getElementById("cameraVideo");
const cameraCaptureBtn = document.getElementById("cameraCaptureBtn");
const cameraCancelBtn = document.getElementById("cameraCancelBtn");
let cameraStream = null;

function abrirImageModal(src, alt = "Previsualización de imagen") {
  if (!imageModal || !imageModalImg) return;

  imageModalImg.src = src;
  imageModalImg.alt = alt;
  imageModal.classList.add("visible");
  imageModal.setAttribute("aria-hidden", "false");
}

function cerrarImageModal() {
  if (!imageModal || !imageModalImg) return;

  imageModal.classList.remove("visible");
  imageModal.setAttribute("aria-hidden", "true");
  imageModalImg.removeAttribute("src");
  imageModalImg.alt = "";
}

previewList?.addEventListener("click", (event) => {
  const img = event.target.closest("img");
  if (!img || !img.src) return;
  abrirImageModal(img.src, "Vista previa de imagen seleccionada");
});

imageModalClose?.addEventListener("click", cerrarImageModal);
imageModalBackdrop?.addEventListener("click", cerrarImageModal);
window.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && imageModal && imageModal.getAttribute("aria-hidden") === "false") {
    cerrarImageModal();
  }
});

function renderizarPreviews() {
  if (!previewList) return;

  previewList.innerHTML = "";

  if (imagenesSeleccionadas.length === 0) {
    previewEl.hidden = true;
    return;
  }

  previewEl.hidden = false;

  imagenesSeleccionadas.forEach((archivo, index) => {
    const item = document.createElement("div");
    item.className = "preview-item";

    const img = document.createElement("img");
    img.alt = `Vista previa ${index + 1}`;

    const lector = new FileReader();
    lector.onload = (e) => {
      img.src = e.target.result;
    };
    lector.readAsDataURL(archivo);

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "preview-remove";
    btn.setAttribute("aria-label", `Quitar imagen ${index + 1}`);
    btn.innerHTML = '<svg class="icon" viewBox="0 0 24 24"><path d="M18.3 5.71 12 12.01l-6.3-6.3-1.41 1.41 6.3 6.3-6.3 6.3 1.41 1.41 6.3-6.3 6.3 6.3 1.41-1.41-6.3-6.3 6.3-6.3z"/></svg>';
    btn.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      imagenesSeleccionadas = imagenesSeleccionadas.filter((_, idx) => idx !== index);
      if (fileInput) fileInput.value = "";
      renderizarPreviews();
    });

    item.appendChild(img);
    item.appendChild(btn);
    previewList.appendChild(item);
  });
}

function limpiarImagenesSeleccionadas() {
  imagenesSeleccionadas = [];
  if (fileInput) {
    fileInput.value = "";
  }
  if (previewEl) {
    previewEl.hidden = true;
  }
  if (previewList) {
    previewList.innerHTML = "";
  }
}

/* ---------- Tema claro/oscuro ---------- */
const ICONO_SOL = '<path d="M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0-5a1 1 0 0 1 1 1v2a1 1 0 1 1-2 0V3a1 1 0 0 1 1-1zm0 18a1 1 0 0 1 1 1v2a1 1 0 1 1-2 0v-2a1 1 0 0 1 1-1zM3 11a1 1 0 0 1 1 1H2a1 1 0 1 1 0-2h2a1 1 0 0 1-1 1zm18 0a1 1 0 0 1 1 1h2a1 1 0 1 1 0-2h-2a1 1 0 0 1-1 1zM4.2 4.2a1 1 0 0 1 1.4 0l1.4 1.4a1 1 0 1 1-1.4 1.4L4.2 5.6a1 1 0 0 1 0-1.4zm14.8 14.8a1 1 0 0 1 1.4 0l1.4 1.4a1 1 0 1 1-1.4 1.4l-1.4-1.4a1 1 0 0 1 0-1.4zM19.8 4.2a1 1 0 0 1 0 1.4l-1.4 1.4a1 1 0 1 1-1.4-1.4l1.4-1.4a1 1 0 0 1 1.4 0zM5.6 18.6a1 1 0 0 1 0 1.4L4.2 21.4a1 1 0 1 1-1.4-1.4l1.4-1.4a1 1 0 0 1 1.4 0z"/>';
const ICONO_LUNA = '<path d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z"/>';

function aplicarTema(tema) {
  document.documentElement.setAttribute("data-theme", tema);
  themeIcon.innerHTML = tema === "dark" ? ICONO_SOL : ICONO_LUNA;
  localStorage.setItem("tema", tema);
}

(function initTema() {
  const guardado = localStorage.getItem("tema");
  const prefiereOscuro = window.matchMedia("(prefers-color-scheme: dark)").matches;
  aplicarTema(guardado || (prefiereOscuro ? "dark" : "light"));
})();

themeBtn.addEventListener("click", () => {
  const actual = document.documentElement.getAttribute("data-theme");
  aplicarTema(actual === "dark" ? "light" : "dark");
});

/* ---------- Sidebar en móvil ---------- */
menuBtn.addEventListener("click", () => {
  sidebar.classList.toggle("open");
});

chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    inputEl.value = chip.dataset.texto;
    inputEl.focus();
    sidebar.classList.remove("open");
  });
});

/* ---------- Adjuntar imagen ---------- */
attachBtn.addEventListener("click", () => {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    fileInput.click();
    return;
  }

  abrirSourceModal();
});

function abrirSourceModal() {
  if (!sourceModal) return;

  sourceModal.classList.add("visible");
  sourceModal.setAttribute("aria-hidden", "false");
}

function cerrarSourceModal() {
  if (!sourceModal) return;

  sourceModal.classList.remove("visible");
  sourceModal.setAttribute("aria-hidden", "true");
}

cameraSourceBtn?.addEventListener("click", () => {
  cerrarSourceModal();
  abrirCamara();
});

fileSourceBtn?.addEventListener("click", () => {
  cerrarSourceModal();
  fileInput?.click();
});

sourceModalClose?.addEventListener("click", () => cerrarSourceModal());
sourceModalBackdrop?.addEventListener("click", () => cerrarSourceModal());

function abrirCamara() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Tu navegador no soporta acceso a la cámara.");
    return;
  }

  if (!cameraModal || !cameraVideo) return;

  cameraModal.classList.add("visible");
  cameraModal.setAttribute("aria-hidden", "false");

  navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false })
    .then((stream) => {
      cameraStream = stream;
      cameraVideo.srcObject = stream;
      cameraVideo.play();
    })
    .catch(() => {
      cerrarCamara();
      fileInput?.click();
    });
}

function cerrarCamara() {
  if (!cameraModal || !cameraVideo) return;

  cameraModal.classList.remove("visible");
  cameraModal.setAttribute("aria-hidden", "true");

  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
  }

  if (cameraVideo) {
    cameraVideo.pause();
    cameraVideo.srcObject = null;
  }
}

cameraCaptureBtn?.addEventListener("click", () => {
  if (!cameraVideo || !cameraModal) return;

  const canvas = document.createElement("canvas");
  const width = cameraVideo.videoWidth || 1024;
  const height = cameraVideo.videoHeight || 768;
  canvas.width = width;
  canvas.height = height;

  const contexto = canvas.getContext("2d");
  contexto.drawImage(cameraVideo, 0, 0, width, height);

  canvas.toBlob((blob) => {
    if (!blob) {
      cerrarCamara();
      return;
    }

    const archivo = new File([blob], `foto-${Date.now()}.png`, { type: "image/png" });
    manejarArchivosImagenes([archivo]);
    cerrarCamara();
  }, "image/png");
});

cameraCancelBtn?.addEventListener("click", () => cerrarCamara());
cameraModalClose?.addEventListener("click", () => cerrarCamara());
cameraModalBackdrop?.addEventListener("click", () => cerrarCamara());

function manejarArchivosImagenes(archivos) {
  if (!archivos.length) {
    limpiarImagenesSeleccionadas();
    return;
  }

  const nuevos = archivos.filter((archivo) => archivo && archivo.type && archivo.type.startsWith("image/"));
  const actuales = imagenesSeleccionadas.length;
  const restantes = MAX_IMAGENES - actuales;

  if (restantes <= 0) {
    alert(`Máximo ${MAX_IMAGENES} imágenes a la vez.`);
    if (fileInput) fileInput.value = "";
    return;
  }

  const paraAgregar = nuevos.slice(0, restantes);
  if (!paraAgregar.length) {
    if (fileInput) fileInput.value = "";
    return;
  }

  imagenesSeleccionadas = [...imagenesSeleccionadas, ...paraAgregar];
  renderizarPreviews();
  if (fileInput) fileInput.value = "";
}

fileInput.addEventListener("change", () => {
  const archivos = Array.from(fileInput.files || []);
  manejarArchivosImagenes(archivos);
});

composerEl.addEventListener("paste", (event) => {
  const items = Array.from(event.clipboardData?.items || []);
  const imagenesPegadas = items
    .filter((item) => item.type.startsWith("image/"))
    .map((item) => item.getAsFile())
    .filter(Boolean);

  if (!imagenesPegadas.length) return;

  event.preventDefault();
  manejarArchivosImagenes(imagenesPegadas);
});

composerEl.addEventListener("dragover", (event) => {
  const archivos = Array.from(event.dataTransfer?.files || []);
  if (!archivos.length) return;

  event.preventDefault();
  event.dataTransfer.dropEffect = "copy";
  inputEl.classList.add("drag-target");
  composerEl.classList.add("composer-drop");
});

composerEl.addEventListener("dragleave", (event) => {
  if (event.relatedTarget && composerEl.contains(event.relatedTarget)) return;
  inputEl.classList.remove("drag-target");
  composerEl.classList.remove("composer-drop");
});

composerEl.addEventListener("drop", (event) => {
  event.preventDefault();
  const archivos = Array.from(event.dataTransfer?.files || []);
  inputEl.classList.remove("drag-target");
  composerEl.classList.remove("composer-drop");
  manejarArchivosImagenes(archivos);
});

/* ---------- Utilidades de mensajes ---------- */
function crearAvatarBot() {
  const div = document.createElement("div");
  div.className = "avatar avatar-bot";
  div.innerHTML = '<svg class="icon" viewBox="0 0 24 24"><path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7z"/></svg>';
  return div;
}

function agregarMensajeUsuario(texto, imagenesDataUrls) {
  const msg = document.createElement("div");
  msg.className = "msg msg-user";
  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if (texto) {
    const p = document.createElement("p");
    p.textContent = texto;
    bubble.appendChild(p);
  }

  const imagenes = Array.isArray(imagenesDataUrls)
    ? imagenesDataUrls
    : imagenesDataUrls ? [imagenesDataUrls] : [];

  if (imagenes.length > 0) {
    const contenedor = document.createElement("div");
    contenedor.className = "message-images";

    imagenes.forEach((url) => {
      const img = document.createElement("img");
      img.src = url;
      img.alt = "Imagen enviada";
      img.className = "message-image";
      img.addEventListener("click", () => abrirImageModal(url, "Imagen enviada"));
      contenedor.appendChild(img);
    });

    bubble.appendChild(contenedor);
  }

  msg.appendChild(bubble);
  messagesEl.appendChild(msg);
  desplazarAbajo();
}

function agregarCargando() {
  const msg = document.createElement("div");
  msg.className = "msg msg-bot";
  msg.id = "msgCargando";
  msg.appendChild(crearAvatarBot());
  const bubble = document.createElement("div");
  bubble.className = "bubble bubble-bot";
  bubble.innerHTML = '<div class="loading-dots"><span></span><span></span><span></span></div>';
  msg.appendChild(bubble);
  messagesEl.appendChild(msg);
  desplazarAbajo();
}

function quitarCargando() {
  const el = document.getElementById("msgCargando");
  if (el) el.remove();
}

function agregarError(texto) {
  const msg = document.createElement("div");
  msg.className = "msg msg-bot";
  msg.appendChild(crearAvatarBot());
  const bubble = document.createElement("div");
  bubble.className = "bubble error-bubble";
  bubble.innerHTML = `<p>${texto}</p>`;
  msg.appendChild(bubble);
  messagesEl.appendChild(msg);
  desplazarAbajo();
}

function agregarResultado(data) {
  const msg = document.createElement("div");
  msg.className = "msg msg-bot";
  msg.appendChild(crearAvatarBot());

  const bubble = document.createElement("div");
  bubble.className = "bubble bubble-bot result-card";

  const tags = document.createElement("div");
  tags.className = "result-tags";
  tags.innerHTML = `<span>${data.tema || "-"}</span><span class="dot">·</span><span>Nivel ${data.nivel || "-"}</span>`;
  bubble.appendChild(tags);

  const link = LINKS_IA[data.ia_recomendada] || "#";
  const badge = document.createElement("a");
  badge.className = "ia-badge";
  badge.href = link;
  badge.target = "_blank";
  badge.rel = "noopener";
  badge.innerHTML = `<svg class="icon" viewBox="0 0 24 24"><path d="M12 2 1 21h22L12 2zm0 5.5 7.5 13h-15L12 7.5z"/></svg>Usar ${data.ia_recomendada || "IA"}`;
  badge.addEventListener("click", () => {
    navigator.clipboard.writeText(data.prompt_optimizado || "");
  });
  bubble.appendChild(badge);

  if (data.justificacion) {
    const just = document.createElement("p");
    just.className = "bubble-note";
    just.textContent = data.justificacion;
    bubble.appendChild(just);
  }

  const promptBox = document.createElement("div");
  promptBox.className = "prompt-box";
  promptBox.textContent = data.prompt_optimizado || "";
  bubble.appendChild(promptBox);

  const acciones = document.createElement("div");
  acciones.className = "result-actions";
  const copyBtn = document.createElement("button");
  copyBtn.type = "button";
  copyBtn.className = "copy-btn";
  copyBtn.innerHTML = '<svg class="icon" viewBox="0 0 24 24"><path d="M16 1H4a2 2 0 0 0-2 2v14h2V3h12V1zm3 4H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm0 16H8V7h11v14z"/></svg><span>Copiar prompt</span>';
  copyBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(data.prompt_optimizado || "");
    copyBtn.classList.add("copied");
    copyBtn.querySelector("span").textContent = "¡Copiado!";
    setTimeout(() => {
      copyBtn.classList.remove("copied");
      copyBtn.querySelector("span").textContent = "Copiar prompt";
    }, 1500);
  });
  acciones.appendChild(copyBtn);
  bubble.appendChild(acciones);

  msg.appendChild(bubble);
  messagesEl.appendChild(msg);
  desplazarAbajo();
}

function desplazarAbajo() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

/* ---------- Envío ---------- */
composerEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const texto = inputEl.value.trim();

  if (!texto && imagenesSeleccionadas.length === 0) {
    inputEl.focus();
    return;
  }

  const archivosParaEnviar = [...imagenesSeleccionadas];
  const imagenesParaMostrar = archivosParaEnviar.map((archivo) => URL.createObjectURL(archivo));
  agregarMensajeUsuario(texto, imagenesParaMostrar);

  inputEl.value = "";
  limpiarImagenesSeleccionadas();
  sendBtn.disabled = true;

  agregarCargando();

  try {
    let respuesta;
    
    if (archivosParaEnviar.length > 0) {
      const formData = new FormData();
      formData.append("consulta", texto);
      archivosParaEnviar.forEach((archivo) => formData.append("imagenes", archivo));
      respuesta = await fetch("/generar-prompt/imagen", {
        method: "POST",
        body: formData,
      });
    } else {
      respuesta = await fetch("/generar-prompt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ consulta: texto }),
      });
    }

    quitarCargando();

    if (!respuesta.ok) {
      const err = await respuesta.json().catch(() => ({}));
      throw new Error(err.detail || "No se pudo procesar la consulta.");
    }

    const data = await respuesta.json();
    agregarResultado(data);
  } catch (err) {
    quitarCargando();
    agregarError(err.message || "Ocurrió un error inesperado. Intenta de nuevo.");
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
});