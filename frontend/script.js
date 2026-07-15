const API_URL = "/generar-prompt";

document.getElementById("btnGenerar").addEventListener("click", async () => {
  const consulta = document.getElementById("consulta").value.trim();
  const loading = document.getElementById("loading");
  const resultado = document.getElementById("resultado");
  const errorDiv = document.getElementById("error");

  resultado.classList.add("oculto");
  errorDiv.classList.add("oculto");

  if (!consulta) {
    errorDiv.textContent = "Por favor escribe tu consulta.";
    errorDiv.classList.remove("oculto");
    return;
  }

  loading.classList.remove("oculto");

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ consulta }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Error al procesar la consulta.");
    }

    const data = await res.json();

    document.getElementById("tema").textContent = data.tema;
    document.getElementById("nivel").textContent = data.nivel;
    document.getElementById("ia").textContent = data.ia_recomendada;
    document.getElementById("justificacion").textContent = data.justificacion;
    document.getElementById("promptOptimizado").textContent = data.prompt_optimizado;

    resultado.classList.remove("oculto");
  } catch (e) {
    errorDiv.textContent = e.message;
    errorDiv.classList.remove("oculto");
  } finally {
    loading.classList.add("oculto");
  }
});

document.getElementById("btnCopiar").addEventListener("click", () => {
  const texto = document.getElementById("promptOptimizado").textContent;
  navigator.clipboard.writeText(texto);
  const btn = document.getElementById("btnCopiar");
  btn.textContent = "¡Copiado!";
  setTimeout(() => (btn.textContent = "Copiar prompt"), 1500);
});