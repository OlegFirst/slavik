export const config = { runtime: 'edge' }
export default async function handler(req: Request) {
  const { searchParams } = new URL(req.url)
  const tenant = searchParams.get('tenant') || 'default'
  const stream = new ReadableStream({
    start(controller) {
      const enc = (s:string)=>controller.enqueue(new TextEncoder().encode(s))
      enc(`retry: 2000\n\n`)
      const ping = setInterval(()=>enc(`: ping\n\n`), 15000)
      // TODO: подписка на реальные события → enc(`data: ${JSON.stringify(payload)}\n\n`)
      const close = ()=>{ clearInterval(ping); controller.close() }
      // @ts-ignore
      req.signal?.addEventListener?.('abort', close)
    }
  })
  return new Response(stream, {
    headers: {
      'Content-Type':'text/event-stream',
      'Cache-Control':'no-cache, no-transform',
      'Connection':'keep-alive',
      'X-Accel-Buffering':'no'
    }
  })
}
