#include "Experience/IRLEcologyCore.h"
#include <iostream>
#include <iomanip>
#include <cassert>
using namespace IRLEcology;
struct Metrics {double reward=0;int cycles=0;int consumed=0;int duration=0;};
Metrics Run(const Policy P,int world){
 Habitat H(3,1,42);assert(H.Valid());
 if(world==0){H.SetTile(0,0,Tile{0,0,0,10,false});H.SetTile(1,0,Tile{1,1,1,0,false});H.SetTile(2,0,Tile{0,0,0,0,true});}
 if(world==1){H.SetTile(0,0,Tile{0,0,0,0,true});H.SetTile(1,0,Tile{1,1,1,25,false});H.SetTile(2,0,Tile{0,0,0,0,true});}
 if(world==2){H.SetTile(0,0,Tile{0,0,0,12,false});H.SetTile(1,0,Tile{1,1,3,0,false});H.SetTile(2,0,Tile{0,0,0,0,true});}
 H.AddCreature(1,0,70);Metrics M;
 for(int T=0;T<250;++T){H.Regrow();auto R=H.Step(1,P);if(!R.Valid)break;M.reward+=R.ObservedReward;M.cycles+=1;M.duration=T+1;M.consumed+=R.DidConsumeFood?1:0;}
 return M;
}
int main(){
 for(int S=0;S<3;++S){
   auto A=Run(Policy::BIE,S),F=Run(Policy::AlwaysForage,S),Sh=Run(Policy::AlwaysShelter,S),R=Run(Policy::Random,S);
   std::cout<<"scenario "<<S<<" [BIE,F,S,R] duration "<<A.duration<<"/"<<F.duration<<"/"<<Sh.duration<<"/"<<R.duration
       <<" food "<<A.consumed<<"/"<<F.consumed<<"/"<<Sh.consumed<<"/"<<R.consumed
       <<" normalized reward "<<std::fixed<<std::setprecision(2)<<A.reward<<"/"<<F.reward<<"/"<<Sh.reward<<"/"<<R.reward<<"\n";
 }
}
