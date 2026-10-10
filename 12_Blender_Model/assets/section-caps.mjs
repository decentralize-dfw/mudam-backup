import {Vector2,ShapeUtils} from './vendor/three/three.module.js';
// Intersect a closed triangle shell. Open/branched contours are left unfilled.
export function sectionTriangles(positions,indices,plane,epsilon=1e-5) {
  const axis=plane.slice(0,3).findIndex(v=>Math.abs(v)>.5), axes=[0,1,2].filter(i=>i!==axis);
  if(axis<0)throw Error('Axis-aligned section required');
  const points=new Map(),edges=new Map(),adj=new Map();
  const buckets=new Map();
  // Search adjacent cells: rounding alone separates near-identical Boolean vertices
  // when they fall on opposite sides of a quantization boundary.
  const key=p=>{
    const x=p[axes[0]],y=p[axes[1]],ix=Math.floor(x/epsilon),iy=Math.floor(y/epsilon);
    let best,dist=epsilon*epsilon;
    for(let dx=-1;dx<=1;dx++)for(let dy=-1;dy<=1;dy++)for(const k of buckets.get(`${ix+dx},${iy+dy}`)||[]){const q=points.get(k),d=(q[axes[0]]-x)**2+(q[axes[1]]-y)**2;if(d<=dist){best=k;dist=d}}
    if(best!==undefined)return best;
    const k=String(points.size),cell=`${ix},${iy}`;points.set(k,p);if(!buckets.has(cell))buckets.set(cell,[]);buckets.get(cell).push(k);return k;
  };
  const add=(a,b)=>{const ka=key(a),kb=key(b);if(ka===kb)return;const e=[ka,kb].sort().join('|');if(edges.has(e))return;edges.set(e,[ka,kb]);for(const [x,y] of [[ka,kb],[kb,ka]]){if(!adj.has(x))adj.set(x,new Set());adj.get(x).add(y)}};
  const count=indices?.length??positions.length/3;
  for(let i=0;i<count;i+=3){
    const tri=[0,1,2].map(j=>{const v=(indices?indices[i+j]:i+j)*3;return positions.slice(v,v+3)});
    const ab=tri[1].map((v,k)=>v-tri[0][k]),ac=tri[2].map((v,k)=>v-tri[0][k]);
    const twiceArea=Math.hypot(ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]);
    if(twiceArea<=epsilon*Math.max(Math.hypot(...ab),Math.hypot(...ac)))continue;
    const ds=tri.map(p=>p[0]*plane[0]+p[1]*plane[1]+p[2]*plane[2]+plane[3]);
    if(ds.every(d=>Math.abs(d)<epsilon)||ds.every(d=>d>epsilon)||ds.every(d=>d< -epsilon))continue;
    const hits=new Map();
    for(let j=0;j<3;j++){const k=(j+1)%3,a=tri[j],b=tri[k];if(Math.abs(ds[j])<=epsilon)hits.set(key(a),a);if(ds[j]*ds[k]<0){const t=ds[j]/(ds[j]-ds[k]),p=a.map((v,c)=>v+(b[c]-v)*t);hits.set(key(p),p)}}
    if(hits.size===2)add(...hits.values());
  }
  // Boolean triangulation can leave a contour vertex in the middle of another
  // contour segment. Node those T-junctions before testing closed rings.
  const junctions=[...adj.keys()].filter(k=>adj.get(k).size!==2);
  if(junctions.length){
    const split=[];
    for(const [ka,kb] of edges.values()){
      const a=points.get(ka),b=points.get(kb),u=b[axes[0]]-a[axes[0]],v=b[axes[1]]-a[axes[1]],len=u*u+v*v,cuts=[[0,ka],[1,kb]];
      for(const k of junctions){if(k===ka||k===kb)continue;const p=points.get(k),x=p[axes[0]]-a[axes[0]],y=p[axes[1]]-a[axes[1]],t=(x*u+y*v)/len;if(t>0&&t<1&&(x-t*u)**2+(y-t*v)**2<=epsilon*epsilon)cuts.push([t,k])}
      cuts.sort((a,b)=>a[0]-b[0]);for(let i=1;i<cuts.length;i++)split.push([points.get(cuts[i-1][1]),points.get(cuts[i][1])]);
    }
    edges.clear();adj.clear();for(const [a,b] of split)add(a,b);
  }
  // An open spur has no enclosed area. Remove leaves, preserving every cycle;
  // an entirely open contour still produces no cap.
  const leaves=[...adj.keys()].filter(k=>adj.get(k).size<2);let openEdges=0;
  while(leaves.length){const k=leaves.pop(),neighbors=adj.get(k);if(!neighbors||neighbors.size>1)continue;for(const q of neighbors){adj.get(q).delete(k);openEdges++;if(adj.get(q).size<2)leaves.push(q)}adj.delete(k)}
  const seen=new Set(),loops=[],rejected=[];let skipped=openEdges&&adj.size===0?1:0;
  for(const start of adj.keys()){
    if(seen.has(start))continue;const component=[],stack=[start];
    while(stack.length){const k=stack.pop();if(seen.has(k))continue;seen.add(k);component.push(k);for(const q of adj.get(k))if(!seen.has(q))stack.push(q)}
    if(component.some(k=>adj.get(k).size!==2)){skipped++;rejected.push(component.filter(k=>adj.get(k).size!==2).map(k=>({point:points.get(k),degree:adj.get(k).size,neighbors:[...adj.get(k)].map(n=>points.get(n))})));continue}
    const ring=[];let prev=null,cur=start;
    do{ring.push(points.get(cur));const next=[...adj.get(cur)].find(k=>k!==prev);prev=cur;cur=next}while(cur!==start&&ring.length<=component.length);
    if(cur!==start||ring.length<3){skipped++;continue}
    loops.push(ring);
  }
  const inside=(p,ring)=>{let c=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a.y>p.y)!==(b.y>p.y)&&p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x)c=!c}return c};
  const rings=loops.map(r=>r.map(p=>new Vector2(p[axes[0]],p[axes[1]])));
  const depths=rings.map((r,i)=>rings.filter((s,j)=>i!==j&&inside(r[0],s)).length);
  const result=[];
  for(let i=0;i<rings.length;i++){
    if(depths[i]%2)continue;
    const holes=rings.filter((r,j)=>depths[j]===depths[i]+1&&inside(r[0],rings[i]));
    const flat=[...rings[i],...holes.flat()];
    for(const face of ShapeUtils.triangulateShape(rings[i],holes))for(const index of face){const p=[0,0,0];p[axis]=-plane[3]/plane[axis];p[axes[0]]=flat[index].x;p[axes[1]]=flat[index].y;result.push(...p)}
  }
  return {positions:result,loops:loops.length,skipped,rejected,openEdges};
}
