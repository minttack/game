"""Offline editor API contract tests with an Unreal stub. NOT an Unreal test."""
import build_irl_forest_validation_level as builder

class Actor:
    def __init__(self, klass, location):
        self.klass=klass;self.location=location;self.props={};self.mesh=None
        class Component:
            def __init__(inner): inner.parent=self
            def set_static_mesh(inner,mesh):inner.parent.mesh=mesh
            def set_material(inner,idx,mat):inner.parent.props['material']=mat
        self.component=Component()
    def set_actor_label(self,v):self.label=v
    def get_component_by_class(self,cls):return self.component
    def set_actor_scale3d(self,v):self.scale=v
    def set_editor_property(self,k,v):self.props[k]=v
    def apply_visual_tier(self,v):self.tier=v
    def get_class(self):return self.klass
    def set_actor_location(self,v,sweep,teleport):self.location=v

class Library:
    def __init__(self):self.existing={builder.BASE_MAP}
    def does_asset_exist(self,path):return path in self.existing

class Level:
    def __init__(self,library):self.library=library;self.copied=None;self.saved=False
    def is_in_play_in_editor(self):return False
    def new_level_from_template(self,dest,source):
        assert source==builder.BASE_MAP and dest!=source
        self.library.existing.add(dest);self.copied=(dest,source);return True
    def save_current_level(self):self.saved=True;return True

class Actors:
    def __init__(self,unreal):self.unreal=unreal;self.actors=[Actor(unreal.PlayerStart.static_class(),(0,0,0))]
    def spawn_actor_from_class(self,klass,loc,rot):
        a=Actor(klass,loc);self.actors.append(a);return a
    def get_all_level_actors(self):return self.actors

class Klass:
    @classmethod
    def static_class(cls):return cls

class Stub:
    PlayerStart=type('PlayerStart',(Klass,),{})
    StaticMeshActor=type('StaticMeshActor',(Klass,),{})
    StaticMeshComponent=type('StaticMeshComponent',(Klass,),{})
    DirectionalLight=type('DirectionalLight',(Klass,),{})
    SkyLight=type('SkyLight',(Klass,),{})
    SkyAtmosphere=type('SkyAtmosphere',(Klass,),{})
    Vector=lambda self,*args:tuple(args)
    Rotator=lambda self,**kw:kw
    def __init__(self):
        self.EditorAssetLibrary=Library()
        self.LevelEditorSubsystem=type('LevelEditorSubsystem',(Klass,),{})
        self.EditorActorSubsystem=type('EditorActorSubsystem',(Klass,),{})
        self.level=Level(self.EditorAssetLibrary);self.actors=Actors(self)
    def get_editor_subsystem(self,klass):return self.level if klass==self.LevelEditorSubsystem else self.actors
    def load_asset(self,path):return path if path.startswith(builder.ASSETS) else None
    def load_class(self,unused,name):return name if name==builder.BIOME_CLASS else None
    def log(self,msg):self.message=msg

u=Stub()
assert builder.make(u)==builder.NEW_MAP
assert u.level.copied==(builder.NEW_MAP,builder.BASE_MAP)
assert u.level.saved
labels=[a.label for a in u.actors.actors if hasattr(a,'label')]
assert len(labels)==22,labels
biomes=[a for a in u.actors.actors if 'IRL_Biome_' in getattr(a,'label','')]
assert len(biomes)==4 and all(a.tier==1 for a in biomes)
assert all(a.props['ground_cover_mesh']==builder.ASSETS+'/SM_IRL_GrassClump' for a in biomes)
assert u.actors.actors[0].location[0]>10000
try:builder.make(u)
except RuntimeError as exc:assert 'already exists' in str(exc)
else:raise AssertionError('Original map might be overwritten on rerun')
assert builder.BASE_MAP in u.EditorAssetLibrary.existing
print('PASS editor contract stub: map clone, placements, material props, rerun refusal')
