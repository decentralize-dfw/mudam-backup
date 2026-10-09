import assert from 'node:assert/strict';
import {clipEquations,retained,sourceIds} from '../assets/viewer-core.mjs';
for(const [level,inside,outside] of [['LM1',-4,1],['L00',2,6],['LP1',6,2]]) {
  assert(retained({x:0,y:inside,z:0},clipEquations(level,'none',0)));
  assert(!retained({x:0,y:outside,z:0},clipEquations(level,'none',0)));
}
for(const axis of ['H','E','N']) {
  const p=axis==='H'?{x:0,y:3,z:0}:axis==='E'?{x:3,y:0,z:0}:{x:0,y:0,z:-3};
  assert(retained(p,clipEquations('all',axis,4)));
  assert(!retained(p,clipEquations('all',axis,4,true)));
}
assert(!retained({x:0,y:4.4,z:0},clipEquations('L00','H',1.5)),'Clipped ceiling must not intercept picking');
assert(retained({x:0,y:0,z:0},clipEquations('L00','H',1.5)),'Visible floor remains selectable');
assert.deepEqual(sourceIds({source_ids:'023,024',surface_source_ids:'024,101'}),['023','024','101']);
console.log('P20: floor bands, glTF Y-up, north sign, reverse plane and clipped selection checks passed');
