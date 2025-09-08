# test_slack_alert.py
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner


runner = CliRunner()


class FakeWebhookClient:
    def __init__(self):
        self.sent_messages = []

    def send(self, text=None, blocks=None):
        self.sent_messages.append({"text": text, "blocks": blocks})
        return {"ok": True, "message": "sent"}
    
@pytest.fixture
def _fake_env(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.fake/test123")

@pytest.mark.usefixtures("_fake_env")
def test_merge_conflict_sends_correct_message():
    from scripts.merge_conflict_notify import merge_conflict

    fake_webhook = FakeWebhookClient()
    merge_conflict(
        ref_name="refs/heads/feature",
        workflow_name="merge-check",
        run_link="http://eg.com/run/123",
        repo_name="test-repo",
        webhook_client=fake_webhook,
    )

    assert len(fake_webhook.sent_messages) == 1
    message = fake_webhook.sent_messages[0]

    assert message["text"] == "Workflow Failure"
    assert any("merge main with feature" in block["text"]["text"]
               for block in message["blocks"]
               if block["type"] == "section")

@pytest.mark.usefixtures("_fake_env")
def test_cli_invokes_merge_conflict(monkeypatch):
    import scripts.merge_conflict_notify as mcn

    def mock_send(**kwargs):
        return SimpleNamespace(status_code=200, body="ok")

    monkeypatch.setattr(mcn.webhook, "send", mock_send)

    result = runner.invoke(mcn.app, [
        "update-slack",
        "repo_name",
        "refs/heads/test-branch",
        "https://eg.com/run",
    ])
    assert result.exit_code == 0
