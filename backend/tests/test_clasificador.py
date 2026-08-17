from unittest.mock import MagicMock, patch

from app.services.clasificador import clasificar_consulta


def test_clasificar_consulta_parses_json():
	fake_content = '{"tema":"medidas de tendencia central","nivel":"básico","ia_recomendada":"GPT","justificacion":"porque...","prompt_optimizado":"texto..."}'
	fake_response = MagicMock()
	fake_response.choices = [MagicMock()]
	fake_response.choices[0].message.content = fake_content

	mock_client = MagicMock()
	mock_client.chat.completions.create.return_value = fake_response

	with patch("app.services.clasificador.get_client", return_value=mock_client):
		resultado = clasificar_consulta("¿Qué es la media?")

	assert isinstance(resultado, dict)
	assert resultado["tema"] == "medidas de tendencia central"
	assert "prompt_optimizado" in resultado


def test_clasificar_consulta_raises_on_invalid_json():
	fake_content = "not a json"
	fake_response = MagicMock()
	fake_response.choices = [MagicMock()]
	fake_response.choices[0].message.content = fake_content

	mock_client = MagicMock()
	mock_client.chat.completions.create.return_value = fake_response

	with patch("app.services.clasificador.get_client", return_value=mock_client):
		try:
			clasificar_consulta("consulta que devuelve texto no-json")
			raised = False
		except ValueError:
			raised = True

	assert raised is True

