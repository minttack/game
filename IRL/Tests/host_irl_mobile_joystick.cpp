#include "IRLMobileJoystickCore.h"
#include <cassert>
#include <cmath>
#include <limits>
#include <iostream>
using IRLMobile::FilterJoystick;
int main()
{
    int tests=0;
    auto near=[](float a,float b){return std::fabs(a-b)<0.002f;};
    auto a=FilterJoystick(0,0);assert(a.X==0 && a.Y==0); ++tests;
    a=FilterJoystick(.08f,.05f);assert(a.X==0 && a.Y==0); ++tests;
    a=FilterJoystick(.12f,0);assert(a.X==0 && a.Y==0); ++tests;
    a=FilterJoystick(1,0);assert(near(a.X,1) && near(a.Y,0)); ++tests;
    a=FilterJoystick(0,-1);assert(near(a.X,0) && near(a.Y,-1)); ++tests;
    a=FilterJoystick(1,1);assert(near(std::hypot(a.X,a.Y),1)); ++tests;
    a=FilterJoystick(.5f,.5f);assert(near(a.X,a.Y) && std::hypot(a.X,a.Y)<1); ++tests;
    a=FilterJoystick(50,0);assert(near(a.X,1)); ++tests;
    a=FilterJoystick(std::numeric_limits<float>::quiet_NaN(),0);assert(a.X==0 && a.Y==0); ++tests;
    a=FilterJoystick(1,std::numeric_limits<float>::infinity());assert(a.X==0 && a.Y==0); ++tests;
    a=FilterJoystick(1,0,-1);assert(a.X==0 && a.Y==0); ++tests;
    a=FilterJoystick(1,0,1);assert(a.X==0 && a.Y==0); ++tests;
    a=FilterJoystick(0.3f,0.0f);assert(a.X>0.1f && a.X<0.3f); ++tests;
    std::cout << "PASS "<<tests<<"/"<<tests<<" original IRL phone-axis safety native cases\n";
}
