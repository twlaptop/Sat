'use client'

import { useState } from 'react'

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
  기쁨: '😊', 스트레스: '😤', 무기력: '😔', 성취감: '🎉',
  불안: '😰', 혼란: '😵', 외로움: '🥺', 설렘: '🤩',
}

const EMOTION_COLORS: Record<string, string> = {
  기쁨: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
  스트레스: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
  무기력: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
  성취감: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
  불안: 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300',
  혼란: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300',
  외로움: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
  설렘: 'bg-pink-100 text-pink-700 dark:bg-pink-900 dark:text-pink-300',
}

export default function JournalDetailModal({
  journal,
  onClose,
  onDelete,
}: {
  journal: Journal
  onClose: () => void
  onDelete: (id: string) => void
}) {
  const [confirming, setConfirming] = useState(false)
  const [deleting, setDeleting] = useState(false)

  const handleDelete = async () => {
    setDeleting(true)
    const res = await fetch(`/api/journal/${journal.id}`, { method: 'DELETE' })
    if (res.ok) {
      onDelete(journal.id)
      onClose()
    }
    setDeleting(false)
  }

  const kst = new Date(new Date(journal.created_at).getTime() + 9 * 60 * 60 * 1000)

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-gray-800 rounded-3xl w-full max-w-lg max-h-[85vh] overflow-y-auto animate-slide-up"
        onClick={e => e.stopPropagation()}
      >
        {/* 헤더 */}
        <div className="flex items-center justify-between p-5 border-b border-gray-100 dark:border-gray-700 sticky top-0 bg-white dark:bg-gray-800 rounded-t-3xl">
          <div>
            <p className="text-sm font-medium text-gray-800 dark:text-white">
              {kst.toLocaleDateString('ko-KR', { month: 'long', day: 'numeric', weekday: 'long' })}
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
              {kst.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600 text-lg"
          >
            ×
          </button>
        </div>

        <div className="p-5 space-y-5">
          {/* 감정 태그 */}
          {journal.emotion_tags?.length > 0 && (
            <div className="flex gap-2 flex-wrap">
              {journal.emotion_tags.map(tag => (
                <span key={tag} className={`px-3 py-1.5 rounded-full text-sm font-medium ${EMOTION_COLORS[tag] || 'bg-indigo-100 text-indigo-700'}`}>
                  {EMOTION_EMOJI[tag]} {tag}
                </span>
              ))}
            </div>
          )}

          {/* 원문 */}
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-2xl p-4">
            <p className="text-xs text-gray-400 dark:text-gray-500 mb-2 font-medium">오늘의 기록</p>
            <p className="text-sm text-gray-700 dark:text-gray-200 leading-relaxed whitespace-pre-wrap">
              {journal.content}
            </p>
          </div>

          {/* AI 한마디 */}
          {journal.ai_comment && (
            <div className="bg-indigo-50 dark:bg-indigo-900/40 rounded-2xl p-4 border border-indigo-100 dark:border-indigo-800">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-base">🤖</span>
                <span className="text-xs font-medium text-indigo-600 dark:text-indigo-400">AI 한마디</span>
              </div>
              <p className="text-sm text-gray-700 dark:text-gray-200 leading-relaxed">{journal.ai_comment}</p>
            </div>
          )}

          {/* 감정 원인 분석 */}
          {journal.ai_cause && (
            <div className="bg-white dark:bg-gray-700/50 rounded-2xl p-4 border border-gray-100 dark:border-gray-600">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-base">🔍</span>
                <span className="text-xs font-medium text-gray-500 dark:text-gray-400">감정 원인 분석</span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{journal.ai_cause}</p>
            </div>
          )}

          {/* 해결방안 */}
          {journal.ai_solutions && journal.ai_solutions.length > 0 && (
            <div className="bg-white dark:bg-gray-700/50 rounded-2xl p-4 border border-gray-100 dark:border-gray-600">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-base">💡</span>
                <span className="text-xs font-medium text-gray-500 dark:text-gray-400">오늘 해볼 수 있는 것</span>
              </div>
              <div className="space-y-2">
                {journal.ai_solutions.map((s, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <span className="text-indigo-400 font-bold text-sm mt-0.5">{i + 1}.</span>
                    <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{s}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI 회고 질문 + 답변 */}
          {journal.ai_questions?.length > 0 && (
            <div>
              <p className="text-xs text-gray-400 dark:text-gray-500 mb-3 font-medium">🤖 AI 회고 질문</p>
              <div className="space-y-3">
                {journal.ai_questions.map((q, i) => {
                  const answer = journal.reflection_answers?.[i]
                  return (
                    <div key={i} className="rounded-xl overflow-hidden border border-indigo-100 dark:border-indigo-800">
                      <div className="bg-indigo-50 dark:bg-indigo-900/30 px-4 py-3 border-l-2 border-indigo-400">
                        <p className="text-xs text-indigo-500 dark:text-indigo-400 font-medium mb-1">Q{i + 1}</p>
                        <p className="text-sm text-gray-700 dark:text-gray-200 leading-relaxed">{q}</p>
                      </div>
                      {answer && (
                        <div className="bg-white dark:bg-gray-700/50 px-4 py-3 border-l-2 border-gray-200 dark:border-gray-600">
                          <p className="text-xs text-gray-400 dark:text-gray-500 font-medium mb-1">내 답변</p>
                          <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{answer}</p>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}
          {/* 삭제 버튼 */}
          <div className="pt-2 pb-2">
            {!confirming ? (
              <button
                onClick={() => setConfirming(true)}
                className="w-full py-3 text-sm text-red-400 hover:text-red-500 border border-red-100 dark:border-red-900 hover:border-red-200 rounded-xl transition"
              >
                이 기록 삭제하기
              </button>
            ) : (
              <div className="space-y-2">
                <p className="text-sm text-center text-gray-500 dark:text-gray-400">정말 삭제할까요? 되돌릴 수 없어요.</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setConfirming(false)}
                    className="flex-1 py-3 text-sm border border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    취소
                  </button>
                  <button
                    onClick={handleDelete}
                    disabled={deleting}
                    className="flex-1 py-3 text-sm bg-red-500 hover:bg-red-600 text-white rounded-xl transition disabled:opacity-50"
                  >
                    {deleting ? '삭제 중...' : '삭제'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
