"""Helpers for converting git remote URLs into browsable web URLs."""

import re

# Any scheme://... prefix (e.g. https://, ssh://, file://, git://).
_SCHEME_RE = re.compile(r"^(?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*)://")

# https://host/path(.git)? or http://host/path(.git)?
_HTTP_URL_RE = re.compile(r"^(?P<scheme>https?)://(?P<rest>.+)$")

# ssh://[user@]host[:port]/path(.git)?
_SSH_SCHEME_URL_RE = re.compile(
    r"^ssh://(?:[^@/]+@)?(?P<host>[^:/]+)(?::\d+)?/(?P<path>.+)$"
)

# scp-like syntax: [user@]host:path(.git)? (e.g. git@gitlab.com:user/repo.git)
_SCP_LIKE_URL_RE = re.compile(r"^(?:[^@/]+@)?(?P<host>[^:/]+):(?P<path>.+)$")


def _strip_git_suffix(path: str) -> str:
    path = path.rstrip("/")
    return path.removesuffix(".git")


def to_web_url(remote_url: str) -> str | None:
    """Convert a git remote URL into a browsable web URL.

    Handles the common git remote URL forms:
      - https://host/path(.git)?      -> used as-is, minus .git suffix
      - http://host/path(.git)?       -> used as-is, minus .git suffix
        (not force-upgraded to https, in case of internal instances
        without TLS)
      - ssh://[user@]host[:port]/path(.git)? -> https://host/path
      - scp-like [user@]host:path(.git)?     -> https://host/path

    Anything else — local filesystem paths (absolute, relative, or
    `file://` URLs) and unsupported schemes (e.g. `git://`) — returns
    None, since there's no meaningful web page to open.

    Args:
        remote_url: A git remote URL, as returned by `git remote get-url`.

    Returns:
        A browsable web URL, or None if the input isn't a recognized
        remote URL form.
    """
    remote_url = remote_url.strip()
    if not remote_url:
        return None

    http_match = _HTTP_URL_RE.match(remote_url)
    if http_match:
        scheme = http_match.group("scheme")
        rest = _strip_git_suffix(http_match.group("rest"))
        return f"{scheme}://{rest}"

    ssh_match = _SSH_SCHEME_URL_RE.match(remote_url)
    if ssh_match:
        host = ssh_match.group("host")
        path = _strip_git_suffix(ssh_match.group("path"))
        return f"https://{host}/{path}"

    # Any other explicit scheme (file://, git://, etc.) isn't a supported
    # remote form — bail out before the scp-like check below, which would
    # otherwise misinterpret e.g. "file:///path/to/repo" as an scp-like
    # remote with host "file".
    if _SCHEME_RE.match(remote_url):
        return None

    scp_match = _SCP_LIKE_URL_RE.match(remote_url)
    if scp_match:
        host = scp_match.group("host")
        path = scp_match.group("path")
        # Guard against Windows-style local paths (e.g. "C:\Users\me\repo")
        # being misread as scp-like remotes.
        if "\\" in path:
            return None
        return f"https://{host}/{_strip_git_suffix(path)}"

    return None
