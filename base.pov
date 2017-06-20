/* Lab 1, Composite Object, Stephen K Oliver, CS 360
*/

camera
{
 perspective
 location <2,2,-5>
 look_at <0,0,0>
}

light_source
{
 <5,3,-5>
 color rgb <0.95,0.95,0.95>
}

union
{
difference
{
box
{
 <-1,-1,-1>,<1,1,1>
 pigment { rgb <0,0,0.8> }
}

sphere
{<-1,0,-1>,1} 

}

cylinder
{
  <0.7,1,0.7>, <0.7,-1,0.7>,0.5
  pigment { rgb <0,0,0.8> }
}

} 

plane
{
 <0,1,0>, -1
 pigment
 {
 checker
 color rgb <1,1,1>
 color rgb <0,0,0>
 }
}