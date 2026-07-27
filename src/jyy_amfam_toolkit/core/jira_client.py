"""Thin httpx-based client for the Jira Cloud REST API (v3).

Only implements what this toolkit currently needs: searching issues via
JQL. Kept intentionally small and explicit rather than pulling in a
general-purpose Jira SDK.
"""

from dataclasses import dataclass

import httpx

from jyy_amfam_toolkit.constants import JIRA_REQUEST_TIMEOUT_SECONDS, JIRA_SEARCH_PATH
from jyy_amfam_toolkit.settings import Settings


@dataclass(frozen=True)
class Issue:
    """A minimal representation of a Jira issue."""

    key: str
    summary: str
    status: str


class JiraClient:
    """Client for querying Jira Cloud issues."""

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.jira_url.rstrip("/")
        self._auth = (settings.jira_email, settings.jira_api_token)

    def search_issues(self, jql: str, max_results: int = 50) -> list[Issue]:
        """Search issues matching a JQL query, handling pagination.

        Args:
            jql: The JQL query string.
            max_results: Maximum number of issues to return in total.

        Returns:
            A list of Issue objects matching the query.

        Raises:
            httpx.HTTPStatusError: If the Jira API returns an error status.
        """
        issues: list[Issue] = []
        next_page_token: str | None = None

        with httpx.Client(
            auth=self._auth, timeout=JIRA_REQUEST_TIMEOUT_SECONDS
        ) as client:
            while len(issues) < max_results:
                page_size = min(50, max_results - len(issues))
                params: dict[str, str | int] = {
                    "jql": jql,
                    "maxResults": page_size,
                    "fields": "summary,status",
                }
                if next_page_token:
                    params["nextPageToken"] = next_page_token

                response = client.get(
                    f"{self._base_url}{JIRA_SEARCH_PATH}", params=params
                )
                response.raise_for_status()
                data = response.json()

                for raw_issue in data.get("issues", []):
                    fields = raw_issue.get("fields", {})
                    issues.append(
                        Issue(
                            key=raw_issue["key"],
                            summary=fields.get("summary", ""),
                            status=fields.get("status", {}).get("name", ""),
                        )
                    )

                next_page_token = data.get("nextPageToken")
                if not next_page_token or data.get("isLast", True):
                    break

        return issues
