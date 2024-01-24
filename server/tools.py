from vertexai.preview.generative_models import Tool, FunctionDeclaration
from typing import List

import config


def gen_tool_list() -> Tool:
    function_declarations: List[FunctionDeclaration] = []

    function_declarations.append(
        FunctionDeclaration(
            name="get_outer_html",
            description="Used when you want to get more detailed information based on the URL",
            parameters={
                "type": "object",
                "properties": {
                        "q": {
                            "type": "string",
                            "description": "URL"
                        }
                },
                "required": ["q"]
            }
        ),
    )

    function_declarations.append(
        FunctionDeclaration(
            name="get_now_date_at_ISO",
            description="Get the current date and time in ISO8601 format",
            parameters={
                "type": "object",
                "properties": {},
            }
        ),
    )

    if config.GOOGLE_CSE_ID and config.GOOGLE_API_KEY:
        function_declarations.append(
            FunctionDeclaration(
                name="get_default_serch",
                description="When you need to search, do a google search",
                parameters={
                    "type": "object",
                    "properties": {
                            "q": {
                                "type": "string",
                                "description": "Query used for google search. Be able to search by word."
                            }
                    },
                    "required": ["q"]
                }
            )
        )

    if config.NOTION_API_KEY:
        function_declarations.append(
            FunctionDeclaration(
                name="notion_search",
                description="Be able to access to personal information such as login information and search information about your own services(ex:eメンテ,Pureha,省エネ,SEAMO).",
                parameters={
                    "type": "object",
                    "properties": {
                        "q": {
                            "type": "string",
                            "description": "Query used for Notion.Be able to search by word."
                        },
                        "start_cursor": {
                            "type": "string",
                            "description": "Start Id of next page.Be able to also search with notion"
                        }
                    },
                    "required": ["q"]
                }
            )
        )

    return Tool(function_declarations=function_declarations)
