<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { sendChatMessage } from '@/api/chatbotApi'
import { getRestaurants } from '@/api/restaurantApi'

const router = useRouter()

const isOpen = ref(false)
const inputText = ref('')
const isSending = ref(false)
const messageListRef = ref(null)
const chatInputRef = ref(null)
let nextMessageId = 2

const SUGGESTED_PROMPTS = [
  '유성구 맛집 추천해줘',
  '덕명동 맛집 알려줘',
  'OO식당과 관련된 커뮤니티 게시글을 소개해줘',
]

const useSuggestedPrompt = async (prompt) => {
  inputText.value = prompt
  await nextTick()
  chatInputRef.value?.focus()
}

// 챗봇이 언급한 음식점 이름을 지도로 바로 연결하기 위한 이름→id 조회 테이블.
const restaurantByName = new Map()

onMounted(async () => {
  try {
    const response = await getRestaurants()
    response.data.forEach((restaurant) => {
      restaurantByName.set(restaurant.name, restaurant.id)
    })
  } catch {
    // 지도 연결은 부가 기능이므로, 실패해도 챗봇 자체는 정상 동작해야 한다.
  }
})

const GREETING_TEXT = '안녕하세요! 궁금한 지역 정보를 물어보세요.'
const messages = ref([
  { id: 1, role: 'bot', text: GREETING_TEXT, proseHtml: `<p>${GREETING_TEXT}</p>` },
])

const TYPING_FRAMES = ['.', '..', '...']
const typingDots = ref(TYPING_FRAMES[0])
let typingTimer = null

const startTypingAnimation = () => {
  let frameIndex = 0
  typingDots.value = TYPING_FRAMES[frameIndex]
  typingTimer = window.setInterval(() => {
    frameIndex = (frameIndex + 1) % TYPING_FRAMES.length
    typingDots.value = TYPING_FRAMES[frameIndex]
  }, 400)
}

const stopTypingAnimation = () => {
  window.clearInterval(typingTimer)
  typingTimer = null
}

const toggleOpen = () => {
  isOpen.value = !isOpen.value
}

const closeWidget = () => {
  isOpen.value = false
}

const scrollToBottom = async () => {
  await nextTick()
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

// LLM 응답을 v-html로 그대로 꽂으면 XSS 위험이 있어, 먼저 HTML 특수문자를 이스케이프한 뒤
// "- 목록", 빈 줄 기준 문단, **굵게**, 음식점/게시글 언급만 안전하게 태그로 변환한다
// (LLM 출력에 실제 태그가 섞여 있어도 텍스트로만 취급되어 주입될 수 없다).
const escapeHtml = (text) => text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

const formatInline = (line) => {
  let html = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  // LLM이 "가게명 — 주소"처럼 줄 단위로 쓸 때도, 여러 가게를 한 문장에 쉼표로 나열할 때도 있어서
  // 특정 위치/구두점 패턴에 기대지 않고, 문장 어디에 있든 실제 DB 이름과 일치하면 지도 링크로 바꾼다.
  // 이름이 긴 것부터 치환해, 짧은 이름이 긴 이름의 일부를 먼저 가로채지 않게 한다.
  const namesInLine = [...restaurantByName.keys()]
    .filter((name) => html.includes(name))
    .sort((a, b) => b.length - a.length)

  // 지도 마커와 같은 물방울 핀 모양의 작은 아이콘을 이름 앞에 붙인다 (currentColor로 링크 색을 그대로 물려받는다).
  const pinIconSvg =
    '<svg class="chat-widget__pin-icon" width="11" height="15" viewBox="0 0 32 42" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
    '<path d="M16 0C7.163 0 0 7.163 0 16c0 11 16 26 16 26s16-15 16-26C32 7.163 24.837 0 16 0z" fill="currentColor" />' +
    '<circle cx="16" cy="16" r="6" fill="#ffffff" /></svg>'

  for (const name of namesInLine) {
    const restaurantId = restaurantByName.get(name)
    const escapedName = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    html = html.replace(
      new RegExp(escapedName, 'g'),
      `<button type="button" class="chat-widget__restaurant-link" data-restaurant-id="${restaurantId}">${pinIconSvg}${name}</button>`,
    )
  }

  return html
}

const MAX_VISIBLE_POSTS = 3

// LLM이 게시글을 나열할 때 "게시글 ID: N" / "ID: N" / "연결된 음식점 ID: 12345 (이름)" /
// "음식점: 이름" / "제목: ..." / "내용: ..." 형식의 줄을 반복해서 쓰는데, 이 줄들은 화면에
// 그대로 보여주지 않고 아래처럼 정리해서 다시 그린다.
// - 음식점 이름은 (여러 번 나와도) 딱 한 번만 보여준다.
// - 게시글은 음식점 카드처럼 제목이 붙은 카드(최대 3개)로 분리해서 보여준다.
// - 음식점 ID(숫자), 내용 줄은 화면에서 완전히 제거한다.
// LLM이 목록 기호(-, •, "1.")를 붙여서 줄을 쓰기도 해서, 분류 판단 전에 먼저 제거한다.
const stripListMarker = (line) => line.replace(/^(?:[-•*]\s+|\d+[.)]\s+)/, '')

// 제목은 Vue 텍스트 보간({{ }})으로 그대로 렌더링할 것이므로, 이스케이프 전(원문) 텍스트에서 추출한다.
const extractPostSummary = (text) => {
  const posts = []
  let restaurantName = null
  const proseLines = []
  let currentPost = null

  const pushCurrentPost = () => {
    if (currentPost) posts.push(currentPost)
    currentPost = null
  }

  for (const rawLine of text.split('\n')) {
    const line = stripListMarker(rawLine.trim())

    const postIdMatch = line.match(/^(?:게시글\s*)?ID\s*[:：]\s*(\d+)/)
    if (postIdMatch) {
      pushCurrentPost()
      currentPost = { id: postIdMatch[1], title: null }
      continue
    }

    const restaurantIdWithNameMatch = line.match(/음식점\s*ID\s*[:：]\s*\S+\s*\(([^)]+)\)/)
    if (restaurantIdWithNameMatch) {
      if (!restaurantName) restaurantName = restaurantIdWithNameMatch[1].trim()
      continue
    }

    if (/음식점\s*ID\s*[:：]/.test(line)) {
      continue
    }

    const restaurantMatch = line.match(/^음식점\s*[:：]\s*(.+)$/)
    if (restaurantMatch) {
      if (!restaurantName) restaurantName = restaurantMatch[1].trim()
      continue
    }

    const titleMatch = line.match(/^제목\s*[:：]\s*(.+)$/)
    if (titleMatch) {
      if (currentPost) currentPost.title = titleMatch[1].trim()
      continue
    }

    if (/^내용\s*[:：]/.test(line)) {
      continue
    }

    if (/^검색된\s*게시글/.test(line)) {
      continue
    }

    proseLines.push(rawLine)
  }

  pushCurrentPost()

  return { posts: posts.slice(0, MAX_VISIBLE_POSTS), restaurantName, proseLines }
}

const formatProseLines = (rawLines) => {
  const htmlParts = []
  let listBuffer = []
  let paragraphBuffer = []

  const flushList = () => {
    if (listBuffer.length === 0) return
    const items = listBuffer.map((item) => `<li>${formatInline(item)}</li>`).join('')
    htmlParts.push(`<ul class="chat-widget__list">${items}</ul>`)
    listBuffer = []
  }

  const flushParagraph = () => {
    if (paragraphBuffer.length === 0) return
    htmlParts.push(`<p>${paragraphBuffer.map(formatInline).join('<br>')}</p>`)
    paragraphBuffer = []
  }

  for (const rawLine of rawLines) {
    const line = rawLine.trim()

    if (line.startsWith('- ') || line.startsWith('• ')) {
      flushParagraph()
      listBuffer.push(line.slice(2).trim())
      continue
    }

    flushList()

    if (line === '') {
      flushParagraph()
      continue
    }

    paragraphBuffer.push(line)
  }

  flushList()
  flushParagraph()

  return htmlParts.join('')
}

// 게시글/음식점 언급 줄을 걷어낸 나머지 본문만 안전하게 HTML로 만들고,
// 게시글·음식점 이름은 restaurants 카드와 동일하게 실제 Vue 엘리먼트로 별도 렌더링한다.
const parseBotMessage = (text) => {
  const { posts, restaurantName, proseLines } = extractPostSummary(text)
  const proseHtml = formatProseLines(proseLines.map(escapeHtml))
  return { posts, restaurantName, proseHtml }
}

const viewOnMap = (restaurantId) => {
  closeWidget()
  router.push({ name: 'restaurant-explore', query: { focus: restaurantId } })
}

const viewPost = (postId) => {
  closeWidget()
  router.push({ name: 'post-detail', params: { postId } })
}

// v-html로 렌더링된 음식점 언급 링크는 Vue 이벤트가 직접 안 붙으므로, 상위에서 위임 처리한다.
// 아래 restaurants/posts 카드 목록은 이거랑 별개로 실제 Vue @click을 쓴다.
const handleMessagesClick = (event) => {
  const restaurantLink = event.target.closest('.chat-widget__restaurant-link')
  if (restaurantLink) {
    viewOnMap(restaurantLink.dataset.restaurantId)
  }
}

const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || isSending.value) return

  const history = messages.value.map((message) => ({
    role: message.role === 'bot' ? 'assistant' : 'user',
    content: message.text,
  }))

  messages.value.push({ id: nextMessageId++, role: 'user', text })
  inputText.value = ''
  isSending.value = true
  startTypingAnimation()
  scrollToBottom()

  try {
    const response = await sendChatMessage({ message: text, history })
    const { posts, restaurantName, proseHtml } = parseBotMessage(response.data.answer)
    messages.value.push({
      id: nextMessageId++,
      role: 'bot',
      text: response.data.answer,
      proseHtml,
      posts,
      mentionedRestaurant: restaurantName,
      restaurants: response.data.restaurants ?? [],
    })
  } catch {
    const errorText = '죄송해요, 답변을 가져오지 못했어요. 잠시 후 다시 시도해주세요.'
    messages.value.push({
      id: nextMessageId++,
      role: 'bot',
      text: errorText,
      proseHtml: `<p>${errorText}</p>`,
    })
  } finally {
    isSending.value = false
    stopTypingAnimation()
    scrollToBottom()
  }
}

onBeforeUnmount(stopTypingAnimation)
</script>

<template>
  <div class="chat-widget">
    <Transition name="chat-panel">
      <section v-if="isOpen" class="chat-widget__panel" role="dialog" aria-label="잇슈 챗봇">
        <header class="chat-widget__header">
          <span class="chat-widget__title">
            <svg
              class="chat-widget__title-icon"
              width="22"
              height="22"
              viewBox="0 0 36 36"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <line x1="18" y1="8" x2="18" y2="4" stroke="#ffffff" stroke-width="1.8" stroke-linecap="round" />
              <circle cx="18" cy="3.2" r="1.8" fill="#FED7AA" />
              <rect x="7" y="8" width="22" height="19" rx="8" fill="#ffffff" />
              <circle cx="14.5" cy="17" r="2.1" fill="var(--color-primary)" />
              <circle cx="21.5" cy="17" r="2.1" fill="var(--color-primary)" />
              <path
                d="M14 21c1.2 2.2 7.6 2.2 8.8 0"
                stroke="var(--color-primary)"
                stroke-width="2"
                stroke-linecap="round"
                fill="none"
              />
            </svg>
            잇슈 챗봇
          </span>
          <button type="button" class="chat-widget__close" aria-label="챗봇 닫기" @click="closeWidget">
            ✕
          </button>
        </header>

        <div ref="messageListRef" class="chat-widget__messages" @click="handleMessagesClick">
          <template v-for="message in messages" :key="message.id">
            <div
              v-if="message.role === 'bot' && message.proseHtml"
              class="chat-widget__bubble chat-widget__bubble--bot"
              v-html="message.proseHtml"
            ></div>
            <p v-else-if="message.role === 'user'" class="chat-widget__bubble chat-widget__bubble--user">
              {{ message.text }}
            </p>

            <ul v-if="message.restaurants?.length" class="chat-widget__restaurant-cards">
              <li v-for="restaurant in message.restaurants" :key="restaurant.content_id">
                <button
                  type="button"
                  class="chat-widget__restaurant-card"
                  @click="viewOnMap(restaurant.content_id)"
                >
                  <svg
                    class="chat-widget__pin-icon"
                    width="14"
                    height="19"
                    viewBox="0 0 32 42"
                    xmlns="http://www.w3.org/2000/svg"
                    aria-hidden="true"
                  >
                    <path
                      d="M16 0C7.163 0 0 7.163 0 16c0 11 16 26 16 26s16-15 16-26C32 7.163 24.837 0 16 0z"
                      fill="currentColor"
                    />
                    <circle cx="16" cy="16" r="6" fill="#ffffff" />
                  </svg>
                  <span class="chat-widget__restaurant-card-info">
                    <strong>{{ restaurant.title }}</strong>
                    <span v-if="restaurant.address" class="chat-widget__restaurant-card-address">{{
                      restaurant.address
                    }}</span>
                    <span v-if="restaurant.community_post" class="chat-widget__restaurant-card-post">
                      💬 {{ restaurant.community_post.text }}
                    </span>
                  </span>
                </button>
              </li>
            </ul>

            <ul v-if="message.posts?.length" class="chat-widget__post-cards">
              <li v-for="post in message.posts" :key="post.id">
                <button type="button" class="chat-widget__post-card" @click="viewPost(post.id)">
                  <svg
                    class="chat-widget__post-icon"
                    width="15"
                    height="18"
                    viewBox="0 0 24 28"
                    xmlns="http://www.w3.org/2000/svg"
                    aria-hidden="true"
                  >
                    <path
                      d="M3 2h12l6 6v18a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linejoin="round"
                    />
                    <path d="M15 2v6h6" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
                  </svg>
                  <span class="chat-widget__post-card-info">
                    <strong>{{ post.title || '관련 게시글' }}</strong>
                    <span v-if="message.mentionedRestaurant" class="chat-widget__post-card-restaurant">{{
                      message.mentionedRestaurant
                    }}</span>
                  </span>
                </button>
              </li>
            </ul>
          </template>

          <div v-if="messages.length === 1" class="chat-widget__suggestions">
            <button
              v-for="prompt in SUGGESTED_PROMPTS"
              :key="prompt"
              type="button"
              class="chat-widget__suggestion"
              @click="useSuggestedPrompt(prompt)"
            >
              {{ prompt }}
            </button>
          </div>

          <p v-if="isSending" class="chat-widget__bubble chat-widget__bubble--bot chat-widget__bubble--typing">
            {{ typingDots }}
          </p>
        </div>

        <form class="chat-widget__form" @submit.prevent="sendMessage">
          <input
            ref="chatInputRef"
            v-model="inputText"
            type="text"
            placeholder="메시지를 입력하세요"
            aria-label="챗봇에게 메시지 보내기"
            :disabled="isSending"
          />
          <button
            type="submit"
            class="chat-widget__send"
            aria-label="메시지 전송"
            :disabled="isSending"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" fill="currentColor" />
            </svg>
          </button>
        </form>
      </section>
    </Transition>

    <button
      v-if="!isOpen"
      type="button"
      class="chat-widget__toggle"
      aria-expanded="false"
      aria-label="챗봇 열기"
      @click="toggleOpen"
    >
      <svg width="36" height="36" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
        <!-- 다수 IT 서비스 챗봇 아이콘에서 흔한 패턴(둥근 배지 + 미니멀 봇 페이스 + 안테나 + 온라인 상태 점)을
             참고한 오리지널 디자인 -->
        <line x1="18" y1="8" x2="18" y2="4" stroke="#ffffff" stroke-width="1.8" stroke-linecap="round" />
        <circle cx="18" cy="3.2" r="1.8" fill="#F97316" />
        <rect x="7" y="8" width="22" height="19" rx="8" fill="#ffffff" />
        <circle cx="14.5" cy="17" r="2.1" fill="var(--color-primary)" />
        <circle cx="21.5" cy="17" r="2.1" fill="var(--color-primary)" />
        <path
          d="M14 21c1.2 2.2 7.6 2.2 8.8 0"
          stroke="var(--color-primary)"
          stroke-width="2"
          stroke-linecap="round"
          fill="none"
        />
        <circle cx="27" cy="26" r="3.6" fill="var(--color-primary)" />
        <circle cx="27" cy="26" r="2.6" fill="#16A34A" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.chat-widget {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 1100;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.chat-widget__toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  min-height: auto;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: var(--color-primary);
  box-shadow: var(--shadow-panel);
  cursor: pointer;
  transition: transform 0.15s ease;
}

.chat-widget__toggle:hover {
  background: var(--color-primary-hover);
  transform: translateY(-2px);
}

.chat-widget__panel {
  display: flex;
  flex-direction: column;
  width: 400px;
  max-width: calc(100vw - 48px);
  height: 600px;
  max-height: calc(100vh - 48px);
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  box-shadow: var(--shadow-panel);
}

.chat-widget__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: var(--color-primary);
  color: #ffffff;
  font-weight: 700;
}

.chat-widget__title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-widget__title-icon {
  flex-shrink: 0;
}

.chat-widget__close {
  min-height: auto;
  padding: 4px;
  border: 0;
  background: transparent;
  color: #ffffff;
  font-size: 16px;
  cursor: pointer;
}

.chat-widget__messages {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  padding: 16px;
  background: var(--color-background);
}

.chat-widget__bubble {
  max-width: 80%;
  margin: 0;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: 14px;
  line-height: 1.5;
}

.chat-widget__bubble--bot {
  align-self: flex-start;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.chat-widget__bubble--user {
  align-self: flex-end;
  background: var(--color-primary);
  color: #ffffff;
}

.chat-widget__bubble--typing {
  min-width: 34px;
  color: var(--color-text-secondary);
  font-weight: 700;
  letter-spacing: 1px;
}

.chat-widget__bubble :deep(p) {
  margin: 0 0 8px;
}

.chat-widget__bubble :deep(p:last-child) {
  margin-bottom: 0;
}

.chat-widget__bubble :deep(.chat-widget__list) {
  margin: 4px 0 8px;
  padding-left: 18px;
}

.chat-widget__bubble :deep(.chat-widget__list li) {
  margin-bottom: 4px;
}

.chat-widget__bubble :deep(.chat-widget__list li:last-child) {
  margin-bottom: 0;
}

.chat-widget__bubble :deep(strong) {
  font-weight: 800;
}

.chat-widget__bubble :deep(.chat-widget__restaurant-link) {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--color-primary);
  font: inherit;
  font-weight: 800;
  text-decoration: underline;
  text-underline-offset: 2px;
  cursor: pointer;
}

.chat-widget__bubble :deep(.chat-widget__restaurant-link:hover) {
  color: var(--color-primary-hover);
}

.chat-widget__bubble :deep(.chat-widget__pin-icon) {
  flex-shrink: 0;
}

.chat-widget__pin-icon {
  flex-shrink: 0;
}

.chat-widget__restaurant-cards {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 88%;
  margin: 0;
  padding: 0;
  list-style: none;
  align-self: flex-start;
}

.chat-widget__restaurant-card {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  width: 100%;
  min-height: auto;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-primary);
  text-align: left;
  cursor: pointer;
}

.chat-widget__restaurant-card:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-50);
}

.chat-widget__restaurant-card .chat-widget__pin-icon {
  margin-top: 2px;
}

.chat-widget__restaurant-card-info {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 2px;
}

.chat-widget__restaurant-card-info strong {
  color: var(--color-text-primary);
  font-size: 13px;
  font-weight: 800;
}

.chat-widget__restaurant-card-address {
  color: var(--color-text-secondary);
  font-size: 12px;
  line-height: 1.4;
}

.chat-widget__restaurant-card-post {
  color: var(--color-primary);
  font-size: 11px;
  font-weight: 700;
}

.chat-widget__post-cards {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 88%;
  margin: 0;
  padding: 0;
  list-style: none;
  align-self: flex-start;
}

.chat-widget__post-card {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  width: 100%;
  min-height: auto;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-primary);
  text-align: left;
  cursor: pointer;
}

.chat-widget__post-card:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-50);
}

.chat-widget__post-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.chat-widget__post-card-info {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 2px;
}

.chat-widget__post-card-info strong {
  color: var(--color-text-primary);
  font-size: 13px;
  font-weight: 800;
}

.chat-widget__post-card-restaurant {
  color: var(--color-text-secondary);
  font-size: 12px;
  line-height: 1.4;
}

.chat-widget__suggestions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  max-width: 88%;
}

.chat-widget__suggestion {
  width: auto;
  min-height: auto;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-pill);
  background: var(--color-surface-soft);
  color: var(--color-text-secondary);
  font-size: 12.5px;
  text-align: left;
  cursor: pointer;
}

.chat-widget__suggestion:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-50);
  color: var(--color-primary);
}

.chat-widget__form {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
}

.chat-widget__form input {
  flex: 1;
}

.chat-widget__send {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  min-height: auto;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: var(--color-primary);
  color: #ffffff;
  cursor: pointer;
}

.chat-widget__send:hover {
  background: var(--color-primary-hover);
}

.chat-widget__send:disabled,
.chat-widget__form input:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.chat-panel-enter-active,
.chat-panel-leave-active {
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}

.chat-panel-enter-from,
.chat-panel-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@media (max-width: 767px) {
  .chat-widget {
    right: 16px;
    bottom: 16px;
  }

  .chat-widget__panel {
    position: fixed;
    inset: 0;
    width: 100%;
    max-width: 100%;
    height: 100%;
    border-radius: 0;
  }
}
</style>
