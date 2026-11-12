"""Report a stale ModelRig release without changing public claims or status."""

import argparse
import json
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen


MARKER = "<!-- kaliv-release-drift -->"
ROOT = Path(__file__).resolve().parent.parent


def api(method, path, payload=None):
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "Kaliv-release-check"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = Request("https://api.github.com" + path, data=data, headers=headers, method=method)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def issue_for(project, release):
    tag = release["tag_name"]
    if release.get("draft") or release.get("prerelease") or not re.fullmatch(r"v?\d+\.\d+\.\d+", tag):
        raise ValueError("Expected a public, stable x.y.z ModelRig release")
    current = project["latest_release"]["version"]
    if tag.removeprefix("v") == current:
        return None
    return {
        "title": f"kaliv.dk: gennemgå ModelRig {tag} (sitet viser v{current})",
        "body": f"""{MARKER}
ModelRig har en anden offentlig release end den, der er gennemgået til kaliv.dk.

| Kilde | Version |
|---|---|
| `project.json` → `latest_release.version` | v{current} |
| [ModelRig releases/latest](https://github.com/Ternedal/ModelRig/releases/latest) | {tag} |

Udgivet: `{release['published_at']}`. Kilde: [GitHub API](https://api.github.com/repos/Ternedal/ModelRig/releases/latest).

Gennemgå releasen og opdatér `project.json` i en PR efter planen i #6. Behold historiske testdatoer og bevisstatus, medmindre der er ny evidens. Indholdsgodkendelse følger samme arbejdsgang som andre produktpåstande.

Dette tjek ændrer ikke hjemmesidens indhold. Luk opgaven, når afvigelsen er afklaret.
""",
    }


def report_issue(call, repository, issue, write=False):
    if issue is None:
        return {"action": "current"}
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
        raise ValueError("Expected owner/repository")
    for page in range(1, 101):
        candidates = call("GET", f"/repos/{repository}/issues?state=open&per_page=100&page={page}")
        for existing in candidates:
            if ("pull_request" not in existing and existing.get("user", {}).get("login") == "github-actions[bot]"
                    and MARKER in (existing.get("body") or "")):
                if existing["title"] == issue["title"] and existing["body"] == issue["body"]:
                    return {"action": "existing", "number": existing["number"]}
                if write:
                    call("PATCH", f"/repos/{repository}/issues/{existing['number']}", issue)
                return {"action": "updated" if write else "would-update", "number": existing["number"]}
        if len(candidates) < 100:
            break
    else:
        raise ValueError("Open issue pagination exceeded limit; refusing a duplicate report")
    if not write:
        return {"action": "would-create", "title": issue["title"]}
    created = call("POST", f"/repos/{repository}/issues", issue)
    return {"action": "created", "number": created["number"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Create/update the bot's release-drift issue")
    args = parser.parse_args()
    project = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
    release = api("GET", "/repos/Ternedal/ModelRig/releases/latest")
    issue = issue_for(project, release)
    if args.write and not os.environ.get("GITHUB_TOKEN"):
        parser.error("--write requires GITHUB_TOKEN")
    result = report_issue(api, os.environ.get("GITHUB_REPOSITORY", "Ternedal/Kaliv"), issue, write=args.write)
    print(json.dumps({"recorded": project["latest_release"]["version"], "latest": release["tag_name"], **result}))


if __name__ == "__main__":
    main()
