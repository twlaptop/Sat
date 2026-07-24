'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function FindIdPage() {
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<{ maskedEmail: string }[]>([])
  const [searched, setSearched] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSearched(false)

    const res = await fetch('/api/find-id', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    })
    const data = await res.json()

    if (data.found) {
      setResults(data.results)
    } else {
      setResults([])
    }
    setSearched(true)
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col items-center justify-center p-4 transition-colors">
      <div className="mb-6 text-center">
        <span className="text-5xl">📔</span>
        <h1 className="text-xl font-bold text-gray-800 dark:text-white mt-3">AI 감정 저널</h1>
      </div>

      <div className="bg-white dark:bg-gray-800 w-full max-w-sm rounded-2xl shadow-sm p-8">
        {!searched ? (
          <>
            <h2 className="text-lg font-bold text-gray-800 dark:text-white mb-1">아이디 찾기</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">가입 시 입력한 이름을 입력해 주세요.</p>

            <form onSubmit={handleSearch} className="space-y-6">
              <div className="border border-gray-200 dark:border-gray-600 rounded-xl overflow-hidden">
                <div className="flex items-center px-4 py-3 gap-3">
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
              </div>

              {error && <p className="text-sm text-center text-red-400">{error}</p>}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl py-3.5 text-sm font-bold transition disabled:opacity-50"
              >
                {loading ? '검색 중...' : '다음'}
              </button>
            </form>
          </>
        ) : results.length > 0 ? (
          <>
            <h2 className="text-lg font-bold text-gray-800 dark:text-white mb-1">아이디를 찾았어요</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
              비밀번호를 잊으셨다면 비밀번호 찾기를 이용해 주세요.
            </p>

            <div className="border border-gray-200 dark:border-gray-600 rounded-xl overflow-hidden mb-6">
              {results.map((r, i) => (
                <div key={i} className={`flex items-center gap-3 px-4 py-4 ${i > 0 ? 'border-t border-gray-100 dark:border-gray-700' : ''}`}>
                  <div className="w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-gray-400">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                    </svg>
                  </div>
                  <span className="text-sm font-medium text-gray-800 dark:text-white">{r.maskedEmail}</span>
                </div>
              ))}
            </div>

            <div className="flex gap-2">
              <Link
                href="/find-pw"
                className="flex-1 text-center border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl py-3 text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition"
              >
                비밀번호 찾기
              </Link>
              <Link
                href="/login"
                className="flex-1 text-center bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl py-3 text-sm font-bold transition"
              >
                로그인하러 가기
              </Link>
            </div>
          </>
        ) : (
          <>
            <div className="text-center py-4">
              <div className="text-4xl mb-4">😔</div>
              <h2 className="text-lg font-bold text-gray-800 dark:text-white mb-2">일치하는 계정 없음</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                입력한 이름으로 가입된 계정을 찾을 수 없습니다.
              </p>
              <button
                onClick={() => { setSearched(false); setName('') }}
                className="w-full bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl py-3.5 text-sm font-bold transition"
              >
                다시 시도
              </button>
            </div>
          </>
        )}
      </div>

      <div className="flex items-center gap-4 mt-5 text-sm text-gray-400 dark:text-gray-500">
        <Link href="/login" className="hover:text-gray-600 dark:hover:text-gray-300">로그인</Link>
        <span className="text-gray-300 dark:text-gray-700">|</span>
        <Link href="/find-pw" className="hover:text-gray-600 dark:hover:text-gray-300">비밀번호 찾기</Link>
        <span className="text-gray-300 dark:text-gray-700">|</span>
        <Link href="/signup" className="text-indigo-500 hover:text-indigo-600 font-medium">회원가입</Link>
      </div>
    </div>
  )
}
