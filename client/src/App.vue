<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { Marked } from 'marked'
import { getResponse, sendMessage as s, ResponseMessage } from 'src/modules'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js'
import { selectFile, fileToBase64 } from 'fileasy'

const marked = new Marked(
  markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code, lang) {
      const language = hljs.getLanguage(lang) ? lang : 'plaintext'
      return hljs.highlight(code, { language }).value
    }
  })
)

const inputDom = ref<HTMLInputElement | null>(null)
const footerDom = ref<HTMLDivElement | null>(null)

const isComposing = ref(false)
const alreadyResponse = ref(true)
const progressMessage = ref('')
const messageText = ref('')
const message = ref<ResponseMessage[]>([])
const images = ref<string[]>([])

const managerKey = ref({
  Shift: false
})

nextTick(() => {
  if (!inputDom.value) return
  inputDom.value.addEventListener('compositionstart', () => {
    isComposing.value = true
  })
  inputDom.value.addEventListener('compositionend', () => {
    isComposing.value = false
  })

  document.addEventListener('keydown', e => {
    if (e.key === 'Shift') {
      managerKey.value.Shift = true
    }

    if (managerKey.value.Shift) {
      return
    }
    if (e.key === 'Enter' && !isComposing.value && alreadyResponse.value) {
      // inoutへの入力を禁止する
      e.preventDefault()
      sendMessage()
    }
  })
  document.addEventListener('keyup', e => {
    if (e.key === 'Shift') {
      managerKey.value.Shift = false
    }
  })
})

getResponse(res => {
  if (res.status === 'progress') {
    progressMessage.value = res.message
    return
  }
  message.value.push(res)
  alreadyResponse.value = true

  nextTick(() => {
    const pageHeight = document.documentElement.scrollHeight
    window.scrollTo(0, pageHeight)
  })
})

const sendMessage = () => {
  if (isComposing.value) return
  if (!alreadyResponse.value) return
  if (!messageText.value) return
  s(messageText.value, images.value)
  message.value.push({
    message: messageText.value,
    status: 'success',
    role: 'user',
    images: images.value
  })
  progressMessage.value = ''
  messageText.value = ''
  images.value = []
  alreadyResponse.value = false
  nextTick(() => {
    const pageHeight = document.documentElement.scrollHeight
    window.scrollTo(0, pageHeight)
  })
}

const footerHight = computed(() => {
  if (!footerDom.value) return '0px'
  return `${footerDom.value.clientHeight}px`
})

const messageTextToHTML = (r: ResponseMessage) => {
  if (r.role === 'user') return r.message
  if (r.status === 'error')
    return `<div>${r.message}<br />※ジェミニには、エラー前の記憶はありません。</div>`
  return marked.parse(r.message)
}

const selectImage = async () => {
  const file = await selectFile('image/png, image/jpeg', 3)
  if (!file) return

  images.value = await Promise.all(file.map(f => fileToBase64(f)))
}
</script>

<template>
  <div class="_page">
    <h1 v-if="!message.length">何を手伝いましょう</h1>

    <div v-for="(m, index) in message" :key="`message_${index}`">
      <div class="_chat">
        <div>
          <b class="_user_name"
            >{{ m.role === 'user' ? 'あなた' : 'ジェミニ' }}
          </b>
        </div>

        <div class="_message" v-if="m.role === 'user'" v-text="m.message" />
        <div
          class="_message"
          :style="`color: ${m.status === 'error' ? '#ff0000' : '#000000'}`"
          v-else-if="m.role === 'model'"
          v-html="messageTextToHTML(m)"
        />

        <div class="_send_image_area">
          <img
            v-for="(image, index) in m.images || []"
            :key="`image_${index}`"
            :src="image"
            class="_send_image"
          />
        </div>
      </div>
    </div>

    <div class="_chat" v-if="!alreadyResponse">
      <div style="display: flex">
        <b class="_user_name">ジェミニ</b>
        <div class="_spinner" style="margin-left: 10px" />
      </div>
      <div class="_message" style="opacity: 0.8">
        {{ progressMessage || '考え中です...' }}
      </div>
    </div>
  </div>

  <footer ref="footerDom">
    <div class="_main">
      <div></div>
      <div style="opacity: 0.8; display: flex; gap: 5px">
        <img
          v-for="(image, index) in images || []"
          :key="`image_${index}`"
          :src="image"
          style="width: 50px; height: 50px"
          class="_send_image"
        />
      </div>
      <div></div>
    </div>

    <div class="_main">
      <div class="_photo_library" @click="selectImage">
        <img src="/photo_library.svg" />
      </div>

      <textarea
        ref="inputDom"
        placeholder="ジェミニへのメッセージを入力してください"
        v-model="messageText"
      />

      <div
        @click="alreadyResponse ? sendMessage() : null"
        :class="['_send', { _disable: !alreadyResponse }]"
      >
        <img src="/send.svg" />
      </div>
    </div>
  </footer>
</template>

<style lang="sass">
p
  margin: 0
ol
  margin: 0
</style>
<style lang="sass" scoped>
._page
  padding: 0.5rem
  padding-bottom: v-bind(footerHight)
._message
  padding-left: 1rem
  margin-bottom: 0.5rem
  white-space: pre-wrap
  word-wrap: break-word
._send_image_area
  padding-left: 1rem
  display: flex
  gap: 5px
  margin-bottom: 0.5rem
._send_image
  height: 100px
  width: 100px
  object-fit: cover
  border-radius: 8px
._user_name
  font-size: 16px
  line-height: 18px
._spinner
  width: 16px
  height: 16px
  border: 2px #ddd solid
  border-top: 2px #2e93e6 solid
  border-radius: 50%
  animation: sp-anime 1.0s infinite linear
@keyframes sp-anime
  100%
    transform: rotate(360deg)
footer
  position: fixed
  bottom: 0
  left: 0
  width: 100vw
  background: #ffffff
  padding: 0.5rem 0.5rem 1rem 0.5rem
  box-sizing: border-box
  ._main
    width: 100%
    display: grid
    grid-template-columns: 32px 1fr 32px
  textarea
    box-sizing: border-box
    width: 100%
    padding: 0.5rem
    border: 1px solid #676767
    border-radius: 0.5rem
    outline: none
    font-size: 16px
  button
    width: 20%
    padding: 0.5rem
    border: 1px solid #676767
    border-radius: 0.5rem
    outline: none

._photo_library
  margin-top: auto
  margin-right: 8px
  cursor: pointer
._send
  margin-top: auto
  margin-left: 8px
  cursor: pointer
  ._disable
    opacity: 0.8
    cursor: not-allowed
</style>
