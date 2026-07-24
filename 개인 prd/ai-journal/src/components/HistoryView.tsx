'use client'

import { useState } from 'react'
import Link from 'next/link'
import JournalDetailModal from '@/components/JournalDetailModal'

type Journal = {
  id: string
  content: string
  primary_emotion: string | null
  emotion_tags: string[]
  ai_questions: string[]
  reflection_answers: string[] | null
  ai_comment: string | null
  ai_cause: string | null
  ai_solutions: string[] | null
  created_at: string
}

const EMOTION_EMOJI: Record<string, string> = {
  기쁨: '😊',
  스트레스: '😤',
  무기력: '😔',
  성취감: '🎉',
}

const EMOTION_COLORS: Record<string, string> = {
  기쁨: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
  스트레스: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
  무기력: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
  성취감: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
}

const MONTH_KR = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
const DAY_KR = ['일', '월', '화', '수', '목', '금', '토']

export default function HistoryView({
  journals,
  totalCount,
  year,
  month,
}: {
  journals: Journal[]
  totalCount: number
  year: number
  month: number
}) {
  const [selected, setSelected] = useState<string | null>(null)
  const [detailJournal, setDetailJournal] = useState<Journal | null>(null)
  const [journalList, setJournalList] = useState<Journal[]>(journals)

  const handleDelete = (id: string) => {
    setJournalList(prev => prev.filter(j => j.id !== id))
  }

  // 날짜별 감정 맵
  const dateMap: Record<string, Journal[]> = {}
  journals.forEach(j => {
    const date = new Date(j.created_at)
    const kstDate = new Date(date.getTime() + 9 * 60 * 60 * 1000)
    const key = kstDate.toISOString().split('T')[0]
    if (!dateMap[key]) dateMap[key] = []
    dateMap[key].push(j)
  })

  // 이달 통계
  const monthCount = journalList.length
  const emotionCount: Record<string, number> = {}
  journalList.forEach(j => {
    if (j.primary_emotion) emotionCount[j.primary_emotion] = (emotionCount[j.primary_emotion] || 0) + 1
  })
  const topEmotion = Object.entries(emotionCount).sort((a, b) => b[1] - a[1])[0]?.[0]

  // 스트릭 계산
  let streak = 0
  const today = new Date()
  for (let i = 0; i < 30; i++) {
    const d = new Date(today)
    d.setDate(today.getDate() - i)
    const key = d.toISOString().split('T')[0]
    if (dateMap[key]) streak++
    else if (i > 0) break
  }

  // 달력 생성
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const calCells: (number | null)[] = [...Array(firstDay).fill(null), ...Array.from({ length: daysInMonth }, (_, i) => i + 1)]
  while (calCells.length % 7 !== 0) calCells.push(null)

  const todayStr = new Date().toISOString().split('T')[0]

  const selectedJournals = selected
    ? journals.filter(j => {
        const d = new Date(j.created_at)
        const kst = new Date(d.getTime() + 9 * 60 * 60 * 1000)
        return kst.toISOString().split('T')[0] === selected
      })
    : []

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 transition-colors">
      {detailJournal && (
        <JournalDetailModal
          journal={detailJournal}
          onClose={() => setDetailJournal(null)}
          onDelete={handleDelete}
        />
      )}
      {/* 헤더 */}
      <header className="flex items-center justify-between px-5 pt-6 pb-4 max-w-lg mx-auto">
        <div className="flex items-center gap-2">
          <span className="text-2xl">📔</span>
          <span className="font-bold text-gray-800 dark:text-white text-lg">기록 히스토리</span>
        </div>
        <span className="text-sm text-gray-500 dark:text-gray-400 font-medium">
          {year}년 {MONTH_KR[month]}
        </span>
      </header>

      <main className="max-w-lg mx-auto px-5 pb-24 space-y-5">
        {/* 이달 요약 카드 3개 */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 text-center border border-gray-100 dark:border-gray-700 shadow-sm">
            <p className="text-2xl font-bold text-indigo-500">{monthCount}</p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">이달 기록</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 text-center border border-gray-100 dark:border-gray-700 shadow-sm">
            <p className="text-2xl font-bold text-orange-400">🔥{streak}</p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">연속 작성</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 text-center border border-gray-100 dark:border-gray-700 shadow-sm">
            <p className="text-2xl">{topEmotion ? EMOTION_EMOJI[topEmotion] : '—'}</p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">{topEmotion || '감정 없음'}</p>
          </div>
        </div>

        {/* 감정 캘린더 */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700 shadow-sm">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-200 mb-4">감정 캘린더</p>
          <div className="grid grid-cols-7 gap-1 mb-2">
            {DAY_KR.map(d => (
              <div key={d} className="text-center text-xs text-gray-400 dark:text-gray-500 py-1">{d}</div>
            ))}
          </div>
          <div className="grid grid-cols-7 gap-1">
            {calCells.map((day, i) => {
              if (!day) return <div key={i} />
              const key = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
              const dayJournals = dateMap[key]
              const isToday = key === todayStr
              const isSelected = selected === key
              const emotion = dayJournals?.[0]?.primary_emotion

              return (
                <button
                  key={i}
                  onClick={() => setSelected(isSelected ? null : key)}
                  className={`aspect-square rounded-xl flex flex-col items-center justify-center text-xs transition
                    ${isSelected ? 'ring-2 ring-indigo-400' : ''}
                    ${isToday ? 'font-bold' : ''}
                    ${dayJournals ? 'bg-indigo-50 dark:bg-indigo-900/40 hover:bg-indigo-100 dark:hover:bg-indigo-900/60' : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'}
                  `}
                >
                  <span className={`${isToday ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-600 dark:text-gray-400'}`}>
                    {day}
                  </span>
                  {emotion && <span className="text-xs leading-none">{EMOTION_EMOJI[emotion]}</span>}
                  {dayJournals && !emotion && <span className="w-1 h-1 rounded-full bg-indigo-400 mt-0.5" />}
                </button>
              )
            })}
          </div>
        </div>

        {/* 선택된 날짜 기록 */}
        {selected && selectedJournals.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-indigo-200 dark:border-indigo-700 shadow-sm">
            <p className="text-sm font-medium text-indigo-600 dark:text-indigo-400 mb-3">
              {new Date(selected).toLocaleDateString('ko-KR', { month: 'long', day: 'numeric', weekday: 'long' })}
            </p>
            <div className="space-y-3">
              {selectedJournals.map(j => (
                <div key={j.id} className="border-l-2 border-indigo-200 dark:border-indigo-700 pl-3">
                  {j.primary_emotion && (
                    <span className={`text-xs px-2 py-0.5 rounded-full ${EMOTION_COLORS[j.primary_emotion] || ''} mb-1 inline-block`}>
                      {EMOTION_EMOJI[j.primary_emotion]} {j.primary_emotion}
                    </span>
                  )}
                  <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{j.content}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 전체 기록 리스트 */}
        <div>
          <p className="text-xs text-gray-400 dark:text-gray-500 font-medium mb-3">이달 전체 기록 ({monthCount}개)</p>
          {journalList.length === 0 ? (
            <div className="text-center py-12 text-gray-400 dark:text-gray-600">
              <p className="text-4xl mb-3">📭</p>
              <p className="text-sm">이달 기록이 없습니다</p>
            </div>
          ) : (
            <div className="space-y-3">
              {journalList.map(j => {
                const d = new Date(j.created_at)
                const kst = new Date(d.getTime() + 9 * 60 * 60 * 1000)
                return (
                  <div
                    key={j.id}
                    onClick={() => setDetailJournal(j)}
                    className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700 shadow-sm cursor-pointer hover:border-indigo-200 dark:hover:border-indigo-700 hover:shadow-md transition-all"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-gray-400 dark:text-gray-500">
                        {kst.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric', weekday: 'short' })}
                        {' · '}
                        {kst.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      {j.primary_emotion && (
                        <span className={`text-xs px-2 py-0.5 rounded-full ${EMOTION_COLORS[j.primary_emotion] || ''}`}>
                          {EMOTION_EMOJI[j.primary_emotion]} {j.primary_emotion}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 leading-relaxed">{j.content}</p>
                    <p className="text-xs text-indigo-400 dark:text-indigo-500 mt-2">탭하여 자세히 보기 →</p>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </main>

      {/* 하단 네비게이션 */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 flex">
        <Link href="/" className="flex-1 flex flex-col items-center py-3 text-gray-400 dark:text-gray-500 hover:text-indigo-500 transition">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          <span className="text-xs mt-0.5">홈</span>
        </Link>
        <Link href="/history" className="flex-1 flex flex-col items-center py-3 text-indigo-500 dark:text-indigo-400">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          <span className="text-xs mt-0.5 font-medium">기록</span>
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
