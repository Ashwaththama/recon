import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || ''

export async function postFiles(hrFile, payrollFile) {
  const formData = new FormData()
  formData.append('hr_file', hrFile)
  formData.append('payroll_file', payrollFile)

  let response
  try {
    response = await axios.post(`${BASE_URL}/api/reconcile`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob',
    })
  } catch (err) {
    if (err.response?.data) {
      const text = await err.response.data.text()
      try {
        const json = JSON.parse(text)
        throw new Error(json.detail || 'Server error')
      } catch {
        throw new Error(text || 'Server error')
      }
    }
    throw new Error(err.message || 'Network error')
  }

  const blob = new Blob([response.data], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  })
  return URL.createObjectURL(blob)
}
