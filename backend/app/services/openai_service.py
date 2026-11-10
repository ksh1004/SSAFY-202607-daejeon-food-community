import json

from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import get_settings
from app.services.chat_service import (
    search_posts,
    search_restaurant_with_posts,
    search_restaurants,
)


settings = get_settings()

client = OpenAI(
    api_key=settings.openai_api_key,
)


SYSTEM_PROMPT = """
당신은 대전 지역 커뮤니티 LocalHub의 AI 챗봇입니다.

대전 공공 음식점 데이터와 LocalHub 커뮤니티 게시글을
활용해 사용자의 질문에 답변하세요.

규칙:
- 음식점명, 주소 등 사실 정보는 검색된 공공데이터만 사용하세요.
- 커뮤니티 관련 정보는 검색된 LocalHub 게시글만 사용하세요.
- 데이터에 없는 평점, 인기, 맛, 웨이팅 등은 추측하지 마세요.
- 제공된 데이터에 없는 사실을 만들어내지 마세요.
- 음식점 추천 결과는 LocalHub 관련 게시글이 있는 음식점을 우선합니다.
- 게시글이 있는 음식점끼리는 관련 게시글 수가 많은 순으로 우선합니다.
- 이것은 '인기 맛집 순위'가 아니라 LocalHub 커뮤니티에서 관련 이야기가 더 많은 순서입니다.
- 음식점 검색 결과는 별도의 UI로 사용자에게 표시됩니다.
- 음식점 검색 결과가 있으면 음식점 목록을 답변에 반복하지 마세요.
- 음식점 검색 결과가 있으면 답변은 "검색 결과입니다."처럼 짧게 작성하세요.
- 음식점 검색 결과가 없는 일반 질문에는 자연스럽고 간결하게 답변하세요.
- 불필요한 인사, 서론, 결론, 부연 설명을 작성하지 마세요.
- 불필요한 후속 질문이나 추가 제안을 작성하지 마세요.
"""


TOOLS = [
    {
        "type": "function",
        "name": "search_restaurants",
        "description": (
            "대전 공공데이터에서 지역명 또는 "
            "음식점명으로 음식점을 검색합니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": (
                        "검색할 지역명 또는 음식점명"
                    ),
                },
            },
            "required": [
                "keyword"
            ],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_posts",
        "description": (
            "LocalHub 커뮤니티에서 "
            "관련 게시글을 검색합니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": (
                        "검색할 게시글 키워드"
                    ),
                },
            },
            "required": [
                "keyword"
            ],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_restaurant_with_posts",
        "description": (
            "대전 음식점과 해당 음식점에 연결된 "
            "LocalHub 커뮤니티 게시글을 함께 검색합니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": (
                        "검색할 지역명 또는 음식점명"
                    ),
                },
            },
            "required": [
                "keyword"
            ],
            "additionalProperties": False,
        },
    },
]


def execute_tool(
    db: Session,
    name: str,
    arguments: dict,
):
    """
    OpenAI가 요청한 Tool을 실제로 실행합니다.
    """

    keyword = arguments.get(
        "keyword",
        "",
    )

    if name == "search_restaurants":
        return search_restaurants(
            db=db,
            keyword=keyword,
        )

    if name == "search_posts":
        return search_posts(
            db=db,
            keyword=keyword,
        )

    if name == "search_restaurant_with_posts":
        return search_restaurant_with_posts(
            db=db,
            keyword=keyword,
        )

    return {
        "error": "지원하지 않는 검색 기능입니다."
    }


def create_chat_response(
    db: Session,
    message: str,
    history: list[dict] | None = None,
) -> dict:
    """
    사용자 질문을 OpenAI에 전달하고,
    필요한 경우 DB 검색 Tool을 실행합니다.

    최종적으로 프론트에 전달할
    answer + restaurants 데이터를 반환합니다.
    """

    input_messages = []

    # 최근 대화 4개만 전달
    if history:
        for item in history[-4:]:
            input_messages.append(
                {
                    "role": item["role"],
                    "content": item["content"][
                        :500
                    ],
                }
            )

    input_messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    # 첫 번째 OpenAI 호출
    # 사용자의 질문을 보고 필요한 Tool을 선택
    response = client.responses.create(
        model=settings.openai_model,
        instructions=SYSTEM_PROMPT,
        input=input_messages,
        tools=TOOLS,
    )

    tool_outputs = []

    # 프론트에 전달할 음식점 데이터 저장
    collected_restaurants = []

    for item in response.output:

        if item.type != "function_call":
            continue

        arguments = json.loads(
            item.arguments
        )

        result = execute_tool(
            db=db,
            name=item.name,
            arguments=arguments,
        )

        # 음식점 검색 결과 저장
        if item.name == "search_restaurants":

            for restaurant in result:

                collected_restaurants.append(
                    {
                        "restaurant": restaurant,
                        "posts": [],
                    }
                )

        # 음식점 + 게시글 통합 검색 결과 저장
        elif (
            item.name
            == "search_restaurant_with_posts"
        ):

            collected_restaurants.extend(
                result.get(
                    "results",
                    [],
                )
            )

        # Tool 결과를 OpenAI에 다시 전달
        tool_outputs.append(
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(
                    result,
                    ensure_ascii=False,
                    default=str,
                ),
            }
        )

    # Tool 호출이 없었던 일반 대화
    if not tool_outputs:

        return {
            "answer": response.output_text,
            "restaurants": [],
        }

    # DB 검색 결과를 OpenAI에 전달하여
    # 최종 자연어 답변 생성
    final_response = client.responses.create(
        model=settings.openai_model,
        instructions=SYSTEM_PROMPT,
        previous_response_id=response.id,
        input=tool_outputs,
        tools=TOOLS,
    )

    # 프론트에 전달할 구조 생성
    restaurants_for_frontend = []

    for item in collected_restaurants:

        restaurant = item[
            "restaurant"
        ]

        posts = item.get(
            "posts",
            [],
        )

        community_post = None

        # 관련 게시글이 있으면
        # 가장 최근 게시글 1개를 프론트에 전달
        if posts:

            first_post = posts[0]

            community_post = {
                "post_id": first_post["id"],
                "text": (
                    "LocalHub에는 관련 방문 경험을 "
                    "공유한 글이 있어요."
                ),
            }

        restaurants_for_frontend.append(
            {
                "content_id": restaurant[
                    "content_id"
                ],
                "title": restaurant[
                    "title"
                ],
                "address": restaurant[
                    "address"
                ],
                "community_post": community_post,
            }
        )

    return {
        "answer": final_response.output_text,
        "restaurants": restaurants_for_frontend,
    }