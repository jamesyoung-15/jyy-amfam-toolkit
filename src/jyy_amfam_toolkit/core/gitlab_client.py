"""Thin httpx-based client for the GitLab REST API (v4).

Only implements what this toolkit currently needs: looking up a project,
listing its branches, and creating merge requests. Kept intentionally
small and explicit rather than pulling in a general-purpose GitLab SDK.
"""

from dataclasses import dataclass
from urllib.parse import quote

import httpx

from jyy_amfam_toolkit.constants import (
    GITLAB_API_VERSION_PATH,
    GITLAB_REQUEST_TIMEOUT_SECONDS,
)
from jyy_amfam_toolkit.settings import GitlabSettings


@dataclass(frozen=True)
class Project:
    """A minimal representation of a GitLab project."""

    id: int
    default_branch: str
    web_url: str


@dataclass(frozen=True)
class MergeRequest:
    """A minimal representation of a GitLab merge request."""

    iid: int
    web_url: str


@dataclass(frozen=True)
class MergeRequestSummary:
    """A minimal representation of an existing GitLab merge request."""

    iid: int
    title: str
    target_branch: str
    state: str
    web_url: str


class GitlabClient:
    """Client for GitLab projects, branches, and merge requests."""

    def __init__(self, settings: GitlabSettings) -> None:
        self._base_url = settings.gitlab_url.rstrip("/") + GITLAB_API_VERSION_PATH
        self._headers = {"PRIVATE-TOKEN": settings.gitlab_token}

    def _client(self) -> httpx.Client:
        return httpx.Client(
            headers=self._headers, timeout=GITLAB_REQUEST_TIMEOUT_SECONDS
        )

    def get_project(self, project_path: str) -> Project:
        """Look up a project by its namespaced path (e.g. "group/repo").

        Raises:
            httpx.HTTPStatusError: If the GitLab API returns an error
                status (e.g. 404 if the project doesn't exist or the
                token lacks access).
        """
        encoded_path = quote(project_path, safe="")
        with self._client() as client:
            response = client.get(f"{self._base_url}/projects/{encoded_path}")
            response.raise_for_status()
            data = response.json()

        return Project(
            id=data["id"],
            default_branch=data.get("default_branch", ""),
            web_url=data.get("web_url", ""),
        )

    def list_branches(self, project_id: int) -> list[str]:
        """List all branch names for a project.

        Raises:
            httpx.HTTPStatusError: If the GitLab API returns an error
                status.
        """
        branches: list[str] = []
        page = 1

        with self._client() as client:
            while True:
                response = client.get(
                    f"{self._base_url}/projects/{project_id}/repository/branches",
                    params={"per_page": 100, "page": page},
                )
                response.raise_for_status()
                data = response.json()

                if not data:
                    break

                branches.extend(branch["name"] for branch in data)
                page += 1

        return branches

    def list_merge_requests_for_branch(
        self, project_id: int, source_branch: str
    ) -> list[MergeRequestSummary]:
        """List merge requests with the given source branch.

        Includes merge requests in any state (opened, closed, merged).

        Raises:
            httpx.HTTPStatusError: If the GitLab API returns an error
                status.
        """
        with self._client() as client:
            response = client.get(
                f"{self._base_url}/projects/{project_id}/merge_requests",
                params={"source_branch": source_branch, "state": "all"},
            )
            response.raise_for_status()
            data = response.json()

        return [
            MergeRequestSummary(
                iid=mr["iid"],
                title=mr.get("title", ""),
                target_branch=mr.get("target_branch", ""),
                state=mr.get("state", ""),
                web_url=mr["web_url"],
            )
            for mr in data
        ]

    def create_merge_request(
        self,
        project_id: int,
        source_branch: str,
        target_branch: str,
        title: str,
        description: str = "",
    ) -> MergeRequest:
        """Create a merge request.

        Raises:
            httpx.HTTPStatusError: If the GitLab API returns an error
                status (e.g. 409 if an open MR already exists for this
                source/target pair).
        """
        with self._client() as client:
            response = client.post(
                f"{self._base_url}/projects/{project_id}/merge_requests",
                json={
                    "source_branch": source_branch,
                    "target_branch": target_branch,
                    "title": title,
                    "description": description,
                },
            )
            response.raise_for_status()
            data = response.json()

        return MergeRequest(iid=data["iid"], web_url=data["web_url"])
