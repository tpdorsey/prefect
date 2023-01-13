#!/usr/bin/env python3
"""
This script generates release notes using the GitHub Release API then prints it to
standard output. You must be logged into GitHub using the `gh` CLI tool or provide a
GitHub token via `GITHUB_TOKEN` environment variable.

Usage:

    generate-release-notes.py [<release-tag>] [<target>] [<previous-tag>]

The release tag defaults to `preview` but often should be set to the new version:

    generate-release-notes.py "2.3.0"

The target defaults to `main` but can be set to a different commit or branch:

    generate-release-notes.py "2.3.0" "my-test-branch"

The previous tag defaults to the last tag, but can be set to a different tag to view
release notes for a different release. In this case, the target must be provided too.

    generate-release-notes.py "2.3.3" "main" "2.3.2"
"""
import os
import re
import shutil
import subprocess
import sys

import httpx

REPO_ORG = "PrefectHQ"
REPO_NAME = "prefect"
DEFAULT_TAG = "preview"

TOKEN_REGEX = re.compile(r"Token:\s(.*)")
ENTRY_REGEX = re.compile(r"^\* (.*) by @(.*) in (.*)$", re.MULTILINE)


def generate_release_notes(
    repo_org: str,
    repo_name: str,
    tag_name: str,
    github_token: str,
    target_commit: str,
    previous_tag: str = None,
):
    """
    Generate release notes using the GitHub API.
    """
    request = {"tag_name": tag_name, "target_commitish": target_commit}
    if previous_tag:
        request["previous_tag_name"] = previous_tag

    response = httpx.post(
        f"https://api.github.com/repos/{repo_org}/{repo_name}/releases/generate-notes",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_token}",
        },
        json=request,
    )
    if not response.status_code == 200:
        print(
            "Received status code {response.status_code} from GitHub API:",
            file=sys.stderr,
        )
        print(response.json(), file=sys.stderr)
        exit(1)

    release_notes = response.json()["body"]

    # Drop the generated by section
    release_notes = "\n".join(release_notes.splitlines()[2:])

    # Add newlines before all categories
    release_notes = release_notes.replace("\n###", "\n\n###")

    # Update what's new to release name
    release_notes = release_notes.replace("## What's Changed", f"## Release {tag_name}")

    # Parse all entries
    entries = ENTRY_REGEX.findall(release_notes)

    # Generate a contributors section
    contributors = ""
    for contributor in sorted(set(user for _, user, _ in entries)):
        contributors += f"\n- @{contributor}"

    # Replace the heading of the existing contributors section; append contributors
    release_notes = release_notes.replace(
        "\n**Full Changelog**:",
        "### Contributors" + contributors + "\n\n**All changes**:",
    )

    # Strip contributors from individual entries
    release_notes = ENTRY_REGEX.sub(
        lambda match: f"- {match.group(1)} — {match.group(3)}",
        release_notes,
    )

    print(release_notes)


def get_github_token() -> str:
    """
    Retrieve the current GitHub token from the `gh` CLI.
    """
    if "GITHUB_TOKEN" in os.environ:
        return os.environ["GITHUB_TOKEN"]

    if not shutil.which("gh"):
        print(
            "You must provide a GitHub access token via GITHUB_TOKEN or have the gh CLI"
            " installed."
        )
        exit(1)

    gh_auth_status = subprocess.run(
        ["gh", "auth", "status", "--show-token"], capture_output=True
    )
    output = gh_auth_status.stderr.decode()
    if not gh_auth_status.returncode == 0:
        print(
            "Failed to retrieve authentication status from GitHub CLI:", file=sys.stderr
        )
        print(output, file=sys.stderr)
        exit(1)

    match = TOKEN_REGEX.search(output)
    if not match:
        print(
            "Failed to find token in GitHub CLI output with regex"
            f" {TOKEN_REGEX.pattern!r}:",
            file=sys.stderr,
        )
        print(output, file=sys.stderr)
        exit(1)

    return match.groups()[0]


if __name__ == "__main__":
    generate_release_notes(
        REPO_ORG,
        REPO_NAME,
        tag_name=sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TAG,
        target_commit=sys.argv[2] if len(sys.argv) > 2 else "main",
        previous_tag=sys.argv[3] if len(sys.argv) > 3 else None,
        github_token=get_github_token(),
    )
