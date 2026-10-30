"""Регрессионные тесты URL клиента Remnawave."""

import httpx
import pytest

from shared.remnawave import client as rw


@pytest.mark.parametrize(
    ("base_url", "expected_path"),
    [
        ("https://panel.example.com", "/api/system/metadata"),
        ("https://panel.example.com/api", "/api/system/metadata"),
        (
            "https://panel.example.com/remnawave/api",
            "/remnawave/api/system/metadata",
        ),
    ],
)
async def test_connection_check_handles_api_base_url(
    base_url: str, expected_path: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    requested_paths: list[str] = []
    original_client = rw.httpx.AsyncClient

    def respond(request: httpx.Request) -> httpx.Response:
        requested_paths.append(request.url.path)
        return httpx.Response(200, json={"response": {"version": "3.4.7"}})

    def mock_client(*args, **kwargs) -> httpx.AsyncClient:
        kwargs["transport"] = httpx.MockTransport(respond)
        return original_client(*args, **kwargs)

    monkeypatch.setattr(rw.httpx, "AsyncClient", mock_client)

    async with rw.RemnawaveClient(base_url, "test-token") as client:
        response = await client.check_connection()

    assert response["version"] == "3.4.7"
    assert requested_paths == [expected_path]
