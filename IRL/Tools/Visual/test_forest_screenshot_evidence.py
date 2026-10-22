"""Source-only screenshot file integrity cases. Not an Unreal rendering test."""
from forest_screenshot_evidence import verify_capture_png
from pathlib import Path
import hashlib
import struct
import tempfile
import zlib

def chunk(kind,data):
    return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data)&0xffffffff)

def make_png(w=1280,h=720):
    # Fake test pixels, deliberately not a screenshot of the game.
    ihdr=struct.pack(">IIBBBBB",w,h,8,2,0,0,0)
    row=b"\x00"+bytes([7,127,213])*(w)
    # Structurally valid RGB raster; repeated rows compress efficiently.
    image=zlib.compress(row*h,level=1)
    return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",ihdr)+chunk(b"IDAT",image)+chunk(b"IEND",b"")

cases=0
with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)/"IRL_First_Actual_Unreal_Forest_1280x720.png"
    good=make_png()
    p.write_bytes(good)
    fact=verify_capture_png(p)
    assert fact["width"]==1280 and fact["height"]==720
    assert fact["sha256"]==hashlib.sha256(good).hexdigest()
    cases+=1
    def bad(bytes_,name):
        global cases
        p.write_bytes(bytes_)
        try:verify_capture_png(p)
        except RuntimeError:pass
        else:raise AssertionError(name+" was accepted")
        cases+=1
    bad(b"notpng","wrong format")
    bad(make_png(1024,768),"wrong dimensions")
    bad(good[:-12],"missing IEND")
    bad(good[:-1],"truncated trailer")
    broken=bytearray(good);broken[60]^=1
    bad(broken,"altered image CRC")
    bad(good+b"not_a_png_chunk","junk after image")
    p.unlink()
    try:verify_capture_png(p)
    except RuntimeError:pass
    else:raise AssertionError("missing screenshot accepted")
    cases+=1
print("PASS",cases,"PNG integrity cases; source-only, NOT actual game rendering")
