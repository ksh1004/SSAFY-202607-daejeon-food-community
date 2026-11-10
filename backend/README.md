# LocalHub Backend

대전·충청권 음식점 JSON 516건을 SQLite에 적재하고, FastAPI로 음식점 조회와 익명 게시판 CRUD를 제공하는 백엔드입니다.

## 1. 설치

```bash
python -m venv venv
```

Windows Git Bash:

```bash
source venv/Scripts/activate
```

```bash
pip install -r requirements.txt
```

## 2. 환경변수

```bash
cp .env.example .env
```

Windows에서는 `.env.example`을 복사해 `.env` 파일을 직접 만들어도 됩니다.

```env
DATABASE_URL=sqlite:///./data/localhub.db
FRONTEND_ORIGIN=http://localhost:5173
```

`.env`는 Git에 올리지 않습니다.

## 3. DB 생성 및 음식점 적재

```bash
python -m scripts.seed_restaurants
```

실행 후 `data/localhub.db`가 생성됩니다.

## 4. 서버 실행

```bash
uvicorn app.main:app --reload
```

- API 문서: http://127.0.0.1:8000/docs
- 상태 확인: http://127.0.0.1:8000/health

## 5. API

### 음식점

- `GET /api/restaurants`
- `GET /api/restaurants/{restaurant_id}`
- 검색: `/api/restaurants?keyword=칼국수`
- 페이지: `/api/restaurants?page=1&size=20`

### 게시글

- `GET /api/posts`
- `GET /api/posts/{post_id}`
- `POST /api/posts`
- `PUT /api/posts/{post_id}`
- `DELETE /api/posts/{post_id}`

게시글 작성 예시:

```json
{
  "restaurant_id": 1,
  "title": "방문 후기",
  "content": "맛있었습니다.",
  "password": "1234"
}
```

게시글 삭제 요청 body:

```json
{
  "password": "1234"
}
```

## 6. Render

- Build Command:
  `pip install -r requirements.txt && python -m scripts.seed_restaurants`
- Start Command:
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Render 환경변수:

- `DATABASE_URL=sqlite:///./data/localhub.db`
- `FRONTEND_ORIGIN=https://프론트주소.netlify.app`

무료 Render에서는 재시작 또는 재배포 시 SQLite 변경 데이터가 초기화될 수 있습니다.
