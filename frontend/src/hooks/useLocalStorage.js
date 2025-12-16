import { useEffect, useState } from 'react'

export default function useLocalStorage(key, initialValue) {
  const readValue = () => {
    if (typeof window === 'undefined') return initialValue
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (e) {
      console.warn('useLocalStorage parse error for', key, e)
      return initialValue
    }
  }

  const [storedValue, setStoredValue] = useState(readValue)

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(storedValue))
    } catch (e) {
      console.warn('useLocalStorage write error for', key, e)
    }
  }, [key, storedValue])

  return [storedValue, setStoredValue]
}
