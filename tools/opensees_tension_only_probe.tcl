wipe
model basic -ndm 3 -ndf 3
uniaxialMaterial ENT 1 1000.0
puts "ENT_OK"
wipe
model basic -ndm 3 -ndf 3
uniaxialMaterial ElasticPPGap 2 1000.0 1.0e12 0.0
puts "ElasticPPGap_OK"
wipe
model basic -ndm 3 -ndf 3
uniaxialMaterial Elastic 3 1000.0
node 1 0 0 0
node 2 1 0 0
fix 1 1 1 1
fix 2 0 1 1
element corotTruss 1 1 2 1.0 3
puts "corotTruss_OK"
