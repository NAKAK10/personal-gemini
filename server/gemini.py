"""
Documentaion
https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini?hl=ja#gemini-pro
"""
import json
from google.oauth2 import service_account
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from vertexai.preview import generative_models
from vertexai.generative_models._generative_models import ResponseBlockedError

import utils
from tools import gen_tool_list
from config import PROJECT_ID, REGION, SAFETY_CONFIG

from typing import Tuple, Optional, Callable


credentials = service_account.Credentials.from_service_account_file('./google_key.json')
vertexai.init(project=PROJECT_ID, location=REGION, credentials=credentials)


tools = gen_tool_list()


class GeminiAI():
    def __init__(self, model_name="gemini-pro", max_output_tokens=2048):
        model_name = self._check_model_name(model_name)
        self.model_name = model_name  # gemini-pro, gemini-pro-vision

        self.config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": max_output_tokens,

        }
        _model = GenerativeModel(
            model_name="gemini-pro",
            generation_config=self.config,
            safety_settings=SAFETY_CONFIG,
        )
        self.model = _model.start_chat()
        self.token = {
            "prompt_token_count": 0,
            "total_token_count": 0
        }

    def _check_model_name(self, model_name):
        # gemini-pro, gemini-pro-vision
        if not model_name and self.model_name:
            return self.model_name
        if model_name in ["gemini-pro", "gemini-pro-vision"]:
            return model_name
        raise ValueError("model_name is gemini-pro or gemini-pro-vision")

    def close(self):
        print(self.token)
        pass

    @staticmethod
    def attached_image(image: str, mime_type: Optional[str] = None) -> dict:
        """
        Params
        ---
        image: str
            image path(local path) or base64 or dateURI or URL
            ex: 'https://example.com/image.png'
            ex: 'images/image.png' (local path)
            ex: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...'

        mime_type: Optional[str]
            ※base64の場合は必須
            ex: 'image/png'
            ex: 'image/jpeg'

        Returns
        ---
        res: dict
            ex: {
                'mime_type': 'image/png',
                'data': bytes
            }
        """
        import mimetypes
        import requests
        import base64

        res = {'mime_type': '', 'data': b''}

        if image.startswith(('http://', 'https://')):
            response = requests.get(image)
            response.raise_for_status()
            res['data'] = response.content

        elif image.startswith(('data:image/', 'data:application/')):
            _, data = image.split(',', 1)
            res['data'] = base64.b64decode(data)
            mime_type = image.split(';', 1)[0][5:]
        else:
            try:
                with open(image, 'rb') as file:
                    res['data'] = file.read()
            except FileNotFoundError:
                # If the file is not found, assuming it is a base64 encoded image
                res['data'] = base64.b64decode(image)

        if not mime_type:
            mime_type, _ = mimetypes.guess_type(image)
            if not mime_type:
                raise ValueError(
                    f"Could not determine mime type for image: {image}")

        res['mime_type'] = mime_type
        return res

    def get_anything_chat(
            self,
            q: Tuple[str, list],
            images: list = [],
            is_tool=True,
            model_name="",
            max_tokens: int = 100,
            max_func_num=5,
            f: Optional[Callable] = None
    ) -> str:
        """
        usage
        ---
        >>> from utils.gemini import GenimiAI
        >>> gemini = GenimiAI()
        >>> res = g.get_anything_chat('本日のドル円レートを教えて')
        >>> print(res)

        Params
        ---
        q: Tuple[str, list]
            str: question
            list: question history
        images: list
            image path(local path) or base64 or dateURI or URL
        is_tool: bool
            toolを使用するかどうか
        model_name: str
            ex: gemini-pro, gemini-pro-vision
        max_tokens: int
            一回のリクエストで使用するトークン数
        max_func_num: int
            一回のリクエストで使用するfunctionの数
            ex: 5
        f: Optional[functools]
            ツールを使用する場合は、実行される

        Returns
        ---
        res: str
            ex: 本日のドル円レートは、1ドル=110円です。
        """
        model_name = self._check_model_name(model_name)
        chat = self.model
        if len(images) > 0:
            """
            現在: 2025-01-15
            画像を添付する場合は、gemini-pro-visionを使用し、toolを使用しない
            """

            self.model_name = 'gemini-pro-vision'
            _model = GenerativeModel(
                model_name=self.model_name,
                generation_config=self.config,
                safety_settings=SAFETY_CONFIG,
            )
            chat = _model.start_chat()
            self.model = chat

        elif self.model_name != model_name:
            self.model_name = model_name
            _model = GenerativeModel(
                model_name=self.model_name,
                generation_config=self.config,
                safety_settings=SAFETY_CONFIG,
            )
            chat = _model.start_chat()
            self.model = chat

        is_tool = self.model_name == 'gemini-pro'

        history = q if isinstance(q, list) else [Part.from_text(q)]

        for image in images:
            res_image = self.attached_image(image)
            history.append(Part.from_data(data=res_image['data'], mime_type=res_image['mime_type']))

        response = chat.send_message(
            content=history,
            tools=[tools] if is_tool else None
        )

        if (response.candidates[0].finish_reason == generative_models.FinishReason.SAFETY):
            return '安全な応答が生成されませんでした。'

        usage_metadata = response._raw_response.usage_metadata
        self.token['prompt_token_count'] += usage_metadata.prompt_token_count
        self.token['total_token_count'] += usage_metadata.total_token_count

        parts = response.candidates[0].content.parts

        func_num = 0
        while parts:
            func_res = []
            func_num += 1
            for part in parts:
                if 'text' in str(part):
                    return part.text

                if 'function_call' in str(part):
                    function_name: str = part.function_call.name

                    if function_name == "get_default_serch":
                        if f:
                            f('goole検索を開始')
                        q: str = part.function_call.args['q']
                        search_res = utils.get_default_serch(q)
                        func_res.append(
                            Part.from_function_response(
                                name=function_name,
                                response={"result": True, 'message': search_res}
                            )
                        )

                    if function_name == "get_outer_html":
                        if f:
                            f('スクレイピングを開始')
                        q: str = part.function_call.args['q']
                        html = utils.get_outer_html(url=q)
                        func_res.append(
                            Part.from_function_response(
                                name=function_name,
                                response={
                                    "result": bool(html),
                                    'message': html if html else 'URLが不正 or 取得できませんでした'
                                }
                            )
                        )

                    if function_name == "get_now_date_at_ISO":
                        date = utils.get_now_date_at_ISO()
                        func_res.append(
                            Part.from_function_response(
                                name=function_name,
                                response={"result": True, 'message': date}
                            )
                        )

                    if function_name == "notion_search":
                        if f:
                            f('Notion検索を開始')
                        q: str = part.function_call.args['q']
                        start_cursor: str = part.function_call.args.get('start_cursor', '')
                        n = utils.Notion()
                        search_res = n.search(query=q, start_cursor=start_cursor)
                        search_res_str = json.dumps(search_res.to_dict(), ensure_ascii=False)
                        func_res.append(
                            Part.from_function_response(
                                name=function_name,
                                response={
                                    "result": bool(len(search_res.result)),
                                    'message': search_res_str if len(search_res.result) else 'Notionの検索に失敗しました。queryを確認してください。'
                                }
                            )
                        )
            if not len(func_res):
                res = chat.send_message(
                    'もう一度考えてください。',
                    tools=[tools] if func_num < max_func_num and is_tool else None
                )
                usage_metadata = res._raw_response.usage_metadata
                self.token['prompt_token_count'] += usage_metadata.prompt_token_count
                self.token['total_token_count'] += usage_metadata.total_token_count
            else:
                try:
                    res = chat.send_message(
                        func_res,
                        tools=[tools] if func_num < max_func_num and is_tool else None
                    )
                    usage_metadata = res._raw_response.usage_metadata
                    self.token['prompt_token_count'] += usage_metadata.prompt_token_count
                    self.token['total_token_count'] += usage_metadata.total_token_count
                except ResponseBlockedError as e:
                    print(e.responses)
                    break

            if res.candidates[0].finish_reason == generative_models.FinishReason.SAFETY:
                return '安全な応答が生成されませんでした。'

            parts = res.candidates[0].content.parts
