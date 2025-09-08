import datetime
import json
import logging
import os
from pathlib import Path

import humanize
from slack_sdk.errors import SlackApiError
from slack_sdk.webhook import WebhookClient
from typer import Typer

logger = logging.getLogger(__name__)
app = Typer()

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
REPO_NAME = os.environ["REPO_NAME"]

webhook = WebhookClient(SLACK_WEBHOOK_URL)
now = datetime.datetime.now()


def parse_prs(
    file_path: str = "prs.json",
):
    file = Path(file_path)
    prs = json.loads(file.read_text())
    for pr in prs:
        pr_open_date = datetime.datetime.strptime(pr["createdAt"], "%Y-%m-%dT%H:%M:%SZ")
        open_for = pr_open_date - now
        pr["openFor"] = humanize.naturaldelta(open_for)
    return prs


def open_prs(
    prs: list[dict],
    repo: str = REPO_NAME,
) -> None:
    """Post message about open prs."""
    blocks = [
        {
            "text": {
                "type": "mrkdwn",
                "text": f":alert: :wave: Hi there! <!channel> Today's Open PRs in {repo}:",
            },
            "type": "section",
        },
    ]
    for pr in prs:
        new_block = {
            "text": {
                "type": "mrkdwn",
                "text": f"<{pr['url']}|{pr['title']}> \n Been open for {pr['openFor']}",
            },
            "type": "section",
        }
        blocks.append(new_block)
    try:
        response = webhook.send(
            text="Open PRs",
            blocks=blocks,
        )
        logger.info(response)

    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        error_message = e.response["error"]
        logger.error(error_message)
        raise


@app.command()
def open_prs_slack() -> None:
    prs = parse_prs("prs.json")
    open_prs(prs)


if __name__ == "__main__":
    app()
