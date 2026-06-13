wipe
model basic -ndm 3 -ndf 6
uniaxialMaterial ElasticPPGap 1 1000.0 1.0e12 0.0
node 1 0 0 0
node 2 1 0 0
fix 1 1 1 1 1 1 1
fix 2 0 1 1 1 1 1
mass 1 1 1 1 0 0 0
mass 2 1 1 1 0 0 0
element corotTruss 1 1 2 1.0 1
timeSeries Linear 1
pattern Plain 1 1 {
    load 2 1 0 0 0 0 0
}
constraints Transformation
numberer Plain
system FullGeneral
test NormDispIncr 1.0e-12 50
algorithm Newton
integrator DisplacementControl 2 1 0.01
analysis Static
set ok [analyze 1]
puts "ok=$ok axial=[eleResponse 1 axialForce]"
