// glTF Y is Blender Z. Positive plane distance is the retained side.
export const LEVELS = {all:null, LM1:[-5.65,-0.30], L00:[-0.30,4.60], LP1:[4.60,10.05]};
export function clipEquations(level,axis,offset,reverse=false) {
  const result=[], band=LEVELS[level];
  if(band) result.push([0,1,0,-band[0]],[0,-1,0,band[1]]);
  if(axis!=='none') {
    const sign=reverse?1:-1;
    // North is glTF -Z; input is local northing for the N cut.
    const normal=axis==='H'?[0,sign,0]:axis==='E'?[sign,0,0]:[0,0,-sign];
    result.push([...normal,-sign*offset]);
  }
  return result;
}
export function retained(point,planes) {
  return planes.every(p=>p[0]*point.x+p[1]*point.y+p[2]*point.z+p[3]>=-1e-5);
}
export function sourceIds(data) {
  return [...new Set(Object.entries(data).filter(([k])=>/source.*ids$/.test(k)).flatMap(([,v])=>String(v).split(/[,;\s]+/)).filter(Boolean))];
}
