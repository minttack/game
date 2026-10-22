"""Standalone proof that a screenshot file is a complete readable PNG.

Does NOT prove Unreal drew the content. Provenance is established separately
by running the screenshot request inside the original Unreal Editor.
"""
from pathlib import Path
import hashlib
import struct
import zlib

PNG_MAGIC=b"\x89PNG\r\n\x1a\n"
MAX_BYTES=64*1024*1024

def verify_capture_png(path, expected=(1280,720)):
    p=Path(path)
    if not p.is_file() or p.stat().st_size > MAX_BYTES:
        raise RuntimeError("No readable or reasonably sized screenshot file")
    raw=p.read_bytes()
    if len(raw)<1024 or not raw.startswith(PNG_MAGIC):
        raise RuntimeError("Screenshot missing PNG signature or incomplete")
    offset=8
    count=0
    width=height=0
    has_idat=False
    ended=False
    while offset+12<=len(raw):
        size=struct.unpack(">I",raw[offset:offset+4])[0]
        typ=raw[offset+4:offset+8]
        end=offset+12+size
        if size > MAX_BYTES or end>len(raw):
            raise RuntimeError("Truncated or oversized PNG chunk")
        data=raw[offset+8:offset+8+size]
        stored=struct.unpack(">I",raw[offset+8+size:end])[0]
        actual=zlib.crc32(typ+data)&0xffffffff
        if stored!=actual:
            raise RuntimeError("PNG chunk checksum failure")
        if count==0:
            if typ!=b"IHDR" or size!=13:
                raise RuntimeError("First PNG chunk must be IHDR")
            width,height=struct.unpack(">II",data[:8])
            if (width,height)!=tuple(expected):
                raise RuntimeError("Screenshot resolution mismatch")
        if typ==b"IDAT":has_idat=True
        if typ==b"IEND":
            if size!=0 or end!=len(raw):
                raise RuntimeError("PNG IEND malformed or trailing bytes")
            ended=True
            break
        offset=end
        count+=1
        if count>100000:
            raise RuntimeError("Excess PNG chunk count")
    if not has_idat or not ended:
        raise RuntimeError("Incomplete PNG image data or trailer")
    return {
        "width":width,"height":height,"bytes":len(raw),
        "sha256":hashlib.sha256(raw).hexdigest(),
        "verified_format":"PNG_VALID_CHUNKS_AND_CRC_NOT_SEMANTIC_IMAGE_CONTENT",
    }
