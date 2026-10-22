"""IRL source-only UE editor API contract tests. NOT an Unreal runtime test."""
import build_irl_forest_validation_level as builder

class Body:
    def __init__(self): self.flag="default"
    def get_editor_property(self,key):
        assert key=="collision_trace_flag"
        return self.flag
    def set_editor_property(self,key,value):
        assert key=="collision_trace_flag"
        self.flag=value

class Mesh:
    def __init__(self): self.body=Body()
    def get_editor_property(self,key):
        assert key=="body_setup"
        return self.body

class Actor:
    def __init__(self,klass,location):
        self.klass=klass;self.location=location;self.props={};self.mesh=None
        class Component:
            def __init__(inner):inner.parent=self;inner.profile="NoCollision"
            def set_static_mesh(inner,mesh):inner.parent.mesh=mesh
            def set_material(inner,idx,mat):inner.parent.props["material"]=mat
            def set_collision_profile_name(inner,profile):inner.profile=profile
            def get_collision_profile_name(inner):return inner.profile
        self.component=Component()
    def set_actor_label(self,v):self.label=v
    def get_component_by_class(self,cls):return self.component
    def set_actor_scale3d(self,v):self.scale=v
    def set_editor_property(self,k,v):self.props[k]=v
    def apply_visual_tier(self,v):self.tier=v
    def get_class(self):return self.klass
    def set_actor_location(self,v,sweep,teleport):self.location=v

class Library:
    def __init__(self):self.existing={builder.BASE_MAP};self.saved=0;self.directories=[]
    def does_asset_exist(self,path):return path in self.existing
    def make_directory(self,path):self.directories.append(path)
    def save_loaded_asset(self,mesh):self.saved+=1;return True

class Level:
    def __init__(self,library):self.library=library;self.copied=None;self.saved=False
    def is_in_play_in_editor(self):return False
    def new_level_from_template(self,dest,source):
        assert source==builder.BASE_MAP and dest!=source
        self.library.existing.add(dest);self.copied=(dest,source);return True
    def save_current_level(self):self.saved=True;return True

class Actors:
    def __init__(self,unreal):
        self.unreal=unreal;self.actors=[Actor(unreal.PlayerStart.static_class(),(0,0,0))]
    def spawn_actor_from_class(self,klass,loc,rot):
        a=Actor(klass,loc);self.actors.append(a);return a
    def get_all_level_actors(self):return self.actors

class Klass:
    @classmethod
    def static_class(cls):return cls

class Stub:
    PlayerStart=type("PlayerStart",(Klass,),{})
    StaticMeshActor=type("StaticMeshActor",(Klass,),{})
    StaticMeshComponent=type("StaticMeshComponent",(Klass,),{})
    DirectionalLight=type("DirectionalLight",(Klass,),{})
    SkyLight=type("SkyLight",(Klass,),{})
    SkyAtmosphere=type("SkyAtmosphere",(Klass,),{})
    CollisionTraceFlag=type("CollisionTraceFlag",(),{"CTF_USE_COMPLEX_AS_SIMPLE":"complex_as_simple"})
    Vector=lambda self,*args:tuple(args)
    Rotator=lambda self,**kw:kw
    def __init__(self):
        self.EditorAssetLibrary=Library()
        self.LevelEditorSubsystem=type("LevelEditorSubsystem",(Klass,),{})
        self.EditorActorSubsystem=type("EditorActorSubsystem",(Klass,),{})
        self.level=Level(self.EditorAssetLibrary)
        self.actors=Actors(self)
        self.terrain_mesh=Mesh()
    def get_editor_subsystem(self,klass):return self.level if klass==self.LevelEditorSubsystem else self.actors
    def load_asset(self,path):
        if path==builder.ASSETS+"/SM_IRL_TerrainPatch":return self.terrain_mesh
        return path if path.startswith(builder.ASSETS) else None
    def load_class(self,unused,name):return name if name==builder.BIOME_CLASS else None
    def log(self,msg):self.message=msg

u=Stub()
assert builder.make(u)==builder.NEW_MAP
assert u.level.copied==(builder.NEW_MAP,builder.BASE_MAP)
assert u.level.saved
assert u.EditorAssetLibrary.saved==1
assert u.terrain_mesh.body.flag=="complex_as_simple"
assert "/Game/IRL/Maps" in u.EditorAssetLibrary.directories
labels=[a.label for a in u.actors.actors if hasattr(a,"label")]
assert len(labels)==22,labels
biomes=[a for a in u.actors.actors if "IRL_Biome_" in getattr(a,"label","")]
assert len(biomes)==4 and all(a.tier==1 for a in biomes)
assert all(a.props["ground_cover_mesh"]==builder.ASSETS+"/SM_IRL_GrassClump" for a in biomes)
terrain_actors=[a for a in u.actors.actors if getattr(a,"label",None)=="IRL_OriginalForestTerrain"]
assert len(terrain_actors)==1
assert terrain_actors[0].component.profile=="BlockAll"
assert u.actors.actors[0].location[0]>10000
try:builder.make(u)
except RuntimeError as exc:assert "already exists" in str(exc)
else:raise AssertionError("Original map might be overwritten on rerun")
assert u.EditorAssetLibrary.saved==1
assert builder.BASE_MAP in u.EditorAssetLibrary.existing

broken=Stub()
broken.terrain_mesh.body=None
try:builder.make(broken)
except RuntimeError as exc:assert "no BodySetup" in str(exc)
else:raise AssertionError("Missing collision was accepted")
assert broken.level.copied is None
assert builder.NEW_MAP not in broken.EditorAssetLibrary.existing
print("PASS editor contract stub: clone, source collision readback, fail-before-clone, decor, no-overwrite")
