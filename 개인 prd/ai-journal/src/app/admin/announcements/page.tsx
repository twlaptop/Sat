import { createClient } from '@/lib/supabase/server'
import { createAnnouncement, deleteAnnouncement, toggleAnnouncement } from './actions'

export default async function AnnouncementsPage() {
  const supabase = await createClient()
  const { data: announcements } = await supabase
    .from('announcements').select('*').order('priority', { ascending: false })

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-8">
      <h1 className="text-xl font-bold">공지사항 관리</h1>

      <form action={createAnnouncement} className="space-y-3 border rounded-lg p-4">
        <h2 className="font-semibold">새 공지 작성</h2>
        <input name="title" placeholder="제목" required
          className="w-full border rounded px-3 py-2 text-sm" />
        <textarea name="content" placeholder="내용" required rows={3}
          className="w-full border rounded px-3 py-2 text-sm" />
        <div className="flex gap-2 flex-wrap">
          <input name="priority" type="number" placeholder="우선순위" defaultValue={0}
            className="w-28 border rounded px-3 py-2 text-sm" />
          <input name="starts_at" type="datetime-local"
            className="border rounded px-3 py-2 text-sm" />
          <input name="ends_at" type="datetime-local"
            className="border rounded px-3 py-2 text-sm" />
        </div>
        <button type="submit"
          className="bg-black text-white px-4 py-2 rounded text-sm">등록</button>
      </form>

      <div className="space-y-3">
        {announcements?.map(a => (
          <div key={a.id} className="border rounded-lg p-4 flex justify-between items-start gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className={`text-xs px-2 py-0.5 rounded-full ${a.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                  {a.is_active ? '활성' : '비활성'}
                </span>
                <span className="text-xs text-gray-400">우선순위 {a.priority}</span>
              </div>
              <p className="font-medium mt-1">{a.title}</p>
              <p className="text-sm text-gray-600 mt-0.5">{a.content}</p>
            </div>
            <div className="flex flex-col gap-1 shrink-0">
              <form action={toggleAnnouncement.bind(null, a.id, a.is_active)}>
                <button type="submit" className="text-xs border rounded px-2 py-1 w-full">
                  {a.is_active ? '숨기기' : '활성화'}
                </button>
              </form>
              <form action={deleteAnnouncement.bind(null, a.id)}>
                <button type="submit" className="text-xs border border-red-200 text-red-500 rounded px-2 py-1 w-full">
                  삭제
                </button>
              </form>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
