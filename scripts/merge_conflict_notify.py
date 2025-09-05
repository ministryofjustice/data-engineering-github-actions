import logging
import os
from typing import Annotated

from slack_sdk.errors import SlackApiError
from slack_sdk.webhook import WebhookClient
from typer import Argument, Typer

logger = logging.getLogger(__name__)
app = Typer()

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

webhook = WebhookClient(SLACK_WEBHOOK_URL)


def merge_conflict(
    ref_name: str,
    workflow_name: str,
    run_link: str,
) -> None:
    """Post message about merge conflict."""
    branch_name = ref_name.split("/")[-1]
    try:
        response = webhook.send(
            text="Workflow Failure",
            blocks=[
                {
                    "text": {
                        "type": "mrkdwn",
                        "text": ":alert: :wave: Hi there! <!channel>",
                    },
                    "type": "section",
                },
                {
                    "text": {
                        "type": "mrkdwn",
                        "text": f"The workflow {workflow_name} in airflow-load-em-data has failed.",
                    },
                    "type": "section",
                },
                {
                    "text": {
                        "type": "mrkdwn",
                        "text": f"The workflow attempted to merge main with {branch_name} "
                        f"and has failed. Check {run_link} to fix.",
                    },
                    "type": "section",
                },
            ],
        )
        logger.info(response)

    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        error_message = e.response["error"]
        logger.error(error_message)
        raise error_message from SlackApiError


@app.command()
def update_slack(
    workflow_name: Annotated[str, Argument()],
    ref_name: Annotated[str | None, Argument()] = None,
    run_link: Annotated[str | None, Argument()] = None,
) -> None:
    merge_conflict(workflow_name=workflow_name, ref_name=ref_name, run_link=run_link)


if __name__ == "__main__":
    app()
