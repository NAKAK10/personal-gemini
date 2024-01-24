import requests
import dataclasses

import utils
from config import NOTION_API_KEY


@dataclasses.dataclass
class NotionPageDict:
    title: str
    pageId: str
    content: str
    url: str


@dataclasses.dataclass
class NotionSearch:
    result: list[NotionPageDict]
    has_more: bool
    next_cursor: str

    def to_dict(self):
        return {
            "result": [r.__dict__ for r in self.result],
            "has_more": self.has_more,
            "next_cursor": self.next_cursor
        }


class Notion:
    def __init__(self):
        self.headers = {
            'Notion-Version': '2022-06-28',
            'Authorization': 'Bearer ' + NOTION_API_KEY,
            'Content-Type': 'application/json',
        }

    def search(self, query: str, start_cursor="", page_size=10, add_contests=True) -> NotionSearch:
        """
        Params
        ---
        query: str
            検索クエリ
        page_size: int
            取得件数
        add_contests: bool
            ページの本文を取得するかどうか

        Returns
        ---
        res: dict
            検索結果
        """
        utils.gray_log(f"「{query}」でNotion内検索...")

        request_json = {
            "query": query,
            "page_size": page_size,
        }
        if start_cursor:
            request_json["start_cursor"] = start_cursor

        response = requests.post(
            "https://api.notion.com/v1/search",
            headers=self.headers,
            json=request_json
        )
        response = response.json()

        result = response.get('results', [])

        res_list = []
        for r in result:
            if r["object"] == "page":
                if r["properties"].get("title"):
                    tmp_title = ''
                    for t in r["properties"]["title"]["title"]:
                        tmp_title += t["plain_text"]

                    tmp_content = ""
                    if add_contests:
                        tmp_content = self.get_page_contents(page_id=r["id"])

                    res_list.append(
                        NotionPageDict
                        (
                            title=tmp_title,
                            pageId=r["id"],
                            content=tmp_content,
                            url=""
                        )
                    )

                if r["properties"].get("URL"):
                    tmp_title = ''
                    try:
                        for t in r["properties"]["名前"]["title"]:
                            tmp_title += t["plain_text"]
                    except Exception:
                        continue
                    res_list.append(
                        NotionPageDict
                        (
                            title=tmp_title,
                            pageId=r["id"],
                            content="",
                            url=r["properties"]["URL"]["url"]
                        )
                    )

        return NotionSearch(
            result=res_list,
            has_more=response["has_more"],
            next_cursor=response.get("next_cursor", "")
        )

    def get_page_contents(self, page_id: str) -> dict:
        if not page_id:
            return NotionSearch(
                result=[],
                has_more=False,
                next_cursor=""
            )
        response = requests.get(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=self.headers,
        )
        if response.status_code != 200:
            return NotionSearch(
                result=[],
                has_more=False,
                next_cursor=""
            )

        response = response.json()

        result = response["results"]

        res_text = ""

        for r in result:
            text_type = r["type"]
            rich_texts = r.get(text_type).get("rich_text", [])
            for rich_text in rich_texts:
                res_text += rich_text["plain_text"] + "\n"

        return res_text
