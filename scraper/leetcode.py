#!/usr/bin/env python3
import uuid
import requests

def fetch_leetcode_company(slug: str):
    session = requests.Session()

    # 1) First GET to seed cookies + csrftoken
    ua = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    )
    get_headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Referer": "https://leetcode.com/discuss/",          # spoof coming from discuss listing
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }
    homepage = session.get("https://leetcode.com/", headers=get_headers, timeout=10)
    if homepage.status_code != 200:
        raise RuntimeError(f"Failed to load homepage: {homepage.status_code}")

    csrftoken = session.cookies.get("csrftoken")
    if not csrftoken:
        raise RuntimeError("Could not find 'csrftoken' in cookies")

    # 2) Prepare GraphQL query
    graphql_query = {
        "query": """
          query getCompanyTagData($slug: String!) {
            companyTag(titleSlug: $slug) {
              name
              problems { difficulty }
            }
          }
        """,
        "variables": {"slug": slug},
        "operationName": "getCompanyTagData",
    }

    # 3) POST to /graphql/ with full set of curl-like headers
    post_headers = {
        "User-Agent": ua,
        "Accept": "*/*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Referer": f"https://leetcode.com/company/{slug}/",
        "Origin": "https://leetcode.com",
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-CH-UA": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"macOS"',
        "Priority": "u=1, i",
        "Random-UUID": str(uuid.uuid4()),
        # "Authorization": "",          # no token needed here
        # "Baggage": "...",             # optional, can omit
        # "Sentry-Trace": "...",        # optional
    }

    resp = session.post(
        "https://leetcode.com/graphql/",
        json=graphql_query,
        headers=post_headers,
        timeout=10,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"GraphQL request failed: {resp.status_code} / {resp.text[:200]}")

    data = resp.json()
    if data.get("errors"):
        raise RuntimeError(f"GraphQL errors: {data['errors']}")

    company = data["data"]["companyTag"]
    if not company:
        raise RuntimeError(f"No data returned for slug '{slug}'")

    return company["name"], company["problems"]


if __name__ == "__main__":
    try:
        name, problems = fetch_leetcode_company("amazon")
        print(f"Company name: {name}")
        print(f"Fetched {len(problems)} problems")
    except Exception as e:
        print("ERROR:", e)
