'use client'

import { createClient } from '@/lib/supabase/client'
import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [remember, setRemember] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [dark, setDark] = useState(false)
  const [showPw, setShowPw] = useState(false)

  const supabase = createClient()

  useEffect(() => {
    setDark(document.documentElement.classList.contains('dark'))
    const saved = localStorage.getItem('savedEmail')
    if (saved) setEmail(saved)
  }, [])

  const toggleTheme = () => {
    const isDark = document.documentElement.classList.contains('dark')
    if (isDark) {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
      setDark(false)
    } else {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
      setDark(true)
    }
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    const { error } = await supabase.auth.signInWithPassword({ email, password })

    if (error) {
      setMessage('이메일 또는 비밀번호가 올바르지 않습니다.')
    } else {
      if (remember) localStorage.setItem('savedEmail', email)
      else localStorage.removeItem('savedEmail')
      location.href = '/'
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col items-center justify-center p-4 transition-colors">
      {/* 다크모드 토글 */}
      <button
        onClick={toggleTheme}
        className="fixed top-4 right-4 flex items-center gap-1.5 px-3 py-2 rounded-full bg-white dark:bg-gray-700 shadow-md text-xs font-medium text-gray-600 dark:text-gray-200 hover:scale-105 transition-transform"
      >
        {dark ? '☀️ 라이트모드' : '🌙 다크모드'}
      </button>

      {/* 로고 */}
      <div className="mb-8 text-center">
        <span className="text-5xl">📔</span>
        <h1 className="text-xl font-bold text-gray-800 dark:text-white mt-3">AI 감정 저널</h1>
      </div>

      {/* 로그인 카드 */}
      <div className="bg-white dark:bg-gray-800 w-full max-w-sm rounded-2xl shadow-sm p-8">
        <form onSubmit={handleLogin} className="space-y-6">
          {/* 이메일 */}
          <div className="relative">
            <input
              type="email"
              placeholder="아이디(이메일)"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              className="w-full bg-transparent border-b border-gray-300 dark:border-gray-600 py-3 text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 dark:focus:border-indigo-400 transition-colors pr-8"
            />
            {email && (
              <button type="button" onClick={() => setEmail('')} className="absolute right-0 top-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                  <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm3.5 10.5L10.5 11.5 8 9l-2.5 2.5L4.5 10.5 7 8 4.5 5.5 5.5 4.5 8 7l2.5-2.5 1 1L9 8l2.5 2.5z"/>
                </svg>
              </button>
            )}
          </div>

          {/* 비밀번호 */}
          <div className="relative">
            <input
              type={showPw ? 'text' : 'password'}
              placeholder="비밀번호"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              className="w-full bg-transparent border-b border-gray-300 dark:border-gray-600 py-3 text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 dark:focus:border-indigo-400 transition-colors pr-16"
            />
            <div className="absolute right-0 top-3 flex gap-2">
              <button type="button" onClick={() => setShowPw(!showPw)} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                {showPw ? (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                    <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                ) : (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                )}
              </button>
              {password && (
                <button type="button" onClick={() => setPassword('')} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm3.5 10.5L10.5 11.5 8 9l-2.5 2.5L4.5 10.5 7 8 4.5 5.5 5.5 4.5 8 7l2.5-2.5 1 1L9 8l2.5 2.5z"/>
                  </svg>
                </button>
              )}
            </div>
          </div>

          {/* 로그인 상태 유지 */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setRemember(!remember)}
              className={`w-5 h-5 rounded flex items-center justify-center border transition-colors ${remember ? 'bg-indigo-500 border-indigo-500' : 'border-gray-300 dark:border-gray-600'}`}
            >
              {remember && (
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path d="M2 6l3 3 5-5" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              )}
            </button>
            <span className="text-sm text-gray-600 dark:text-gray-400 cursor-pointer" onClick={() => setRemember(!remember)}>
              로그인 상태 유지
            </span>
          </div>

          {message && <p className="text-sm text-center text-red-400">{message}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl py-3.5 text-sm font-bold transition disabled:opacity-50"
          >
            {loading ? '로그인 중...' : '로그인'}
          </button>
        </form>
      </div>

      {/* 하단 링크 */}
      <div className="flex items-center gap-4 mt-5 text-sm text-gray-400 dark:text-gray-500">
        <Link href="/find-id" className="hover:text-gray-600 dark:hover:text-gray-300">아이디 찾기</Link>
        <span className="text-gray-300 dark:text-gray-700">|</span>
        <Link href="/find-pw" className="hover:text-gray-600 dark:hover:text-gray-300">비밀번호 찾기</Link>
        <span className="text-gray-300 dark:text-gray-700">|</span>
        <Link href="/signup" className="text-indigo-500 hover:text-indigo-600 font-medium">
          회원가입
        </Link>
      </div>
    </div>
  )
}
