wipe
model basic -ndm 3 -ndf 3
uniaxialMaterial ElasticPPGap 1 1000.0 1.0e12 0.0
uniaxialMaterial InitStrainMaterial 10 1 0.01
node 1 0 0 0
node 2 1 0 0
fix 1 1 1 1
fix 2 1 1 1
element corotTruss 1 1 2 1.0 10
puts "initial_axial=[eleResponse 1 axialForce]"
reactions
puts "node1_reaction=[nodeReaction 1]"
puts "node2_reaction=[nodeReaction 2]"
timeSeries Constant 1
pattern Plain 1 1 {
    load 1 0 0 -5
    load 2 0 0 -5
}
loadConst -time 0.0
reactions
puts "after_loadConst_node1_reaction=[nodeReaction 1]"
puts "after_loadConst_node2_reaction=[nodeReaction 2]"
exit
