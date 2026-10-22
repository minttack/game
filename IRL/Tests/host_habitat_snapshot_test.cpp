#include "Experience/IRLHabitatSnapshotCore.h"
#include <cassert>
#include <iostream>
#include <limits>
using namespace IRLHabitatNet;
int main()
{
    int Passed=0;
    { Frame F;F.Sequence=1;F.Width=12;F.Height=12;
      assert(AddFood(F,2,8)); assert(AddCreature(F,42,11,11));
      assert(Validate(F));assert(IsNewer(0,F));assert(!IsNewer(1,F));
      int X=-1,Y=-1;assert(DecodeCell(12,12,F.CreatureCells[0],X,Y));assert(X==11&&Y==11);
      ++Passed; }
    { Frame F;F.Sequence=1;F.Width=32;F.Height=32;
      for(int Y=0;Y<32;++Y)for(int X=0;X<32;++X)assert(AddFood(F,X,Y));
      for(int I=0;I<40;++I) assert(AddCreature(F,I+1,I%32,I/32));
      assert(Validate(F));assert(EstimatedBytes(F)<=MaxSnapshotBytes);
      assert(!AddFood(F,0,0));assert(!AddCreature(F,1,0,0));assert(!AddCreature(F,41,0,0));
      ++Passed; }
    { Frame F;F.Sequence=1;F.Width=8;F.Height=8;assert(!AddFood(F,8,1));
      assert(!AddFood(F,-1,1));assert(!AddCreature(F,0,0,0));assert(!AddCreature(F,8,8,0));
      assert(AddFood(F,0,0));assert(!AddFood(F,0,0));++Passed; }
    { Frame F;F.Sequence=1;F.Width=1;F.Height=1;F.FoodCells={1};
      assert(!Validate(F));F.FoodCells={0,0};assert(!Validate(F));++Passed; }
    { Frame F;F.Sequence=1;F.Width=3;F.Height=3;
      assert(AddCreature(F,2,0,0));F.CreatureIds.push_back(3);
      assert(!Validate(F));F.CreatureIds.pop_back();
      F.CreatureIds[0]=0;assert(!Validate(F));++Passed; }
    { Frame F;F.Sequence=1;F.Width=5;F.Height=5;
      F.CellSizeCm=std::numeric_limits<float>::quiet_NaN();assert(!Validate(F));
      F.CellSizeCm=99;assert(!Validate(F));F.CellSizeCm=1001;assert(!Validate(F));
      F.CellSizeCm=200;assert(Validate(F));++Passed; }
    { Frame F;F.Sequence=0;F.Width=5;F.Height=5;assert(!Validate(F));
      F.Sequence=2;assert(!IsNewer(3,F));assert(IsNewer(1,F));++Passed; }
    { Frame F;F.Sequence=1;F.Width=0;F.Height=32;assert(!Validate(F));
      F.Width=33;assert(!Validate(F));F.Width=32;assert(Validate(F));++Passed; }
    { Frame F;F.Sequence=1;F.Width=4;F.Height=4;assert(AddCreature(F,100,1,1));
      assert(AddCreature(F,101,1,1));assert(Validate(F)); // 2 creatures can share a tile
      ++Passed; }
    { Frame F;F.Sequence=1;F.Width=32;F.Height=32;assert(AddFood(F,31,31));
      int X=0,Y=0;assert(DecodeCell(32,32,1023,X,Y));assert(X==31&&Y==31);
      assert(!DecodeCell(32,32,1024,X,Y));++Passed; }
    std::cout << "PASS " << Passed << "/10 snapshot policy groups; max frame estimated "
              << EstimatedBytes([]{Frame F;F.Sequence=1;F.Width=32;F.Height=32;
                   for(int I=0;I<1024;++I)AddFood(F,I%32,I/32);
                   for(int I=0;I<40;++I){AddCreature(F,I+1,0,0);} return F;}())
              << " bytes excluding Unreal wire overhead\n";
}
