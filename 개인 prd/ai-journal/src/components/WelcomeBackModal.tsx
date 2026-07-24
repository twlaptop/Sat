'use client'

import { useEffect, useState } from 'react'

type Props = {
  lastJournalDate: string | null
}

function getMessage(days: number) {
  if (days >= 14) return {
    emoji: '💔',
    title: `${days}일 만이에요`,
    desc: '보고 싶었어요. 오늘 하루 어땠나요?\n잠깐이라도 꺼내봐요.',
    btn: '나 왔어요 📔',
  }
  if (days >= 7) return {
    emoji: '🥺',
    title: `일주일이나 지났어요`,
    desc: '그동안 감정이 많이 쌓였을 것 같아요.\n조금이라도 털어놓아 볼까요?',
    btn: '지금 쓸게요',
  }
  return {
    emoji: '😢',
    title: `${days}일 됐네요...`,
    desc: '그동안 많은 일이 있었죠?\nAI가 오늘 감정을 함께 들을게요.',
    btn: '지금 쓸게요',
  }
}

export default function WelcomeBackModal({ lastJournalDate }: Props) {
  const [show, setShow] = useState(false)
  const [days, setDays] = useState(0)

  useEffect(() => {
    if (!lastJournalDate) return

    const last = new Date(lastJournalDate)
    const now = new Date()
    const diff = Math.floor((now.getTime() - last.getTime()) / (1000 * 60 * 60 * 24))

    if (diff >= 3) {
      // 같은 세션에서 이미 보여줬으면 스킵
      const shown = sessionStorage.getItem('welcomeBackShown')
      if (!shown) {
        setDays(diff)
        setShow(true)
        sessionStorage.setItem('welcomeBackShown', '1')
      }
    }
  }, [lastJournalDate])

  if (!show) return null

  const msg = getMessage(days)

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-3xl w-full max-w-sm p-8 text-center shadow-2xl animate-slide-up">
        <div className="text-6xl mb-4">{msg.emoji}</div>
        <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-3">{msg.title}</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed whitespace-pre-line mb-8">
          {msg.desc}
        </p>
        <button
          onClick={() => setShow(false)}
          className="w-full bg-indigo-500 hover:bg-indigo-600 text-white rounded-2xl py-4 font-bold text-sm transition"
        >
          {msg.btn}
        </button>
        <button
          onClick={() => setShow(false)}
          className="mt-3 text-xs text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
        >
          나중에 쓸게요
        </button>
      </div>
    </div>
  )
}
