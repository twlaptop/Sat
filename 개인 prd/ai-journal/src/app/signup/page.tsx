'use client'

import { createClient } from '@/lib/supabase/client'
import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function SignupPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [done, setDone] = useState(false)
  const [dark, setDark] = useState(false)

  const supabase = createClient()

  useEffect(() => {
    setDark(document.documentElement.classList.contains('dark'))
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

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    if (password !== confirm) { setMessage('비밀번호가 일치하지 않습니다.'); return }
    if (password.length < 6) { setMessage('비밀번호는 6자 이상이어야 합니다.'); return }

    setLoading(true)
    setMessage('')

    const { data, error } = await supabase.auth.signUp({ email, password })

    if (error) {
      setMessage(error.message)
      setLoading(false)
      return
    }

    if (data.user) {
      await supabase.from('profiles').insert({
        id: data.user.id,
        name,
        email,
      })
    }

    setDone(true)
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col items-center justify-center p-4 transition-colors">
      <button
        onClick={toggleTheme}
        className="fixed top-4 right-4 flex items-center gap-1.5 px-3 py-2 rounded-full bg-white dark:bg-gray-700 shadow-md text-xs font-medium text-gray-600 dark:text-gray-200 hover:scale-105 transition-transform"
      >
        {dark ? '☀️ 라이트모드' : '🌙 다크모드'}
      </button>

      <div className="mb-6 text-center">
        <span className="text-5xl">📔</span>
        <h1 className="text-xl font-bold text-gray-800 dark:text-white mt-3">AI 감정 저널</h1>
      </div>

      <div className="bg-white dark:bg-gray-800 w-full max-w-sm rounded-2xl shadow-sm p-8">
        {!done ? (
          <>
            <h2 className="text-lg font-bold text-gray-800 dark:text-white mb-6 text-center">회원가입</h2>

            <form onSubmit={handleSignup} className="space-y-5">
              {/* 이름 */}
              <div className="flex items-center border-b border-gray-200 dark:border-gray-600 py-2 gap-3">
                <svg className="text-gray-400 shrink-0" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                </svg>
                <input
                  type="text"
                  placeholder="이름"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  required
                  className="flex-1 bg-transparent text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none"
                />
              </div>

              {/* 이메일 */}
              <div className="flex items-center border-b border-gray-200 dark:border-gray-600 py-2 gap-3">
                <svg className="text-gray-400 shrink-0" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 7L2 7"/>
                </svg>
                <input
                  type="email"
                  placeholder="이메일 주소"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  className="flex-1 bg-transparent text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none"
                />
              </div>

              {/* 비밀번호 */}
              <div className="flex items-center border-b border-gray-200 dark:border-gray-600 py-2 gap-3">
                <svg className="text-gray-400 shrink-0" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                <input
                  type={showPw ? 'text' : 'password'}
                  placeholder="비밀번호 (6자 이상)"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  className="flex-1 bg-transparent text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none"
                />
                <button type="button" onClick={() => setShowPw(!showPw)} className="text-gray-400 hover:text-gray-600 shrink-0">
                  {showPw ? (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  ) : (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                    </svg>
                  )}
                </button>
              </div>

              {/* 비밀번호 확인 */}
              <div className="flex items-center border-b border-gray-200 dark:border-gray-600 py-2 gap-3">
                <svg className="text-gray-400 shrink-0" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 12l2 2 4-4"/><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                <input
                  type="password"
                  placeholder="비밀번호 확인"
                  value={confirm}
                  onChange={e => setConfirm(e.target.value)}
                  required
                  className="flex-1 bg-transparent text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none"
                />
                {confirm && (
                  <span className={`text-xs shrink-0 ${password === confirm ? 'text-green-500' : 'text-red-400'}`}>
                    {password === confirm ? '✓' : '✗'}
                  </span>
                )}
              </div>

              {message && <p className="text-sm text-center text-red-400">{message}</p>}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl py-3.5 text-sm font-bold transition disabled:opacity-50 mt-2"
              >
                {loading ? '가입 중...' : '회원가입'}
              </button>
            </form>
          </>
        ) : (
          <div className="text-center py-4">
            <div className="text-5xl mb-4">✅</div>
            <h2 className="text-lg font-bold text-gray-800 dark:text-white mb-2">가입 완료!</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
              <span className="text-indigo-500 font-medium">{email}</span>으로<br />
              인증 메일을 발송했습니다.<br />
              메일 확인 후 로그인해 주세요.
            </p>
            <Link href="/login" className="block w-full bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl py-3.5 text-sm font-bold transition text-center">
              로그인하러 가기
            </Link>
          </div>
        )}
      </div>

      <div className="flex items-center gap-4 mt-5 text-sm text-gray-400 dark:text-gray-500">
        <Link href="/login" className="hover:text-gray-600 dark:hover:text-gray-300">로그인</Link>
        <span className="text-gray-300 dark:text-gray-700">|</span>
        <Link href="/find-id" className="hover:text-gray-600 dark:hover:text-gray-300">아이디 찾기</Link>
        <span className="text-gray-300 dark:text-gray-700">|</span>
        <Link href="/find-pw" className="hover:text-gray-600 dark:hover:text-gray-300">비밀번호 찾기</Link>
      </div>
    </div>
  )
}
