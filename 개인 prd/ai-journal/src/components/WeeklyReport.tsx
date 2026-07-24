'use client'

import Link from 'next/link'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

type Journal = {
  id: string
  content: string
  primary_emotion: string | null
  emotion_tags: string[]
  created_at: string
}

const EMOTION_EMOJI: Record<string, string> = {
  기쁨: '😊', 스트레스: '😤', 무기력: '😔', 성취감: '🎉',
  불안: '😰', 혼란: '😵', 외로움: '🥺', 설렘: '🤩',
}

const EMOTION_COLOR: Record<string, string> = {
  기쁨: '#FBBF24', 스트레스: '#F87171', 무기력: '#9CA3AF',
  성취감: '#34D399', 불안: '#FB923C', 혼란: '#A78BFA',
  외로움: '#60A5FA', 설렘: '#F472B6',
}

const DAY_LABELS = ['월', '화', '수', '목', '금', '토', '일']

const WEEKLY_COMMENTS: Record<string, string> = {
  스트레스: '이번 주 많이 지치셨네요. 다음 주엔 나를 위한 시간을 조금 더 챙겨보세요.',
  기쁨: '이번 주 좋은 에너지가 가득했어요! 이 기분을 기억해 두세요.',
  무기력: '이번 주 의욕이 낮았던 한 주였어요. 작은 것부터 다시 시작해봐요.',
  성취감: '이번 주 정말 잘 해내셨어요! 스스로를 칭찬해줄 만한 한 주였습니다.',
  불안: '이번 주 걱정이 많으셨군요. 내가 통제할 수 있는 것에만 집중해봐요.',
  혼란: '이번 주 머릿속이 복잡했던 것 같아요. 한 가지씩 정리해가다 보면 길이 보일 거예요.',
  외로움: '이번 주 혼자라는 느낌이 많이 드셨군요. 작은 연결을 먼저 시도해봐요.',
  설렘: '이번 주 설레는 일들이 있었군요! 그 에너지를 잘 활용해봐요.',
}

export default function WeeklyReport({
  journals,
  lastWeekJournals,
  weekStart,
}: {
  journals: Journal[]
  lastWeekJournals: { primary_emotion: string | null }[]
  weekStart: string
}) {
  const monday = new Date(weekStart)

  // 요일별 데이터 생성
  const chartData = DAY_LABELS.map((label, i) => {
    const date = new Date(monday)
    date.setDate(monday.getDate() + i)
    const dateStr = date.toISOString().split('T')[0]

    const dayJournals = journals.filter(j => {
      const kst = new Date(new Date(j.created_at).getTime() + 9 * 60 * 60 * 1000)
      return kst.toISOString().split('T')[0] === dateStr
    })

    const emotion = dayJournals[0]?.primary_emotion || null
    return {
      day: label,
      count: dayJournals.length,
      emotion,
      emoji: emotion ? EMOTION_EMOJI[emotion] : '',
      color: emotion ? EMOTION_COLOR[emotion] : '#374151',
    }
  })

  // 이번 주 감정 집계
  const emotionCount: Record<string, number> = {}
  journals.forEach(j => {
    if (j.primary_emotion) emotionCount[j.primary_emotion] = (emotionCount[j.primary_emotion] || 0) + 1
  })
  const topEmotion = Object.entries(emotionCount).sort((a, b) => b[1] - a[1])[0]?.[0]

  // 지난 주 감정
  const lastEmotionCount: Record<string, number> = {}
  lastWeekJournals.forEach(j => {
    if (j.primary_emotion) lastEmotionCount[j.primary_emotion] = (lastEmotionCount[j.primary_emotion] || 0) + 1
  })
  const lastTopEmotion = Object.entries(lastEmotionCount).sort((a, b) => b[1] - a[1])[0]?.[0]

  const weekComment = topEmotion ? WEEKLY_COMMENTS[topEmotion] : '이번 주 기록이 없어요. 오늘부터 시작해봐요!'

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 transition-colors">
      {/* 헤더 */}
      <header className="flex items-center justify-between px-5 pt-6 pb-4 max-w-lg mx-auto">
        <div className="flex items-center gap-2">
          <span className="text-2xl">📊</span>
          <span className="font-bold text-gray-800 dark:text-white text-lg">주간 리포트</span>
        </div>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {monday.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })} ~{' '}
          {new Date(monday.getTime() + 6 * 24 * 60 * 60 * 1000).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
        </span>
      </header>

      <main className="max-w-lg mx-auto px-5 pb-24 space-y-5">
        {/* 이번 주 요약 카드 */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 text-center border border-gray-100 dark:border-gray-700 shadow-sm">
            <p className="text-2xl font-bold text-indigo-500">{journals.length}</p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">이번 주 기록</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 text-center border border-gray-100 dark:border-gray-700 shadow-sm">
            <p className="text-2xl">{topEmotion ? EMOTION_EMOJI[topEmotion] : '—'}</p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">{topEmotion || '감정 없음'}</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 text-center border border-gray-100 dark:border-gray-700 shadow-sm">
            <p className="text-2xl">{lastTopEmotion ? EMOTION_EMOJI[lastTopEmotion] : '—'}</p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">지난 주</p>
          </div>
        </div>

        {/* 감정 흐름 그래프 */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700 shadow-sm">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-200 mb-4">이번 주 감정 흐름</p>
          {journals.length === 0 ? (
            <div className="text-center py-8 text-gray-400 dark:text-gray-600">
              <p className="text-3xl mb-2">📭</p>
              <p className="text-sm">이번 주 기록이 없어요</p>
            </div>
          ) : (
            <>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={chartData} barSize={28}>
                  <XAxis
                    dataKey="day"
                    tick={{ fontSize: 12, fill: '#9CA3AF' }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis hide />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (!active || !payload?.length) return null
                      const d = payload[0].payload
                      return (
                        <div className="bg-white dark:bg-gray-700 rounded-xl px-3 py-2 shadow-lg text-xs">
                          <p className="font-medium text-gray-800 dark:text-white">{d.day}요일</p>
                          {d.emotion && <p className="text-gray-500 dark:text-gray-400">{d.emoji} {d.emotion}</p>}
                          <p className="text-indigo-500">{d.count}개 기록</p>
                        </div>
                      )
                    }}
                  />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {chartData.map((entry, i) => (
                      <Cell key={i} fill={entry.count > 0 ? entry.color : '#E5E7EB'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>

              {/* 요일별 감정 이모지 */}
              <div className="grid grid-cols-7 gap-1 mt-2">
                {chartData.map((d, i) => (
                  <div key={i} className="text-center text-lg">
                    {d.emoji || ''}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* AI 주간 요약 */}
        <div className="bg-indigo-50 dark:bg-indigo-900/40 rounded-2xl p-5 border border-indigo-100 dark:border-indigo-800">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">🤖</span>
            <span className="text-xs font-medium text-indigo-600 dark:text-indigo-400">AI 주간 한마디</span>
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-200 leading-relaxed">{weekComment}</p>
        </div>

        {/* 감정 분포 */}
        {Object.keys(emotionCount).length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-100 dark:border-gray-700 shadow-sm">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-200 mb-4">이번 주 감정 분포</p>
            <div className="space-y-2">
              {Object.entries(emotionCount)
                .sort((a, b) => b[1] - a[1])
                .map(([emotion, count]) => (
                  <div key={emotion} className="flex items-center gap-3">
                    <span className="text-sm w-20 text-gray-600 dark:text-gray-300 flex items-center gap-1">
                      {EMOTION_EMOJI[emotion]} {emotion}
                    </span>
                    <div className="flex-1 bg-gray-100 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="h-2 rounded-full transition-all"
                        style={{
                          width: `${(count / journals.length) * 100}%`,
                          backgroundColor: EMOTION_COLOR[emotion],
                        }}
                      />
                    </div>
                    <span className="text-xs text-gray-400 dark:text-gray-500 w-6 text-right">{count}</span>
                  </div>
                ))}
            </div>
          </div>
        )}
      </main>

      {/* 하단 네비게이션 */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 flex">
        <Link href="/" className="flex-1 flex flex-col items-center py-3 text-gray-400 dark:text-gray-500 hover:text-indigo-500 transition">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          <span className="text-xs mt-0.5">홈</span>
        </Link>
        <Link href="/history" className="flex-1 flex flex-col items-center py-3 text-gray-400 dark:text-gray-500 hover:text-indigo-500 transition">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          <span className="text-xs mt-0.5">기록</span>
        </Link>
        <Link href="/report" className="flex-1 flex flex-col items-center py-3 text-indigo-500 dark:text-indigo-400">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
          </svg>
          <span className="text-xs mt-0.5 font-medium">리포트</span>
        </Link>
      </nav>
    </div>
  )
}
