'use client'

import { createClient } from '@/lib/supabase/client'
import { useState } from 'react'
import Link from 'next/link'

export default function FindPwPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')

  const supabase = createClient()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${location.origin}/auth/reset-password`,
    })

    if (error) {
      setError('이메일 발송에 실패했습니다. 다시 시도해 주세요.')
    } else {
      setSent(true)
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col items-center justify-center p-4 transition-colors">
      <div className="mb-8 text-center">
        <span className="text-5xl">📔</span>
        <h1 className="text-xl font-bold text-gray-800 dark:text-white mt-3">AI 감정 저널</h1>
      </div>

      <div className="bg-white dark:bg-gray-800 w-full max-w-sm rounded-2xl shadow-sm p-8">
        {!sent ? (
          <>
            <div className="text-center mb-6">
              <div className="text-4xl mb-3">🔐</div>
              <h2 className="text-lg font-bold text-gray-800 dark:text-white">비밀번호 찾기</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                가입한 이메일로 재설정 링크를 보내드립니다
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <input
                  type="email"
                  placeholder="가입한 이메일 주소"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  className="w-full bg-transparent border-b border-gray-300 dark:border-gray-600 py-3 text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 dark:focus:border-indigo-400 transition-colors"
                />
              </div>

              {error && <p className="text-sm text-center text-red-400">{error}</p>}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl py-3.5 text-sm font-bold transition disabled:opacity-50"
              >
                {loading ? '발송 중...' : '재설정 링크 받기'}
              </button>
            </form>
          </>
        ) : (
          <div className="text-center py-4">
            <div className="text-5xl mb-4">✅</div>
            <h2 className="text-lg font-bold text-gray-800 dark:text-white mb-2">이메일을 확인해 주세요</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed mb-2">
              <span className="text-indigo-500 font-medium">{email}</span>으로
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed mb-6">
              비밀번호 재설정 링크를 발송했습니다.<br />
              스팸함도 확인해 주세요.
            </p>
            <button
              onClick={() => { setSent(false); setEmail('') }}
              className="text-sm text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 underline"
            >
              다른 이메일로 다시 시도
            </button>
          </div>
        )}
      </div>

      <div className="flex items-center gap-4 mt-5 text-sm text-gray-400 dark:text-gray-500">
        <Link href="/find-id" className="hover:text-gray-600 dark:hover:text-gray-300">아이디 찾기</Link>
        <span className="text-gray-300 dark:text-gray-700">|</span>
        <Link href="/login" className="hover:text-gray-600 dark:hover:text-gray-300">로그인</Link>
        <span className="text-gray-300 dark:text-gray-700">|</span>
        <Link href="/signup" className="text-indigo-500 hover:text-indigo-600 font-medium">회원가입</Link>
      </div>
    </div>
  )
}
