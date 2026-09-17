import logging
from unittest.mock import MagicMock, patch

from app.services.clasificador import clasificar_consulta, clasificar_consulta_con_varias_imagenes


def test_clasificar_consulta_no_envia_max_tokens():
	fake_content = '{"tema":"medidas de tendencia central","nivel":"básico","ia_recomendada":"GPT","justificacion":"porque...","prompt_optimizado":"texto..."}'
	fake_response = MagicMock()
	fake_response.choices = [MagicMock()]
	fake_response.choices[0].message.content = fake_content

	mock_client = MagicMock()
	mock_client.chat.completions.create.return_value = fake_response

	with patch("app.services.clasificador.get_client", return_value=mock_client):
		clasificar_consulta("¿Qué es la media?")

	kwargs = mock_client.chat.completions.create.call_args.kwargs
	assert "max_tokens" not in kwargs


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


def test_clasificar_consulta_con_varias_imagenes_logs_fallback_y_modelos(caplog):
	fake_error = Exception("429 rate_limit_exceeded OTPM exceeded")
	mock_client = MagicMock()
	mock_client.chat.completions.create.side_effect = [fake_error, fake_error]

	with patch("app.services.clasificador.get_client", return_value=mock_client), \
		patch("app.services.clasificador.crear_mensaje_varias_imagenes", return_value={"role": "user", "content": "mensaje"}), \
		patch("app.services.clasificador.clasificar_consulta", return_value={"tema": "estadística"}) as fallback_text:
		with caplog.at_level(logging.INFO):
			resultado = clasificar_consulta_con_varias_imagenes("consulta", [("base64", "image/jpeg")])

	assert resultado == {"tema": "estadística"}
	assert fallback_text.called
	assert "qwen/qwen3.8-27b" in caplog.text
	assert "groq_text_fallback_attempt" in caplog.text


def test_clasificar_consulta_con_imagen_degrada_si_modelo_no_existe(caplog):
	model_not_found = Exception("Error code: 404 - model_not_found")
	mock_client = MagicMock()
	mock_client.chat.completions.create.side_effect = model_not_found

	with patch("app.services.clasificador.get_client", return_value=mock_client), \
		patch("app.services.clasificador.crear_mensaje_varias_imagenes", return_value={"role": "user", "content": "mensaje"}), \
		patch("app.services.clasificador.clasificar_consulta", return_value={"tema": "estadística"}) as fallback_text:
		with caplog.at_level(logging.INFO):
			resultado = clasificar_consulta_con_varias_imagenes("consulta", [("base64", "image/jpeg")])

	assert resultado == {"tema": "estadística"}
	assert fallback_text.called
	assert "groq_image_degrade_to_text" in caplog.text

