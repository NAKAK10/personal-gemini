import json
from datetime import datetime


def markdown_to_dict(markdown_text: str) -> dict:
    """
    マークダウン文字列からJSON形式の部分を抽出

    呼び出した側でエラーを処理してください
    """
    start_index = markdown_text.find("{")
    if start_index == -1:
        markdown_text = "{" + markdown_text
        start_index = 0

    end_index = markdown_text.rfind("}")
    json_text = markdown_text[start_index:end_index + 1]

    # JSON形式のテキストをPythonの辞書に変換
    json_data = json.loads(json_text)
    return json_data


def get_now_date_at_ISO() -> str:
    """
    Get the current date and time in ISO8601 format
    """
    return datetime.now().isoformat()
