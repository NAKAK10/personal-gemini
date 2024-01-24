from googleapiclient.discovery import build
import json

import utils
from config import GOOGLE_CSE_ID, GOOGLE_API_KEY


def get_default_serch(title: str) -> str:
    utils.gray_log(f"「{title}」でgoogle検索を開始...")
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    cse = service.cse()
    res = cse.list(q=title, cx=GOOGLE_CSE_ID, num=10).execute()
    results = res.get("items", [])
    snippets = []
    if len(results) == 0:
        return "No good Google Search Result was found"
    for result in results:
        if "snippet" in result:
            add_dist = {}
            add_dist['link'] = result.get('link', '')
            add_dist['snippet'] = result.get('snippet', '')
            add_dist['title'] = result.get('title', '')
            json_str = json.dumps(add_dist, ensure_ascii=False)
            snippets.append(json_str)
    return " ".join(snippets)
