export const config = { runtime: 'edge' }
export default async function handler(req: Request) {
  const base = process.env.ODOO_BASE_URL || ''
  if (!/^https?:\/\//.test(base)) {
    return new Response(JSON.stringify({ ok:false, error:'INVALID_BASE_URL', base }), { status: 500, headers:{'Content-Type':'application/json'} })
  }
  const res = await fetch(`${base}/web/health`, { headers:{'Accept':'application/json'} })
  const text = await res.text()
  let data:any
  try { data = JSON.parse(text) } catch { data = { html:true, text } }
  return new Response(JSON.stringify({ ok: res.ok, status: res.status, data }), {
    headers:{ 'Content-Type':'application/json', 'Cache-Control':'no-cache, no-transform' }
  })
}
