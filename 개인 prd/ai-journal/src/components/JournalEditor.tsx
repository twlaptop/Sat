'use client'

import { useState, useEffect } from 'react'
import { signOut } from '@/app/actions'
import Link from 'next/link'
import WelcomeBackModal from '@/components/WelcomeBackModal'
import type { User } from '@supabase/supabase-js'

type Journal = {
  id: string
  content: string
  primary_emotion: string | null
  emotion_tags: string[]
  created_at: string
}

type AiResult = {
  emotion_tags: string[]
  primary_emotion: string
  ai_confidence: string
  questions: string[]
  comment: string
  cause: string
  solutions: string[]
}

const EMOTION_COLORS: Record<string, string> = {
  기쁨: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
  스트레스: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
  무기력: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
  성취감: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
}

const EMOTION_EMOJI: Record<string, string> = {
  기쁨: '😊',
  스트레스: '😤',
  무기력: '😔',
  성취감: '🎉',
}

export default function JournalEditor({
  user,
  recentJournals,
  todayCount,
}: {
  user: User
  recentJournals: Journal[]
  todayCount: number
}) {
  const [content, setContent] = useState('')
  const [step, setStep] = useState<'input' | 'questions' | 'done'>('input')
  const [aiResult, setAiResult] = useState<AiResult | null>(null)
  const [answers, setAnswers] = useState<string[]>(['', '', ''])
  const [loading, setLoading] = useState(false)
  const [qLoading, setQLoading] = useState(false)
  const [inputHint, setInputHint] = useState('')
  const [saving, setSaving] = useState(false)
  const [currentQ, setCurrentQ] = useState(0)
  const [q1FollowupCount, setQ1FollowupCount] = useState(0)
  const [dark, setDark] = useState(false)

  // 별점
  const [ratings, setRatings] = useState<number[]>([0, 0, 0])
  const [hoverStar, setHoverStar] = useState(0)

  // 리롤 팝업
  const [rerollOpen, setRerollOpen] = useState(false)
  const [rerollHint, setRerollHint] = useState('')
  const [rerollLoading, setRerollLoading] = useState(false)

  useEffect(() => {
    const isDark = localStorage.getItem('theme') === 'dark'
    setDark(isDark)
    if (isDark) document.documentElement.classList.add('dark')
    else document.documentElement.classList.remove('dark')
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

  const handleAskAI = async () => {
    if (content.trim().length < 5) return
    setLoading(true)
    const res = await fetch('/api/ai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    })
    const data = await res.json()
    if (data.primary_emotion === '무관') {
      setInputHint('여기는 오늘 하루를 기록하는 공간이에요. 오늘 있었던 일이나 느낀 감정을 편하게 써보세요 😊')
      setLoading(false)
      return
    }
    setInputHint('')
    setAiResult(data)
    setStep('questions')
    setLoading(false)
  }

  // 리롤 핸들러
  const handleReroll = async () => {
    if (!aiResult) return
    setRerollLoading(true)
    const body: Record<string, string> = { content, rerollHint }
    if (currentQ === 1) body.q1Answer = answers[0]
    if (currentQ === 2) { body.q1Answer = answers[0]; body.q2Answer = answers[1] }
    body.rerollQ = String(currentQ)
    body.emotion = aiResult.primary_emotion

    const res = await fetch('/api/ai/reroll', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    const data = await res.json()
    if (data.question) {
      setAiResult(prev => {
        if (!prev) return prev
        const next = [...prev.questions]
        next[currentQ] = data.question
        return { ...prev, questions: next }
      })
    }
    setRerollLoading(false)
    setRerollOpen(false)
    setRerollHint('')
  }

  const [saveError, setSaveError] = useState('')

  const handleSave = async () => {
    if (!aiResult) return
    setSaving(true)
    setSaveError('')
    try {
      const res = await fetch('/api/journal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          emotion_tags: aiResult.emotion_tags,
          primary_emotion: aiResult.primary_emotion,
          ai_confidence: aiResult.ai_confidence,
          questions: aiResult.questions,
          answers,
          comment: aiResult.comment,
          cause: aiResult.cause,
          solutions: aiResult.solutions,
          question_ratings: ratings,
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error)
      setStep('done')
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : '저장 중 오류가 발생했습니다.'
      setSaveError(msg)
    }
    setSaving(false)
  }

  const handleReset = () => {
    setContent('')
    setAiResult(null)
    setAnswers(['', '', ''])
    setCurrentQ(0)
    setRatings([0, 0, 0])
    setRerollOpen(false)
    setRerollHint('')
    setQ1FollowupCount(0)
    setStep('input')
  }

  const streak = recentJournals.length
  const lastDate = recentJournals[0]?.created_at ?? null

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 transition-colors">
      <WelcomeBackModal lastJournalDate={lastDate} />
      <header className="flex items-center justify-between px-5 pt-6 pb-4 max-w-lg mx-auto">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-2xl">📔</span>
            <span className="font-bold text-gray-800 dark:text-white text-lg">AI 감정 저널</span>
          </div>
          {streak > 0 && (
            <p className="text-xs text-indigo-500 dark:text-indigo-400 mt-0.5 ml-9">🔥 {streak}일째 기록 중</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={toggleTheme}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-full bg-white dark:bg-gray-700 shadow-sm border border-gray-100 dark:border-gray-600 text-xs text-gray-500 dark:text-gray-300 hover:scale-105 transition-transform"
          >
            {dark ? '☀️ 라이트' : '🌙 다크'}
          </button>
          <button
            onClick={() => signOut()}
            className="text-xs text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-600"
          >
            로그아웃
          </button>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-5 pb-24">
        {/* 입력 단계 */}
        {step === 'input' && (
          <div className="space-y-4">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-5 border border-gray-100 dark:border-gray-700">
              <p className="text-sm text-gray-400 dark:text-gray-500 mb-1">
                {new Date().toLocaleDateString('ko-KR', { month: 'long', day: 'numeric', weekday: 'long' })}
              </p>
              <p className="text-base font-medium text-gray-700 dark:text-gray-200 mb-4">오늘 어땠어? 생각나는 대로 써보세요</p>
              <textarea
                value={content}
                onChange={e => setContent(e.target.value)}
                placeholder="오늘 있었던 일, 느낀 감정, 힘들었던 것... 무엇이든 괜찮아요"
                className="w-full h-40 resize-none text-sm text-gray-700 dark:text-gray-200 placeholder-gray-300 dark:placeholder-gray-600 focus:outline-none bg-transparent"
              />
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-50 dark:border-gray-700">
                <span className="text-xs text-gray-300 dark:text-gray-600">{content.length}자</span>
                {todayCount >= 3 && (
                  <span className="text-xs text-orange-400">오늘 최대 3개 작성 완료</span>
                )}
              </div>
            </div>

            {inputHint && (
              <p className="text-sm text-indigo-400 dark:text-indigo-300 text-center px-2 py-2 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl">
                {inputHint}
              </p>
            )}
            <button
              onClick={() => handleAskAI()}
              disabled={content.trim().length < 5 || loading || todayCount >= 3}
              className="w-full bg-indigo-500 text-white rounded-2xl py-4 font-medium text-sm hover:bg-indigo-600 transition disabled:opacity-40 flex items-center justify-center gap-2"
            >
              {loading ? (
                <><span className="animate-spin">⏳</span> AI가 분석 중...</>
              ) : (
                <>✨ AI 질문 받기</>
              )}
            </button>
          </div>
        )}

        {/* 질문 단계 */}
        {step === 'questions' && aiResult && (
          <div className="space-y-4">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-5 border border-gray-100 dark:border-gray-700">
              <p className="text-xs text-gray-400 dark:text-gray-500 mb-3">AI가 감지한 감정</p>
              <div className="flex gap-2 flex-wrap">
                {(aiResult.emotion_tags ?? []).map(tag => (
                  <span key={tag} className={`px-3 py-1.5 rounded-full text-sm font-medium ${EMOTION_COLORS[tag] || 'bg-indigo-100 text-indigo-700'}`}>
                    {EMOTION_EMOJI[tag]} {tag}
                  </span>
                ))}
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
              {/* Q 탭 */}
              <div className="flex border-b border-gray-50 dark:border-gray-700">
                {aiResult.questions.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentQ(i)}
                    className={`flex-1 py-3 text-xs font-medium transition ${currentQ === i ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-500' : 'text-gray-300 dark:text-gray-600'}`}
                  >
                    Q{i + 1}
                  </button>
                ))}
              </div>

              <div className="p-5">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-200 mb-4 leading-relaxed">
                  {qLoading ? '다음 질문을 만들고 있어요...' : aiResult.questions[currentQ]}
                </p>

                {/* 별점 */}
                <div className="flex items-center gap-1 mb-3">
                  {[1, 2, 3, 4, 5].map(star => (
                    <button
                      key={star}
                      onClick={() => {
                        const next = [...ratings]
                        next[currentQ] = star
                        setRatings(next)
                      }}
                      onMouseEnter={() => setHoverStar(star)}
                      onMouseLeave={() => setHoverStar(0)}
                      className="text-xl transition-transform hover:scale-110"
                    >
                      {star <= (hoverStar || ratings[currentQ]) ? '★' : '☆'}
                    </button>
                  ))}
                  {ratings[currentQ] > 0 && (
                    <span className="text-xs text-gray-400 ml-1">{ratings[currentQ]}점</span>
                  )}
                </div>

                <textarea
                  value={answers[currentQ]}
                  onChange={e => {
                    const next = [...answers]
                    next[currentQ] = e.target.value
                    setAnswers(next)
                  }}
                  placeholder="생각을 자유롭게 써보세요 (선택사항)"
                  className="w-full h-28 resize-none text-sm text-gray-700 dark:text-gray-200 placeholder-gray-300 dark:placeholder-gray-600 focus:outline-none bg-transparent"
                />

                {/* 리롤 버튼 */}
                <button
                  onClick={() => { setRerollOpen(true); setRerollHint('') }}
                  className="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500 hover:text-indigo-500 mt-1 transition"
                >
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M23 4v6h-6"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
                  </svg>
                  질문 다시 받기
                </button>
              </div>

              {/* 리롤 팝업 */}
              {rerollOpen && (
                <div className="mx-5 mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-xl border border-gray-100 dark:border-gray-600">
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">원하는 질문 방향을 알려주세요 (선택사항)</p>
                  <textarea
                    value={rerollHint}
                    onChange={e => setRerollHint(e.target.value)}
                    placeholder="예) 더 구체적으로 물어봐줘 / 다른 각도로 / 더 가볍게"
                    className="w-full h-16 resize-none text-sm bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 placeholder-gray-300 dark:placeholder-gray-600 rounded-lg p-2 focus:outline-none border border-gray-100 dark:border-gray-600"
                  />
                  <div className="flex gap-2 mt-2">
                    <button
                      onClick={() => { setRerollOpen(false); setRerollHint('') }}
                      className="flex-1 py-2 text-xs text-gray-400 border border-gray-200 dark:border-gray-600 rounded-lg"
                    >
                      취소
                    </button>
                    <button
                      onClick={handleReroll}
                      disabled={rerollLoading}
                      className="flex-1 py-2 text-xs bg-indigo-500 text-white rounded-lg disabled:opacity-50"
                    >
                      {rerollLoading ? '생성 중...' : '다시 시도하기'}
                    </button>
                  </div>
                </div>
              )}

              {saveError && (
                <p className="px-5 pb-2 text-xs text-red-400 text-center">{saveError}</p>
              )}

              {/* 하단 버튼 */}
              <div className="flex gap-2 px-5 pb-5">
                <button
                  onClick={handleReset}
                  className="py-2.5 px-3 text-xs text-gray-400 dark:text-gray-500 border border-gray-200 dark:border-gray-600 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  처음으로
                </button>
                {currentQ > 0 && (
                  <button onClick={() => setCurrentQ(q => q - 1)} className="py-2.5 px-3 text-xs text-gray-400 dark:text-gray-500 border border-gray-200 dark:border-gray-600 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700">
                    이전
                  </button>
                )}
                {currentQ < aiResult.questions.length - 1 ? (
                  <button
                    onClick={async () => {
                      if (currentQ === 0) {
                        setQLoading(true)
                        const res = await fetch('/api/ai', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ content, q1Answer: answers[0], emotion: aiResult?.primary_emotion }),
                        })
                        const data = await res.json()
                        setQLoading(false)
                        if (!data.sufficient && q1FollowupCount < 1) {
                          setAiResult(prev => prev ? { ...prev, questions: [data.q1_followup || prev.questions[0], prev.questions[1], prev.questions[2]] } : prev)
                          setAnswers(['', '', ''])
                          setRatings(prev => { const next = [...prev]; next[0] = 0; return next })
                          setQ1FollowupCount(c => c + 1)
                          return
                        }
                        setAiResult(prev => prev ? { ...prev, questions: [prev.questions[0], data.q2 || '그 마음, 조금 더 말해줄 수 있어요?', prev.questions[2]] } : prev)
                      } else if (currentQ === 1) {
                        const res = await fetch('/api/ai', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ content, q1Answer: answers[0], q2Answer: answers[1], emotion: aiResult?.primary_emotion }),
                        })
                        const data = await res.json()
                        if (!data.sufficient) {
                          setAiResult(prev => prev ? { ...prev, questions: [prev.questions[0], data.q2_followup || prev.questions[1], prev.questions[2]] } : prev)
                          setAnswers(prev => { const next = [...prev]; next[1] = ''; return next })
                          setRatings(prev => { const next = [...prev]; next[1] = 0; return next })
                          return
                        }
                        setAiResult(prev => prev ? { ...prev, questions: [prev.questions[0], prev.questions[1], data.q3 || prev.questions[2]] } : prev)
                      }
                      setCurrentQ(q => q + 1)
                    }}
                    className="flex-1 py-2.5 text-sm bg-indigo-50 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 rounded-xl hover:bg-indigo-100 dark:hover:bg-indigo-800">
                    다음 질문
                  </button>
                ) : (
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="flex-1 py-2.5 text-sm bg-indigo-500 text-white rounded-xl hover:bg-indigo-600 disabled:opacity-50"
                  >
                    {saving ? '저장 중...' : '저장하기 💾'}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 완료 단계 */}
        {step === 'done' && aiResult && (
          <div className="space-y-4">
            <div className="text-center py-6">
              <div className="text-5xl mb-3">🌟</div>
              <h2 className="text-xl font-bold text-gray-800 dark:text-white">저장 완료!</h2>
              <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">오늘의 감정을 잘 기록했어요</p>
            </div>

            <div className="bg-indigo-50 dark:bg-indigo-900/40 rounded-2xl p-5 border border-indigo-100 dark:border-indigo-800">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">🤖</span>
                <span className="text-xs font-medium text-indigo-600 dark:text-indigo-400">AI 한마디</span>
              </div>
              <p className="text-sm text-gray-700 dark:text-gray-200 leading-relaxed">{aiResult.comment}</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">🔍</span>
                <span className="text-xs font-medium text-gray-500 dark:text-gray-400">감정 원인 분석</span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{aiResult.cause}</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-lg">💡</span>
                <span className="text-xs font-medium text-gray-500 dark:text-gray-400">오늘 해볼 수 있는 것</span>
              </div>
              <div className="space-y-2">
                {aiResult.solutions.map((s, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <span className="text-indigo-400 font-bold text-sm mt-0.5">{i + 1}.</span>
                    <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{s}</p>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={handleReset}
              className="w-full bg-indigo-500 text-white py-4 rounded-2xl text-sm font-bold hover:bg-indigo-600 transition"
            >
              새 저널 쓰기
            </button>
          </div>
        )}

        {/* 최근 기록 */}
        {step === 'input' && recentJournals.length > 0 && (
          <div className="mt-6">
            <p className="text-xs text-gray-400 dark:text-gray-500 mb-3 font-medium">최근 기록</p>
            <div className="space-y-2">
              {recentJournals.slice(0, 3).map(j => (
                <div key={j.id} className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-400 dark:text-gray-500">
                      {new Date(j.created_at).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
                    </span>
                    {j.primary_emotion && (
                      <span className={`text-xs px-2 py-0.5 rounded-full ${EMOTION_COLORS[j.primary_emotion] || 'bg-gray-100 text-gray-600'}`}>
                        {EMOTION_EMOJI[j.primary_emotion]} {j.primary_emotion}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-2">{j.content}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 flex">
        <Link href="/" className="flex-1 flex flex-col items-center py-3 text-indigo-500 dark:text-indigo-400">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          <span className="text-xs mt-0.5 font-medium">홈</span>
        </Link>
        <Link href="/history" className="flex-1 flex flex-col items-center py-3 text-gray-400 dark:text-gray-500 hover:text-indigo-500 transition">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          <span className="text-xs mt-0.5">기록</span>
        </Link>
        <Link href="/report" className="flex-1 flex flex-col items-center py-3 text-gray-400 dark:text-gray-500 hover:text-indigo-500 transition">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
          </svg>
          <span className="text-xs mt-0.5">리포트</span>
        </Link>
      </nav>
    </div>
  )
}
