import pytest
import json
from io import BytesIO
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


client = TestClient(app)


def crear_imagen_test(formato: str = "JPEG") -> BytesIO:
    """
    Crea una imagen de prueba en memoria.
    
    Args:
        formato: formato de imagen ('JPEG', 'PNG', etc)
        
    Returns:
        BytesIO con imagen
    """
    img = Image.new("RGB", (100, 100), color="red")
    img_bytes = BytesIO()
    img.save(img_bytes, format=formato)
    img_bytes.seek(0)
    return img_bytes


class TestEndpointImagenConMock:
    """Tests para el endpoint /generar-prompt/imagen con Groq mockeado"""

    def test_generar_prompt_imagen_varias_imagenes_exitoso(self):
        """Test: acepta más de una imagen y las envía en un solo mensaje"""
        mock_response = {
            "tema": "Probabilidad",
            "nivel": "Básico",
            "ia_recomendada": "Claude",
            "justificacion": "Para análisis de varios gráficos",
            "prompt_optimizado": "Analiza ambos gráficos"
        }

        imagen_1 = crear_imagen_test("JPEG")
        imagen_2 = crear_imagen_test("PNG")

        with patch("app.services.clasificador.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            mock_response_obj = MagicMock()
            mock_response_obj.choices[0].message.content = json.dumps(mock_response)
            mock_client.chat.completions.create.return_value = mock_response_obj

            response = client.post(
                "/generar-prompt/imagen",
                data={"consulta": "Analiza estos gráficos"},
                files=[
                    ("imagenes", ("uno.jpg", imagen_1, "image/jpeg")),
                    ("imagenes", ("dos.png", imagen_2, "image/png")),
                ],
            )

        assert response.status_code == 200
        assert response.json()["tema"] == "Probabilidad"
        call_args = mock_client.chat.completions.create.call_args
        content = call_args.kwargs["messages"][1]["content"]
        assert len(content) == 3
        assert any(item.get("type") == "image_url" for item in content)

    def test_generar_prompt_imagen_exitoso(self):
        """Test: endpoint recibe imagen + consulta, devuelve clasificación"""
        mock_response = {
            "tema": "Probabilidad",
            "nivel": "Básico",
            "ia_recomendada": "Claude",
            "justificacion": "Para análisis visual de gráficos",
            "prompt_optimizado": "Analiza este gráfico de probabilidad"
        }

        imagen = crear_imagen_test()
        
        with patch("app.services.clasificador.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            
            # Mock de la respuesta de Groq
            mock_response_obj = MagicMock()
            mock_response_obj.choices[0].message.content = json.dumps(mock_response)
            mock_client.chat.completions.create.return_value = mock_response_obj
            
            # Hacer request
            response = client.post(
                "/generar-prompt/imagen",
                data={"consulta": "Analiza este gráfico"},
                files={"imagen": ("test.jpg", imagen, "image/jpeg")}
            )
        
        assert response.status_code == 200
        resultado = response.json()
        assert resultado["tema"] == "Probabilidad"
        assert resultado["nivel"] == "Básico"
        assert mock_client.chat.completions.create.called

    def test_generar_prompt_imagen_consulta_vacia(self):
        """Test: rechaza si la consulta está vacía"""
        imagen = crear_imagen_test()
        
        response = client.post(
            "/generar-prompt/imagen",
            data={"consulta": "   "},  # solo espacios
            files={"imagen": ("test.jpg", imagen, "image/jpeg")}
        )
        
        assert response.status_code == 400
        assert "consulta no puede estar vacía" in response.json()["detail"]

    def test_generar_prompt_imagen_archivo_invalido(self):
        """Test: rechaza si el archivo no es una imagen válida"""
        archivo_fake = BytesIO(b"esto no es una imagen")
        
        response = client.post(
            "/generar-prompt/imagen",
            data={"consulta": "Analiza esto"},
            files={"imagen": ("fake.jpg", archivo_fake, "image/jpeg")}
        )
        
    def test_generar_prompt_imagen_tipo_mime_no_soportado(self):
        """Test: rechaza tipos MIME que no son imagen"""
        fake_file = BytesIO(b"fake content")
        
        response = client.post(
            "/generar-prompt/imagen",
            data={"consulta": "Analiza"},
            files={"imagen": ("fake.pdf", fake_file, "application/pdf")}
        )
        
        assert response.status_code == 400
        assert "no soportado" in response.json()["detail"].lower()

    def test_generar_prompt_imagen_error_groq(self):
        """Test: maneja errores del API de Groq"""
        imagen = crear_imagen_test()
        
        with patch("app.services.clasificador.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            
            # Simular JSON inválido
            mock_response_obj = MagicMock()
            mock_response_obj.choices[0].message.content = "esto no es json válido"
            mock_client.chat.completions.create.return_value = mock_response_obj
            
            response = client.post(
                "/generar-prompt/imagen",
                data={"consulta": "Analiza"},
                files={"imagen": ("test.jpg", imagen, "image/jpeg")}
            )
        
        assert response.status_code == 502
        assert "JSON válido" in response.json()["detail"]

    def test_generar_prompt_imagen_png(self):
        """Test: soporta múltiples formatos de imagen (PNG)"""
        mock_response = {
            "tema": "Estadística",
            "nivel": "Avanzado",
            "ia_recomendada": "GPT",
            "justificacion": "Análisis complejo",
            "prompt_optimizado": "Explora estadísticas"
        }

        imagen_png = crear_imagen_test("PNG")
        
        with patch("app.services.clasificador.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            
            mock_response_obj = MagicMock()
            mock_response_obj.choices[0].message.content = json.dumps(mock_response)
            mock_client.chat.completions.create.return_value = mock_response_obj
            
            response = client.post(
                "/generar-prompt/imagen",
                data={"consulta": "Analiza este gráfico PNG"},
                files={"imagen": ("test.png", imagen_png, "image/png")}
            )
        
        assert response.status_code == 200
        assert response.json()["nivel"] == "Avanzado"


class TestClasificadorConImagen:
    """Tests unitarios para la función clasificar_consulta_con_imagen"""

    def test_clasificar_consulta_con_imagen_retorna_dict(self):
        """Test: la función devuelve un diccionario válido"""
        from app.services.clasificador import clasificar_consulta_con_imagen
        
        mock_response = {
            "tema": "Gráficos",
            "nivel": "Intermedio",
            "ia_recomendada": "Claude",
            "justificacion": "Bueno para OCR",
            "prompt_optimizado": "Describe el gráfico"
        }
        
        with patch("app.services.clasificador.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            
            mock_response_obj = MagicMock()
            mock_response_obj.choices[0].message.content = json.dumps(mock_response)
            mock_client.chat.completions.create.return_value = mock_response_obj
            
            resultado = clasificar_consulta_con_imagen(
                "¿Qué muestra?",
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                "image/png"
            )
        
        assert isinstance(resultado, dict)
        assert resultado["tema"] == "Gráficos"
        assert "prompt_optimizado" in resultado

    def test_clasificar_consulta_con_imagen_usa_modelo_vision(self):
        """Test: usa el modelo de visión (qwen) no el de texto"""
        from app.services.clasificador import clasificar_consulta_con_imagen, MODEL_VISION
        
        with patch("app.services.clasificador.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            
            mock_response_obj = MagicMock()
            mock_response_obj.choices[0].message.content = json.dumps({
                "tema": "Test",
                "nivel": "Test",
                "ia_recomendada": "Test",
                "justificacion": "Test",
                "prompt_optimizado": "Test"
            })
            mock_client.chat.completions.create.return_value = mock_response_obj
            
            clasificar_consulta_con_imagen("consulta", "base64imagen", "image/jpeg")
            
            # Verificar que se llamó con el modelo correcto
            call_args = mock_client.chat.completions.create.call_args
            assert call_args.kwargs["model"] == MODEL_VISION

    def test_clasificar_consulta_con_imagen_json_invalido_lanza_error(self):
        """Test: lanza ValueError si el JSON es inválido"""
        from app.services.clasificador import clasificar_consulta_con_imagen
        
        with patch("app.services.clasificador.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            
            mock_response_obj = MagicMock()
            mock_response_obj.choices[0].message.content = "no json"
            mock_client.chat.completions.create.return_value = mock_response_obj
            
            with pytest.raises(ValueError, match="JSON válido"):
                clasificar_consulta_con_imagen("consulta", "base64", "image/jpeg")
