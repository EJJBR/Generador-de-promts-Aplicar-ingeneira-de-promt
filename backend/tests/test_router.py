from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app


def test_generar_prompt_endpoint():
    client = TestClient(app)

    fake_content = '{"tema":"t","nivel":"b","ia_recomendada":"GPT","justificacion":"x","prompt_optimizado":"p"}'
    fake_response = MagicMock()
    fake_response.choices = [MagicMock()]
    fake_response.choices[0].message.content = fake_content

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = fake_response

    with patch("app.services.clasificador.get_client", return_value=mock_client):
        resp = client.post("/generar-prompt", json={"consulta": "hola"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["tema"] == "t"
    assert data["ia_recomendada"] == "GPT"
