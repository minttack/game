// IRL BIE Experience ecology: verified finite food, movement, danger and lineage.
// Deterministic, non-LLM C++17 sim kernel. Not a completed world or subjective life.
#pragma once
#include "IRLLifeLearningCore.h"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <limits>
#include <random>
#include <vector>

namespace IRLEcology {
enum class Policy : std::uint8_t { BIE=0, AlwaysForage=1, AlwaysShelter=2, Random=3 };
struct Tile {
    int Food=0;
    int FoodCapacity=0;
    int RegrowthTicks=0; // zero = no regrowth; otherwise one food unit per interval
    int Danger=0; // stamina damage each step at unprotected tile
    bool Shelter=false;
};
struct Creature {
    std::uint64_t Id=0;
    int X=0,Y=0,Energy=55,Age=0;
    IRLLife::ExperienceLearner Experience;
    bool Alive=true;
};
struct StepReceipt {
    std::uint64_t CreatureId=0,ExperienceCyclesBefore=0,ExperienceCyclesAfter=0;
    int FromX=0,FromY=0,ToX=0,ToY=0;
    int FoodBefore=0,FoodAfter=0,EnergyBefore=0,EnergyAfter=0;
    IRLLife::Action Action=IRLLife::Action::Forage;
    double ObservedReward=0;
    bool DidConsumeFood=false,Survived=false,Valid=false;
};
class Habitat {
public:
    Habitat(int Width,int Height,std::uint64_t Seed=1)
        : W(Width),H(Height),Tiles(Width>0&&Height>0&&Width<=1000&&Height<=1000
            ? static_cast<std::size_t>(Width)*static_cast<std::size_t>(Height):0),RandomEngine(Seed) {}

    bool Valid() const {return W>0&&H>0&&W<=1000&&H<=1000&&!Tiles.empty();}
    bool SetTile(int X,int Y,const Tile& T){if(!Inside(X,Y)||T.Food<0||T.FoodCapacity<0||T.Food>T.FoodCapacity||T.RegrowthTicks<0||T.Danger<0)return false;Tiles[Index(X,Y)]=T;return true;}
    Tile TileAt(int X,int Y) const{return Inside(X,Y)?Tiles[Index(X,Y)]:Tile{};}
    bool AddCreature(int X,int Y,int Energy=55){if(!Inside(X,Y)||Energy<=0||Energy>100||Creatures.size()>=MaxActiveCreatures)return false;Creature C;C.Id=NextId++;C.X=X;C.Y=Y;C.Energy=Energy;Creatures.push_back(C);return true;}
    bool SpawnDescendant(std::uint64_t ParentId,double Inheritance=0.75){
        Creature* Parent=Find(ParentId);
        if(!Parent||!Parent->Alive||Parent->Energy<75||Creatures.size()>=MaxActiveCreatures||!std::isfinite(Inheritance))return false;
        Creature Child;Child.Id=NextId++;Child.X=Parent->X;Child.Y=Parent->Y;Child.Energy=40;
        Child.Experience=Parent->Experience.SpawnNextGeneration(Inheritance);
        Parent->Energy-=25; // reproductive investment has actual cost
        Creatures.push_back(Child);return true;
    }
    Creature* Find(std::uint64_t Id){for(auto &C:Creatures)if(C.Id==Id)return &C;return nullptr;}
    const Creature* Find(std::uint64_t Id)const{for(const auto &C:Creatures)if(C.Id==Id)return &C;return nullptr;}
    const std::vector<Creature>& Residents()const{return Creatures;}
    std::uint64_t WorldTicks()const{return TickCount;}
    std::uint64_t FoodConsumed() const { return TotalFoodEaten; }
    void Regrow(){
        ++TickCount;
        for(auto &T:Tiles)if(T.RegrowthTicks>0 && TickCount%static_cast<std::uint64_t>(T.RegrowthTicks)==0 && T.Food<T.FoodCapacity)++T.Food;
    }
    IRLLife::Observation Sense(std::uint64_t Id,int Radius=2) const {
        const Creature* C=Find(Id);IRLLife::Observation O{};if(!C||!C->Alive)return O;
        for(int Y=std::max(0,C->Y-Radius);Y<=std::min(H-1,C->Y+Radius);++Y)
            for(int X=std::max(0,C->X-Radius);X<=std::min(W-1,C->X+Radius);++X)
                if(Distance(C->X,C->Y,X,Y)<=Radius){const Tile &T=Tiles[Index(X,Y)];O.FoodNearby|=T.Food>0;O.ThreatNearby|=T.Danger>0;}
        return O;
    }
    StepReceipt Step(std::uint64_t Id,Policy Mode=Policy::BIE) {
        StepReceipt Result;Creature* C=Find(Id);
        if(!C||!C->Alive)return Result;
        Result.CreatureId=Id;Result.FromX=C->X;Result.FromY=C->Y;Result.EnergyBefore=C->Energy;
        Result.ExperienceCyclesBefore=C->Experience.Cycles();
        IRLLife::PredictionReceipt Pending;
        const auto Observation=Sense(Id);
        IRLLife::Action Decision=IRLLife::Action::Forage;
        if(Mode==Policy::BIE){if(!C->Experience.Propose(Observation,Pending))return Result;Decision=Pending.ChosenAction;}
        else if(Mode==Policy::AlwaysShelter)Decision=IRLLife::Action::Shelter;
        else if(Mode==Policy::Random)Decision=static_cast<IRLLife::Action>(RandomEngine()%3);
        Result.Action=Decision;
        // Actual movement: one grid cell toward nearest finite food or shelter.
        if(Decision==IRLLife::Action::Forage)MoveToward(*C,true);
        else if(Decision==IRLLife::Action::Shelter)MoveToward(*C,false);
        else {
            // Explore attempts actual cardinal movement, respecting world bounds.
            constexpr int DX[]={1,0,-1,0};constexpr int DY[]={0,1,0,-1};
            const int D=static_cast<int>(RandomEngine()%4);
            if(Inside(C->X+DX[D],C->Y+DY[D])){C->X+=DX[D];C->Y+=DY[D];}
        }
        Tile &Here=Tiles[Index(C->X,C->Y)];
        Result.ToX=C->X;Result.ToY=C->Y;Result.FoodBefore=Here.Food;
        int Cost=2; // living incurs metabolism whether or not it makes a good choice
        if(Decision==IRLLife::Action::Explore)Cost+=2;
        if(Decision==IRLLife::Action::Forage){
            if(Here.Food>0){--Here.Food;++TotalFoodEaten;Result.DidConsumeFood=true;Cost-=14;}
            else Cost+=3;
        }
        if(Decision==IRLLife::Action::Shelter)Cost+=1;
        // A verified shelter tile, not an imaginary 'shelter action', reduces hazard.
        if(Here.Danger>0)Cost+=Here.Shelter?Here.Danger/10:Here.Danger;
        Result.FoodAfter=Here.Food;
        C->Energy=std::max(0,std::min(100,C->Energy-Cost));++C->Age;
        C->Alive=C->Energy>0;
        Result.EnergyAfter=C->Energy;Result.Survived=C->Alive;
        Result.ObservedReward=std::max(-1.,std::min(1.,(Result.EnergyAfter-Result.EnergyBefore)/20.));
        if(Mode==Policy::BIE && !C->Experience.RecordObservedOutcome(Pending,Result.ObservedReward,C->Alive))return StepReceipt{};
        Result.ExperienceCyclesAfter=C->Experience.Cycles();Result.Valid=true;
        return Result;
    }
    // Every living creature gets at most one witnessed physical action per cycle.
    void StepEveryone(Policy Mode=Policy::BIE){Regrow();const std::size_t N=Creatures.size();for(std::size_t I=0;I<N;++I)Step(Creatures[I].Id,Mode);}
    void SetMaxActive(std::size_t Limit){MaxActiveCreatures=Limit;}
private:
    int W=0,H=0;std::vector<Tile> Tiles;std::vector<Creature> Creatures;
    std::mt19937_64 RandomEngine;std::uint64_t NextId=1,TickCount=0,TotalFoodEaten=0;
    std::size_t MaxActiveCreatures=1000;
    bool Inside(int X,int Y) const{return X>=0&&Y>=0&&X<W&&Y<H&&Valid();}
    std::size_t Index(int X,int Y) const{return static_cast<std::size_t>(Y)*static_cast<std::size_t>(W)+static_cast<std::size_t>(X);}
    static int Distance(int X,int Y,int U,int V){return std::abs(X-U)+std::abs(Y-V);}
    void MoveToward(Creature &C,bool ForFood){
        int BestX=C.X,BestY=C.Y,BestDist=std::numeric_limits<int>::max();
        for(int Y=std::max(0,C.Y-2);Y<=std::min(H-1,C.Y+2);++Y)
            for(int X=std::max(0,C.X-2);X<=std::min(W-1,C.X+2);++X){
            if(Distance(C.X,C.Y,X,Y)>2)continue;
            const Tile &T=Tiles[Index(X,Y)];
            if(ForFood?T.Food>0:T.Shelter){const int Dist=Distance(C.X,C.Y,X,Y);
                if(Dist<BestDist){BestDist=Dist;BestX=X;BestY=Y;}}}
        if(BestDist>0 && BestDist!=std::numeric_limits<int>::max()){
            if(C.X!=BestX)C.X+=(BestX>C.X?1:-1);
            else C.Y+=(BestY>C.Y?1:-1);
        }
    }
};
} // namespace IRLEcology
