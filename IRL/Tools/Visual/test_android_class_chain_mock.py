"""Tests UE Blueprint parentage inspection using mock generated-class objects.
No actual Unreal engine or binary BP inspected in this CI.
"""
from pathlib import Path
import tempfile
import json
import audit_android_class_chain as audit

class IRLGameMode: pass
class IRLPlayerController: pass
class IRLCharacter: pass
class WrongController: pass
class WrongPawn: pass

class Klass:
    def __init__(self,path,obj):
        self.path=path
        self.obj=obj
    def get_path_name(self):return self.path

class Game(IRLGameMode):
    def __init__(self,controller,pawn):
        self.controller=controller
        self.pawn=pawn
    def get_editor_property(self,key):
        return {"player_controller_class":self.controller,
                "default_pawn_class":self.pawn}[key]

class Unreal:
    IRLGameMode=IRLGameMode
    IRLPlayerController=IRLPlayerController
    IRLCharacter=IRLCharacter
    def __init__(self,folder,bad=""):
        self.folder=folder;self.bad=bad
        self.controller=Klass("IRLController",WrongController() if bad=="controller" else IRLPlayerController())
        self.pawn=Klass("IRLCharacter",WrongPawn() if bad=="pawn" else IRLCharacter())
        self.game=Klass(audit.GAME_MODE_CLASS,Game(self.controller,self.pawn))
        if bad=="mode":self.game=Klass(audit.GAME_MODE_CLASS,object())
        self.Paths=type("Paths",(),{"project_saved_dir":lambda *args:str(folder)})
    def load_class(self,outer,path):
        assert path==audit.GAME_MODE_CLASS
        return None if self.bad=="missing" else self.game
    def get_default_object(self,klass):return klass.obj
    def log(self,s):self.last_log=s

cases=0
with tempfile.TemporaryDirectory() as p:
    u=Unreal(p)
    r=audit.inspect_chain(u)
    assert r["status"]=="EDITOR_CLASS_CHAIN_REVIEW_ELIGIBLE"
    assert r["checks"]=={"irl_game_mode":True,"irl_controller":True,"irl_character":True}
    path=audit.main(u)
    assert json.loads(Path(path).read_text())["status"]=="EDITOR_CLASS_CHAIN_REVIEW_ELIGIBLE"
    cases+=1
for reason in ("missing","controller","pawn","mode"):
    with tempfile.TemporaryDirectory() as p:
        u=Unreal(p,reason)
        outcome=audit.inspect_chain(u)
        assert outcome["status"]=="NOT_ESTABLISHED",reason
        try:audit.main(u)
        except RuntimeError:pass
        else:raise AssertionError("Incorrect Blueprint class chain accepted: "+reason)
        cases+=1
print("PASS",cases,"UE mobile Blueprint inheritance mock checks, no Unreal engine executed")
