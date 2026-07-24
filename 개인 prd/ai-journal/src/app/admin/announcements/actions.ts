'use server'
import { createClient } from '@/lib/supabase/server'
import { revalidatePath } from 'next/cache'

export async function createAnnouncement(formData: FormData) {
  const supabase = await createClient()
  await supabase.from('announcements').insert({
    title: formData.get('title') as string,
    content: formData.get('content') as string,
    priority: Number(formData.get('priority') || 0),
    starts_at: formData.get('starts_at') || null,
    ends_at: formData.get('ends_at') || null,
  })
  revalidatePath('/admin/announcements')
}

export async function deleteAnnouncement(id: string) {
  const supabase = await createClient()
  await supabase.from('announcements').delete().eq('id', id)
  revalidatePath('/admin/announcements')
}

export async function toggleAnnouncement(id: string, isActive: boolean) {
  const supabase = await createClient()
  await supabase.from('announcements').update({ is_active: !isActive }).eq('id', id)
  revalidatePath('/admin/announcements')
}
