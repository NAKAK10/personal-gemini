import { io } from 'socket.io-client'

const socket = io('http://127.0.0.1:5000')

export type ResponseMessage = {
  role: 'model' | 'user'
  status: 'success' | 'progress' | 'error'
  message: string
  images?: string[]
}

socket.on('connect', () => {
  console.log('connected GEMINI AI')
})

export const sendMessage = (message: string, images: string[]) => {
  socket.emit('message', {
    message: message,
    images: images,
  })
}

export const getResponse = (f: (m: ResponseMessage) => void) => {
  socket.on('message', (message: ResponseMessage) => {
    f(message)
  })
}
