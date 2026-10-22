"""Mocked editor API regression (NOT actual UE physics or screenshot evidence)."""
from pathlib import Path
import json
import tempfile
import probe_unreal_forest as probe
from forest_world_evidence import EXPECTED_MAP

class V:
    def __init__(self, x=0, y=0, z=0): self.x=x;self.y=y;self.z=z
class K:
    @classmethod
    def static_class(cls): return cls
class Start(K): pass
class MeshComp(K):
    def get_static_mesh(self): return "IRLMesh"
    def get_material(self,i): return "IRLPBRMaterial" if i==0 else None
class Hism(K):
    def __init__(self,name,count):self.name=name;self.count=count
    def get_name(self):return self.name
    def get_instance_count(self):return self.count
class Actor:
    def __init__(self,label,klass=object,pos=None,foliage=True):
        self.label=label;self.klass=klass;self.pos=pos or V(20000,0,250)
        self.foliage=foliage
    def get_actor_label(self):return self.label
    def get_class(self):return self.klass
    def get_actor_location(self):return self.pos
    def get_component_by_class(self,klass):return MeshComp() if klass is MeshComp else None
    def get_components_by_class(self,klass):
        if klass is Hism:
            return [Hism("GroundCover",90),Hism("StoneInstances",20),Hism("LeafLitter",35)] if self.foliage else []
        return []
    def get_editor_property(self,key):
        return "IRLSourceAsset" if key in {"ground_cover_mesh","ground_cover_material"} else None
class World:
    def __init__(self):
        self.path=EXPECTED_MAP+"."+EXPECTED_MAP.rsplit("/",1)[-1]
        self.terrain=None
    def get_path_name(self):return self.path
class Editor:
    def __init__(self,w):self.world=w
    def get_editor_world(self):return self.world
class Level:
    def is_in_play_in_editor(self):return False
class ActorSubsystem:
    def __init__(self,actors):self.actors=actors
    def get_all_level_actors(self):return self.actors
class Hit:
    def __init__(self,actor,z=10.0,normal=1.0):self.actor=actor;self.z=z;self.normal=normal
    def get_editor_property(self,key):
        return {
            "hit_actor":self.actor,
            "blocking_hit":True,
            "impact_normal":V(0,0,self.normal),
            "impact_point":V(0,0,self.z),
        }[key]
class Tracer:
    def __init__(self,terrain):self.terrain=terrain;self.missing=False;self.steep=False
    def line_trace_single(self,world,start,end,channel,complex,ignore,draw,ignore_self):
        if self.missing:return None
        return Hit(self.terrain,normal=0.3 if self.steep else 0.98)
class UE:
    PlayerStart=Start
    StaticMeshComponent=MeshComp
    HierarchicalInstancedStaticMeshComponent=Hism
    Vector=V
    class TraceTypeQuery:
        TRACE_TYPE_QUERY1=1
    class DrawDebugTrace:
        NONE=0
    UnrealEditorSubsystem=type("UeSub",(),{})
    LevelEditorSubsystem=type("LevelSub",(),{})
    EditorActorSubsystem=type("ActSub",(),{})
    def __init__(self,folder):
        self._folder=folder
        self.world=World()
        self.terrain=Actor("IRL_OriginalForestTerrain")
        self.actors=[self.terrain]
        self.actors += [Actor(f"IRL_Biome_{i:02d}") for i in range(4)]
        self.actors += [Actor(f"IRL_Granite_{i:02d}") for i in range(14)]
        self.actors += [Actor("Spawn",Start,V(19700,0,600))]
        self.world.terrain=self.terrain
        self.trace=Tracer(self.terrain)
        self.SystemLibrary=self.trace
        self.Paths=type("Paths",(),{"project_saved_dir":lambda *args:str(folder)})
        self.Vector=V
        self.instance_sub=ActorSubsystem(self.actors)
    def get_editor_subsystem(self,cls):
        if cls is self.UnrealEditorSubsystem:return Editor(self.world)
        if cls is self.LevelEditorSubsystem:return Level()
        if cls is self.EditorActorSubsystem:return self.instance_sub
        raise RuntimeError("Unknown subsystem")
    def log(self,text):self.last_log=text

with tempfile.TemporaryDirectory() as temp:
    ue=UE(temp)
    observed=probe.observe_editor(ue)
    assert observed["actor_counts"]=={"terrain":1,"biome":4,"player_start":1}
    assert len(observed["ground_probes"])==14
    assert observed["biome_instances"]["IRL_Biome_01"]["grass"]==90
    ok=probe.main(ue)
    recorded=json.loads(Path(ok).read_text())
    assert recorded["assessment"]["status"]=="EDITOR_REVIEW_ELIGIBLE"
    assert recorded["device"]=="UNREAL_EDITOR_ONLY_NOT_ANDROID"

    ue.trace.missing=True
    try:probe.main(ue)
    except RuntimeError as exc:assert "FAILED" in str(exc)
    else:raise AssertionError("No ground collision wrongly passed")
    last=sorted((Path(temp)/"IRL").glob("forest_editor_audit_*.json"))[-1]
    assert json.loads(last.read_text())["assessment"]["status"]=="NOT_ESTABLISHED"
    ue.trace.missing=False

    ue.trace.steep=True
    try:probe.main(ue)
    except RuntimeError:pass
    else:raise AssertionError("Steep ground passed")
    ue.trace.steep=False

    ue.actors=[a for a in ue.actors if a.get_actor_label()!="IRL_Biome_03"]
    try:probe.main(ue)
    except RuntimeError:pass
    else:raise AssertionError("Missing biome passed")
    ue.actors.append(Actor("IRL_Biome_03"))
    ue.instance_sub.actors=ue.actors

    ue.world.path="/Game/Other/Others.Others"
    try:probe.main(ue)
    except RuntimeError:pass
    else:raise AssertionError("Wrong level passed")
print("PASS 5 mocked editor-probe scenarios; no actual Unreal Engine runtime invoked")
