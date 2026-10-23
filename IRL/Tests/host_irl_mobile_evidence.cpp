#include "IRLMobileEvidenceCore.h"
#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>
using namespace IRLMobileEvidence;
int main()
{
    int checks=0;
    Recorder R;
    Window W{};
    for(int i=0;i<299;++i)assert(!R.Observe(1.0/30.0,W));
    assert(R.Observe(1.0/30.0,W)); ++checks;
    assert(W.Frames==300 && W.Rejected==0 && W.DurationSeconds>=9.99); ++checks;
    assert(std::abs(W.MeanMs-1000.0/30.0)<1e-6); ++checks;
    assert(std::abs(W.P50Ms-1000.0/30.0)<1e-6 &&
           std::abs(W.P95Ms-1000.0/30.0)<1e-6 &&
           std::abs(W.P99Ms-1000.0/30.0)<1e-6); ++checks;
    assert(W.MoveAxes==0 && W.Experiences==0); ++checks;

    R.Reset();
    for(int i=0;i<270;++i)
    {
        R.MarkInput(InputKind::MoveAxis);
        if(i%2==0) R.MarkInput(InputKind::LookAxis);
        if(i==12) R.MarkInput(InputKind::JumpPress);
        if(i==13) R.MarkInput(InputKind::ExperiencePress);
        assert(!R.Observe(1.0/30.0,W));
    }
    for(int i=0;i<9;++i)
        assert(!R.Observe(0.10,W));
    // 9.9s elapsed: 9s at 30fps, then nine 100ms slow frames.
    assert(R.Observe(0.10,W)); ++checks;
    assert(W.MoveAxes==270 && W.LookAxes==135 && W.Jumps==1 && W.Experiences==1); ++checks;
    assert(W.Frames==280 && W.P95Ms<40 && W.P99Ms>=99.9); ++checks;
    assert(W.MaxMs>=100 && W.MeanMs>33.33); ++checks;
    R.Reset();
    for(int i=0;i<5;++i)
    {
        assert(!R.Observe(0.0,W));
        assert(!R.Observe(-1.0,W));
        assert(!R.Observe(0.21,W));
        assert(!R.Observe(std::numeric_limits<double>::infinity(),W));
        assert(!R.Observe(std::numeric_limits<double>::quiet_NaN(),W));
    }
    for(int i=0;i<300;++i)R.Observe(1.0/30.0,W);
    assert(W.Rejected==25); ++checks;

    R.Reset();
    for(int i=0;i<1023;++i) assert(!R.Observe(0.001,W));
    assert(R.Observe(0.001,W)); ++checks;
    assert(W.Frames==1024 && W.DurationSeconds<10.0); ++checks;
    assert(!R.Observe(1.0/30.0,W)); ++checks;
    R.Reset();
    for(int i=0;i<300;++i)R.Observe(1.0/30.0,W);
    assert(W.MoveAxes==0 && W.LookAxes==0 && W.Jumps==0 && W.Experiences==0); ++checks;
    std::cout<<"PASS "<<checks<<" IRL mobile evidence host C++17 assertions (NOT physical device)\n";
}
