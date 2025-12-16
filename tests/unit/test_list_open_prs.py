"""Test list open prs functions."""
import datetime
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from slack_sdk.errors import SlackApiError


class FakeResponse:
    """Fake bad response for the open prs."""

    def __getitem__(self, key: str) -> str:
        """Return error."""
        return {"error": "invalid_auth"}[key]


@pytest.fixture
def fake_prs_file(tmp_path: Path) -> tuple[Path, dict[any, str]]:
    """Fake files for open PRs."""
    created_at = (datetime.datetime(2025, 9, 3, 12, 0, 0, tzinfo=datetime.UTC)).strftime("%Y-%m-%dT%H:%M:%SZ")
    prs_data = [
        {
            "title": "Fix bug",
            "url": "https://github.com/org/repo/pull/123",
            "createdAt": created_at,
        }
    ]
    prs_path = tmp_path / "prs.json"
    prs_path.write_text(json.dumps(prs_data))
    return prs_path, prs_data


@pytest.fixture
def _fake_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock env vars."""
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.fake/test123")
    monkeypatch.setenv("REPO_NAME", "fake-repo")


@pytest.mark.usefixtures("_fake_env")
def test_parse_prs(monkeypatch: pytest.MonkeyPatch, fake_prs_file: Path) -> None:
    """Test parse PRs function."""
    import scripts.list_open_prs as lop

    monkeypatch.setattr(lop, "now", datetime.datetime(2025, 9, 5, 12, 0, 0, tzinfo=datetime.UTC))

    monkeypatch.setattr(lop.humanize, "naturaldelta", lambda _td: "2 days")

    prs_path, _ = fake_prs_file
    result = lop.parse_prs(str(prs_path))

    assert result[0]["openFor"] == "2 days"
    assert "title" in result[0]


@pytest.mark.usefixtures("_fake_env")
def test_open_prs_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test succesful post of PR message to slack."""
    import scripts.list_open_prs as lop

    def mock_send(**_kwargs: object) -> SimpleNamespace:
        """Mock send message."""
        return SimpleNamespace(status_code=200, body="ok")
    monkeypatch.setattr(lop.webhook, "send", mock_send)

    prs = [
        {
            "title": "Improve docs",
            "url": "https://github.com/org/repo/pull/456",
            "openFor": "5 days",
        }
    ]

    lop.open_prs(prs)


@pytest.mark.usefixtures("_fake_env")
def test_open_prs_failure(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    """Test failure to post a PR message."""
    import scripts.list_open_prs as lop

    fake_error = SlackApiError("Slack API error", response=FakeResponse())

    monkeypatch.setattr(lop.webhook, "send", lambda **_kwargs: (_ for _ in ()).throw(fake_error))

    prs = [
        {
            "title": "Broken PR",
            "url": "https://github.com/org/repo/pull/789",
            "openFor": "1 week",
        }
    ]

    with caplog.at_level("ERROR"), pytest.raises(SlackApiError):
        lop.open_prs(prs)

    assert "invalid_auth" in caplog.text
