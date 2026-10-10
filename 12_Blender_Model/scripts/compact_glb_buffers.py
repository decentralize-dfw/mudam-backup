"""Losslessly share identical glTF buffer payloads; retain every view and element ID."""
from pathlib import Path
import copy,hashlib,json,struct,sys

def parse(raw):
    assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
    n,typ=struct.unpack_from('<II',raw,12);assert typ==0x4E4F534A
    doc=json.loads(raw[20:20+n]);size,typ=struct.unpack_from('<II',raw,20+n)
    assert typ==0x004E4942 and 28+n+size==len(raw)
    assert len(doc['buffers'])==1 and 'uri' not in doc['buffers'][0]
    allowed={'KHR_materials_transmission','KHR_materials_emissive_strength','KHR_materials_specular','KHR_materials_ior'}
    assert set(doc.get('extensionsUsed',[]))<=allowed,'Review buffer references in new extensions first'
    return doc,raw[28+n:]

def normalized(doc):
    d=copy.deepcopy(doc);d['buffers'][0].pop('byteLength')
    for v in d['bufferViews']:v.pop('byteOffset',None)
    return d

def verify(source,result):
    a,ab=parse(source);b,bb=parse(result);assert normalized(a)==normalized(b)
    for x,y in zip(a['bufferViews'],b['bufferViews']):
        n=x['byteLength'];i=x.get('byteOffset',0);j=y.get('byteOffset',0)
        assert ab[i:i+n]==bb[j:j+n] and len(bb[j:j+n])==n
    return len(a['bufferViews'])

def compact(raw):
    d,blob=parse(raw);out=bytearray();seen={};duplicates=0;saved=0
    for v in d['bufferViews']:
        assert v.get('buffer',0)==0 and not v.get('extensions')
        i=v.get('byteOffset',0);n=v['byteLength'];data=blob[i:i+n];assert len(data)==n
        key=hashlib.sha256(data).digest()
        if key in seen:
            offset,original=seen[key];assert original==data
            duplicates+=1;saved+=n
        else:
            out.extend(b'\0'*((-len(out))%4));offset=len(out);out.extend(data);seen[key]=(offset,data)
        v['byteOffset']=offset
    d['buffers'][0]['byteLength']=len(out);out.extend(b'\0'*((-len(out))%4))
    header=json.dumps(d,separators=(',',':'),ensure_ascii=False).encode();header+=b' '*((-len(header))%4)
    result=struct.pack('<4sII',b'glTF',2,28+len(header)+len(out))+struct.pack('<II',len(header),0x4E4F534A)+header+struct.pack('<II',len(out),0x004E4942)+out
    count=verify(raw,result)
    return result,dict(buffer_views=count,shared_duplicate_views=duplicates,duplicate_payload_bytes=saved,before_bytes=len(raw),after_bytes=len(result),all_view_payloads_byte_identical=True,all_other_document_fields_identical=True,failures=[])

if __name__=='__main__':
    source,target,receipt=map(Path,sys.argv[1:]);assert not target.exists()
    raw=source.read_bytes();result,info=compact(raw);assert len(result)<len(raw)
    target.write_bytes(result);verify(raw,target.read_bytes())
    info.update(source=str(source),file=str(target),source_sha256=hashlib.sha256(raw).hexdigest(),sha256=hashlib.sha256(result).hexdigest())
    receipt.write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info))
