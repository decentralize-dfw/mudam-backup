export function summarize(values) {
  if (!values.length || values.some(v => !Number.isFinite(v) || v < 0)) throw Error('Invalid timing samples');
  const sorted = [...values].sort((a,b) => a-b);
  const quantile = p => sorted[Math.min(sorted.length-1, Math.ceil(p*sorted.length)-1)];
  return {count:values.length, mean:values.reduce((a,b)=>a+b,0)/values.length,
    p50:quantile(.5), p95:quantile(.95), min:sorted[0], max:sorted.at(-1)};
}

// Browser frame delivery and JS render submission, not a GPU timer query.
export async function sampleRendering({render, frame, signature, hidden, duration=10000, warmup=2000}) {
  const initial=signature(), intervals=[], submission=[], calls=[], triangles=[];
  let start, previous;
  while (true) {
    const now=await new Promise(requestAnimationFrame);
    if (hidden() || signature()!==initial) throw Error('Görünüm değişti veya sekme gizlendi; ölçüm iptal edildi.');
    start??=now;
    const elapsed=now-start;
    if(elapsed>=warmup+duration) break;
    frame(elapsed/(warmup+duration));
    const t=performance.now(), info=render(), ms=performance.now()-t;
    if(elapsed>=warmup && previous!==undefined) {
      intervals.push(now-previous); submission.push(ms);
      calls.push(info.calls); triangles.push(info.triangles);
    }
    previous=now;
  }
  if(intervals.length<3) throw Error('Ölçüm için yeterli kare üretilemedi.');
  return {warmup_ms:warmup, requested_sample_ms:duration,
    frame_interval_ms:summarize(intervals), render_submission_ms:summarize(submission),
    delivered_fps:1000/summarize(intervals).mean,
    draw_calls:summarize(calls), submitted_triangles:summarize(triangles)};
}
