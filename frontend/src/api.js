import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export async function getConfig() {
  const { data } = await api.get('/config')
  return data
}

export async function testConnection() {
  const { data } = await api.get('/test-connection')
  return data
}

export async function listFiles(folder, recursive = false) {
  const { data } = await api.get('/files', { params: { folder, recursive } })
  return data
}

export async function getDocument(path) {
  const { data } = await api.get('/document', { params: { path } })
  return data
}

export async function uploadFile(file) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/upload', form)
  return data
}

export async function generateNote(payload) {
  const { data } = await api.post('/generate', payload)
  return data
}

export async function generateAll(payload) {
  const { data } = await api.post('/generate-all', payload)
  return data
}

export async function generateFolderMap(folder, maxFiles = 30) {
  const { data } = await api.post('/folder-map', { folder, max_files: maxFiles })
  return data
}

export async function chatWithDoc(question, context, history = []) {
  const { data } = await api.post('/chat', { question, context, history })
  return data
}

export async function extractTerms(content, title = '') {
  const { data } = await api.post('/extract-terms', { content, title })
  return data
}
