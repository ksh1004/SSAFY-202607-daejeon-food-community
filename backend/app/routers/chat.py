from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.services.openai_service import (
    create_chat_response,
)


router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:

    try:

        history = [
            message.model_dump()
            for message in request.history
        ]

        result = create_chat_response(
            db=db,
            message=request.message,
            history=history,
        )

        return ChatResponse(
            answer=result["answer"],
            restaurants=result[
                "restaurants"
            ],
        )

    except Exception as error:

        print(
            f"Chat API Error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "챗봇 응답을 생성하는 중 "
                "오류가 발생했습니다."
            ),
        ) from error