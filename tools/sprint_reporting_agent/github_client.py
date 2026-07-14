"""Shared GitHub Projects v2 GraphQL client for the sprint reporting agent."""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

GRAPHQL_URL = "https://api.github.com/graphql"

PROJECT_ITEMS_QUERY = """
query($login: String!, $number: Int!, $after: String) {
  user(login: $login) {
    projectV2(number: $number) {
      title
      items(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          content {
            ... on Issue {
              number
              title
              url
              createdAt
              closedAt
              repository { name owner { login } }
              assignees(first: 10) { nodes { login } }
              labels(first: 10) { nodes { name } }
            }
          }
          status: fieldValueByName(name: "Status") {
            ... on ProjectV2ItemFieldSingleSelectValue {
              name
              updatedAt
              creator { login }
            }
          }
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field { ... on ProjectV2FieldCommon { name } }
              }
              ... on ProjectV2ItemFieldNumberValue {
                number
                field { ... on ProjectV2FieldCommon { name } }
              }
              ... on ProjectV2ItemFieldTextValue {
                text
                field { ... on ProjectV2FieldCommon { name } }
              }
            }
          }
        }
      }
    }
  }
}
"""

# These are handled separately (Status via the aliased query above) or aren't
# custom fields users add - skip them when collecting "extra" custom fields
# like Priority/Size/Estimate.
_SKIP_FIELD_NAMES = {"Status", "Title", "Assignees", "Labels", "Linked pull requests", "Repository"}


def _parse_extra_fields(field_value_nodes):
    fields = {}
    for node in field_value_nodes:
        field_info = node.get("field") or {}
        field_name = field_info.get("name")
        if not field_name or field_name in _SKIP_FIELD_NAMES:
            continue
        if "number" in node:
            fields[field_name] = node["number"]
        elif "text" in node:
            fields[field_name] = node["text"]
        elif "name" in node:
            fields[field_name] = node["name"]
    return fields


def load_config():
    token = os.environ.get("GITHUB_TOKEN")
    owner = os.environ.get("GITHUB_PROJECT_OWNER")
    number = os.environ.get("GITHUB_PROJECT_NUMBER")
    missing = [
        name
        for name, val in (
            ("GITHUB_TOKEN", token),
            ("GITHUB_PROJECT_OWNER", owner),
            ("GITHUB_PROJECT_NUMBER", number),
        )
        if not val
    ]
    if missing:
        print(f"Missing required .env values: {', '.join(missing)}", file=sys.stderr)
        print("Copy .env.example to .env and fill it in first.", file=sys.stderr)
        sys.exit(1)
    return token, owner, int(number)


def fetch_project_items(token, owner, number):
    """Returns {item_id: {number, title, url, created_at, closed_at, status,
    status_updated_at, status_changed_by, assignees, labels, fields}}.
    `fields` holds whatever other custom project fields exist (e.g.
    Priority, Size, Estimate), keyed by field name.

    status_updated_at / status_changed_by come straight from GitHub (the
    Status field value's own updatedAt/creator) - real attribution and a
    precise timestamp for whoever most recently set the current status,
    with no dependency on the poller having been running.
    """
    headers = {"Authorization": f"Bearer {token}"}
    items = {}
    after = None
    while True:
        resp = requests.post(
            GRAPHQL_URL,
            json={"query": PROJECT_ITEMS_QUERY, "variables": {"login": owner, "number": number, "after": after}},
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()
        if "errors" in payload:
            raise RuntimeError(f"GitHub GraphQL error: {payload['errors']}")
        project = payload["data"]["user"]["projectV2"]
        if project is None:
            raise RuntimeError(f"No project number {number} found for user {owner}")
        block = project["items"]
        for node in block["nodes"]:
            content = node.get("content") or {}
            status_field = node.get("status") or {}
            assignees = [a["login"] for a in (content.get("assignees") or {}).get("nodes", [])]
            labels = [l["name"] for l in (content.get("labels") or {}).get("nodes", [])]
            extra_fields = _parse_extra_fields((node.get("fieldValues") or {}).get("nodes", []))
            repo_info = content.get("repository") or {}
            items[node["id"]] = {
                "number": content.get("number"),
                "title": content.get("title", "(unknown)"),
                "url": content.get("url"),
                "created_at": content.get("createdAt"),
                "closed_at": content.get("closedAt"),
                "status": status_field.get("name", "(no status)"),
                "status_updated_at": status_field.get("updatedAt"),
                "status_changed_by": (status_field.get("creator") or {}).get("login"),
                "assignees": assignees,
                "labels": labels,
                "fields": extra_fields,
                "repo_owner": (repo_info.get("owner") or {}).get("login"),
                "repo_name": repo_info.get("name"),
            }
        if block["pageInfo"]["hasNextPage"]:
            after = block["pageInfo"]["endCursor"]
        else:
            break
    return items


STATUS_HISTORY_QUERY = """
query($owner: String!, $repo: String!, $issueNumber: Int!) {
  repository(owner: $owner, name: $repo) {
    issue(number: $issueNumber) {
      timelineItems(first: 100, itemTypes: [PROJECT_V2_ITEM_STATUS_CHANGED_EVENT]) {
        nodes {
          ... on ProjectV2ItemStatusChangedEvent {
            createdAt
            previousStatus
            status
            wasAutomated
            actor { login }
          }
        }
      }
    }
  }
}
"""


def fetch_status_history(token, owner, repo, issue_number):
    """The REAL, complete status-change history for one issue - straight
    from GitHub's timeline (ProjectV2ItemStatusChangedEvent), including the
    actual GitHub user who made each change. This is authoritative and
    retroactive: it does not depend on sprint_poller.py having been running.

    Returns a list of {from_status, to_status, changed_by, changed_at,
    automated}, oldest first.
    """
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(
        GRAPHQL_URL,
        json={"query": STATUS_HISTORY_QUERY,
              "variables": {"owner": owner, "repo": repo, "issueNumber": issue_number}},
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json()
    if "errors" in payload:
        raise RuntimeError(f"GitHub GraphQL error: {payload['errors']}")
    issue = (payload["data"].get("repository") or {}).get("issue")
    if not issue:
        return []
    history = []
    for node in issue["timelineItems"]["nodes"]:
        history.append({
            "from_status": node.get("previousStatus") or "(new)",
            "to_status": node.get("status"),
            "changed_by": (node.get("actor") or {}).get("login"),
            "changed_at": node.get("createdAt"),
            "automated": node.get("wasAutomated", False),
        })
    return history
