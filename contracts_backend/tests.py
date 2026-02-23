"""Tests for contracts_backend.utils module (ImageProcessor, Base64ImageField, etc.)."""
import base64
import binascii
from io import BytesIO
from unittest.mock import patch

import pytest
from PIL import Image
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import (
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
)
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from .utils import (
    ImageProcessor,
    Base64ImageField,
    api_exception_handler,
    CustomPagination,
)


@pytest.mark.django_db
class TestImageProcessor:
    def test_load_image_from_io(self):
        img = Image.new("RGB", (100, 100), color="red")
        bytes_io = BytesIO()
        img.save(bytes_io, format="PNG")
        bytes_io.seek(0)

        result = ImageProcessor.load_image_from_io(bytes_io)

        assert result is not None
        assert result.shape == (100, 100, 3)

    def test_from_img_to_io(self):
        import numpy as np

        image_array = np.zeros((100, 100, 3), dtype=np.uint8)
        image_array[:, :] = [255, 0, 0]  # Red image

        result = ImageProcessor.from_img_to_io(image_array, "PNG")

        assert isinstance(result, BytesIO)
        result.seek(0)
        img = Image.open(result)
        assert img.size == (100, 100)
        assert img.format == "PNG"

    def test_data_url_to_uploaded_file_with_header(self):
        img = Image.new("RGB", (10, 10), color="blue")
        bytes_io = BytesIO()
        img.save(bytes_io, format="PNG")
        bytes_io.seek(0)
        encoded = base64.b64encode(bytes_io.read()).decode("utf-8")
        data_url = f"data:image/png;base64,{encoded}"

        result = ImageProcessor.data_url_to_uploaded_file(data_url)

        assert result is not None
        assert isinstance(result, ContentFile)
        assert result.name.endswith(".png")

    def test_data_url_to_uploaded_file_without_header(self):
        img = Image.new("RGB", (10, 10), color="green")
        bytes_io = BytesIO()
        img.save(bytes_io, format="JPEG")
        bytes_io.seek(0)
        encoded = base64.b64encode(bytes_io.read()).decode("utf-8")

        result = ImageProcessor.data_url_to_uploaded_file(encoded)

        assert result is not None
        assert isinstance(result, ContentFile)
        assert result.name.endswith(".jpg")

    def test_data_url_to_uploaded_file_invalid_data(self):
        result = ImageProcessor.data_url_to_uploaded_file("invalid_base64!")
        assert result is None

    def test_data_url_to_uploaded_file_non_string(self):
        result = ImageProcessor.data_url_to_uploaded_file(12345)
        assert result is None

    def test_convert_to_webp(self):
        img = Image.new("RGB", (100, 100), color="blue")
        bytes_io = BytesIO()
        img.save(bytes_io, format="PNG")
        bytes_io.seek(0)
        png_data = bytes_io.read()

        result = ImageProcessor.convert_to_webp(png_data)

        assert isinstance(result, ContentFile)

    def test_convert_to_webp_with_bytesio(self):
        img = Image.new("RGB", (50, 50), color="yellow")
        bytes_io = BytesIO()
        img.save(bytes_io, format="JPEG")
        bytes_io.seek(0)

        result = ImageProcessor.convert_to_webp(bytes_io)

        assert isinstance(result, ContentFile)

    def test_convert_to_webp_too_small(self):
        img = Image.new("RGB", (5, 5), color="red")
        bytes_io = BytesIO()
        img.save(bytes_io, format="PNG")
        bytes_io.seek(0)

        with pytest.raises(ValueError, match="too small"):
            ImageProcessor.convert_to_webp(bytes_io)

    def test_convert_to_webp_non_image(self):
        result = ImageProcessor.convert_to_webp(b"not an image")
        assert result is None


class TestBase64ImageField:
    def test_valid_base64_png_string(self):
        img = Image.new("RGB", (10, 10), color="red")
        bytes_io = BytesIO()
        img.save(bytes_io, format="PNG")
        bytes_io.seek(0)
        b64 = base64.b64encode(bytes_io.read()).decode("utf-8")

        field = Base64ImageField()
        # Base64ImageField converts the base64 string to a ContentFile
        result = field.to_internal_value(b64)
        assert hasattr(result, "name")
        assert result.name.endswith(".png")

    def test_data_url_format_base64(self):
        img = Image.new("RGB", (10, 10), color="blue")
        bytes_io = BytesIO()
        img.save(bytes_io, format="JPEG")
        bytes_io.seek(0)
        b64 = base64.b64encode(bytes_io.read()).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{b64}"

        field = Base64ImageField()
        result = field.to_internal_value(data_url)
        assert hasattr(result, "name")

    def test_get_file_extension_jpeg_returns_jpg(self):
        img = Image.new("RGB", (10, 10))
        bytes_io = BytesIO()
        img.save(bytes_io, format="JPEG")
        bytes_io.seek(0)
        decoded = bytes_io.read()

        ext = Base64ImageField.get_file_extension("test", decoded)
        assert ext == "jpg"

    def test_get_file_extension_png_returns_png(self):
        img = Image.new("RGB", (10, 10))
        bytes_io = BytesIO()
        img.save(bytes_io, format="PNG")
        bytes_io.seek(0)
        decoded = bytes_io.read()

        ext = Base64ImageField.get_file_extension("test", decoded)
        assert ext == "png"

    def test_get_file_extension_invalid_returns_jpg(self):
        ext = Base64ImageField.get_file_extension("test", b"not-an-image")
        assert ext == "jpg"


class TestApiExceptionHandler:
    factory = APIRequestFactory()

    def _make_context(self, method="get", path="/test/"):
        request = self.factory.get(path)
        return {"request": Request(request), "view": None}

    def test_not_found_returns_formatted_response(self):
        exc = NotFound("Resource not found")
        context = self._make_context()
        response = api_exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 404
        assert response.data["status_code"] == 404
        assert "Aucune correspondance" in response.data["message"]

    def test_permission_denied_returns_formatted_response(self):
        exc = PermissionDenied("Access denied")
        context = self._make_context()
        response = api_exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 403
        assert response.data["status_code"] == 403
        assert "refusé" in response.data["message"].lower() or "Accès" in response.data["message"]

    def test_authentication_failed_returns_formatted_response(self):
        exc = AuthenticationFailed("Not authenticated")
        context = self._make_context()
        response = api_exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 401
        assert response.data["status_code"] == 401

    def test_validation_error_returns_formatted_response(self):
        exc = ValidationError({"field": ["This field is required."]})
        context = self._make_context()
        response = api_exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 400
        assert response.data["status_code"] == 400

    def test_method_not_allowed_returns_formatted_response(self):
        exc = MethodNotAllowed("POST")
        context = self._make_context()
        response = api_exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 405

    def test_non_api_exception_returns_none(self):
        exc = Exception("Unknown error")
        context = self._make_context()
        response = api_exception_handler(exc, context)
        assert response is None

    def test_throttled_exception_with_french_message(self):
        from rest_framework.exceptions import Throttled

        exc = Throttled(wait=5)
        context = self._make_context()
        response = api_exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 429

    def test_throttled_exception_singular_second(self):
        from rest_framework.exceptions import Throttled

        exc = Throttled(wait=1)
        context = self._make_context()
        response = api_exception_handler(exc, context)

        assert response is not None
        # Message should say "seconde" not "secondes"
        # The detail is set on the exception itself
        assert "seconde" in str(exc.detail)


@pytest.mark.django_db
class TestCustomPagination:
    def test_default_page_size(self):
        paginator = CustomPagination()
        assert paginator.page_size == 10

    def test_max_page_size(self):
        paginator = CustomPagination()
        assert paginator.max_page_size == 100

    def test_page_size_query_param(self):
        paginator = CustomPagination()
        assert paginator.page_size_query_param == "page_size"
