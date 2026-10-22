#include "Experience/IRLEcologyCore.h"
#include <cassert>
#include <iostream>
using namespace IRLEcology;
int main(){
int tests=0;
{
 Habitat H(3,3,12);assert(H.Valid());assert(!H.SetTile(0,0,Tile{3,2,0,0,false}));
 assert(H.SetTile(1,1,Tile{2,2,0,0,false}));assert(H.AddCreature(1,1));
 auto S=H.Step(1,Policy::AlwaysForage);assert(S.Valid&&S.DidConsumeFood&&S.FoodBefore==2&&S.FoodAfter==1);assert(S.EnergyAfter==67);assert(H.TileAt(1,1).Food==1);assert(H.FoodConsumed()==1);++tests;
 auto T=H.Step(1,Policy::AlwaysForage);assert(T.DidConsumeFood&&T.FoodAfter==0);
 auto U=H.Step(1,Policy::AlwaysForage);assert(!U.DidConsumeFood&&U.FoodAfter==0);assert(H.FoodConsumed()==2);++tests;
 H.Regrow();assert(H.TileAt(1,1).Food==0);++tests;
}
{
 Habitat H(2,1,10);assert(H.SetTile(1,0,Tile{0,0,0,24,false}));assert(H.SetTile(0,0,Tile{0,0,0,0,true}));assert(H.AddCreature(1,0,60));
 auto S=H.Step(1,Policy::AlwaysShelter);assert(S.Valid&&S.ToX==0&&S.EnergyAfter==57&&S.Survived);++tests;
 assert(H.SetTile(0,0,Tile{0,0,0,20,true}));auto T=H.Step(1,Policy::AlwaysShelter);assert(T.EnergyAfter==52);++tests;
}
{
 Habitat H(1,1);assert(H.SetTile(0,0,Tile{0,0,0,90,false}));assert(H.AddCreature(0,0,50));
 auto S=H.Step(1);assert(S.Valid&&!S.Survived&&S.EnergyAfter==0);assert(S.ExperienceCyclesAfter==1);assert(!H.Step(1).Valid);++tests;
}
{
 Habitat H(1,1);assert(H.SetTile(0,0,Tile{0,1,1,0,false}));assert(H.AddCreature(0,0,80));
 for(int I=0;I<16;++I){H.StepEveryone();}
 auto *P=H.Find(1);assert(P);assert(P->Experience.Cycles()==16);assert(H.SpawnDescendant(1));auto *Child=H.Find(2);assert(Child&&Child->Experience.Generation()==1&&Child->Experience.Cycles()==0&&Child->Energy==40);assert(H.Find(1)->Energy>=0);++tests;
}
{
 Habitat H(1001,4);assert(!H.Valid());assert(!H.AddCreature(0,0));++tests;
}
{
 Habitat H(1,1);assert(H.SetTile(0,0,Tile{0,1,3,0,false}));H.Regrow();assert(H.TileAt(0,0).Food==0);H.Regrow();assert(H.TileAt(0,0).Food==0);H.Regrow();assert(H.TileAt(0,0).Food==1);H.Regrow();assert(H.TileAt(0,0).Food==1);++tests;
}
{
 Habitat H(3,3);H.SetMaxActive(2);assert(H.AddCreature(0,0));assert(H.AddCreature(1,1));assert(!H.AddCreature(2,2));++tests;
}
std::cout<<"PASS "<<tests<<" ground-truth ecology checks\n";
}
