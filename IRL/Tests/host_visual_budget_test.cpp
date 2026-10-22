#include "IRLVisualBudgetCore.h"
#include <cassert>
#include <limits>
#include <iostream>
using namespace IRLVisual;
static int RunFor(BudgetController& B, int Windows, double Delta, Reason LookingFor=Reason::None)
{
    int Changes=0;Decision D;
    const int Frames=(int)(2.1/Delta)+1;
    for(int W=0;W<Windows;++W)
      for(int F=0;F<Frames;++F)
        if(B.Observe(Delta,D) && D.Changed)
        { ++Changes; if(LookingFor!=Reason::None)assert(D.Cause==LookingFor); }
    return Changes;
}
int main()
{
    int Pass=0;
    BudgetController B;
    assert(B.CurrentTier()==Tier::Balanced); ++Pass;
    // One bad loading spike cannot trigger downgrade.
    Decision D;
    B.Observe(std::numeric_limits<double>::infinity(),D);
    B.Observe(2.0,D);
    assert(B.RejectedSamples()==2); ++Pass;
    RunFor(B,3,1.0/30.0);
    assert(B.CurrentTier()==Tier::Balanced); ++Pass;
    RunFor(B,5,1.0/21.0,Reason::SustainedSlow);
    assert(B.CurrentTier()==Tier::Economy); ++Pass;
    RunFor(B,5,1.0/21.0);
    assert(B.CurrentTier()==Tier::Economy); ++Pass;
    RunFor(B,11,1.0/45.0,Reason::SustainedHeadroom);
    assert(B.CurrentTier()==Tier::Balanced); ++Pass;
    RunFor(B,13,1.0/50.0,Reason::SustainedHeadroom);
    assert(B.CurrentTier()==Tier::Detail); ++Pass;
    RunFor(B,12,1.0/50.0);
    assert(B.CurrentTier()==Tier::Detail); ++Pass;
    // No thrashing around target.
    B.Reset(Tier::Balanced);
    RunFor(B,30,1.0/30.0);
    assert(B.CurrentTier()==Tier::Balanced); ++Pass;
    B.Reset(Tier::Detail,120.0);
    RunFor(B,7,1.0/30.0,Reason::SustainedSlow);
    assert(B.CurrentTier()==Tier::Balanced); ++Pass;
    B.Reset(Tier::Balanced,0.0);
    assert(RunFor(B,3,1.0/30.0)==0); ++Pass;
    std::cout<<"PASS "<<Pass<<"/"<<Pass<<" native visual policy checks"<<std::endl;
}
