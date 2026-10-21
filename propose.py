"""Create a tested update PR using the current repository's Actions token."""

import argparse
import hashlib
import json
import os
import subprocess
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def git(*arguments):
    return subprocess.check_output(["git", *arguments], text=True).strip()


def api(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = Request("https://api.github.com" + path, method=method, data=data, headers={
        "Authorization": "Bearer " + os.environ["GH_TOKEN"],
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Sandfish-SDK-update",
    })
    with urlopen(request, timeout=60) as response:
        content = response.read()
        return json.loads(content) if content else None


def propose(title):
    git("add", ".")
    diff = git("diff", "--cached", "--binary")
    if not diff:
        print("No update is needed.")
        return
    branch = "automation/sdk-" + hashlib.sha256(diff.encode()).hexdigest()[:12]
    repository = os.environ["GITHUB_REPOSITORY"]
    if not git("ls-remote", "--heads", "origin", branch):
        git("switch", "-c", branch)
        git("-c", "user.name=github-actions[bot]", "-c",
            "user.email=41898282+github-actions[bot]@users.noreply.github.com",
            "commit", "-m", title)
        git("push", "origin", branch)
    query = urlencode({"state": "open", "head": repository.split("/")[0] + ":" + branch})
    pull_requests = api("GET", f"/repos/{repository}/pulls?{query}")
    if not pull_requests:
        pull_request = api("POST", f"/repos/{repository}/pulls", {
            "title": title, "head": branch, "base": "main",
            "body": "This update passed the SDK checks in the update workflow. "
                    "Review API and generated method changes before choosing a release version. "
                    "The source manifest records the contract and generator hashes.",
        })
        print(pull_request["html_url"])
    # Token-created PRs do not start normal PR workflows. Explicit dispatch does.
    api("POST", f"/repos/{repository}/actions/workflows/ci.yml/dispatches", {"ref": branch})
    print("Started CI for the update branch.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    propose(parser.parse_args().title)
