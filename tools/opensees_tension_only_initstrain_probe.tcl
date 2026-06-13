proc run_case {label material_cmd} {
    wipe
    model basic -ndm 3 -ndf 3
    eval $material_cmd
    node 1 0 0 0
    node 2 1 0 0
    fix 1 1 1 1
    fix 2 0 1 1
    element corotTruss 1 1 2 1.0 10
    puts "$label initial=[eleResponse 1 axialForce]"
    timeSeries Linear 1
    pattern Plain 1 1 {load 2 1 0 0}
    constraints Plain
    numberer Plain
    system FullGeneral
    test NormDispIncr 1.0e-12 50
    algorithm Newton
    analysis Static
    integrator DisplacementControl 2 1 -0.005
    set ok1 [analyze 1]
    puts "$label shorten_small ok=$ok1 axial=[eleResponse 1 axialForce]"
    integrator DisplacementControl 2 1 -0.010
    set ok2 [analyze 1]
    puts "$label shorten_more ok=$ok2 axial=[eleResponse 1 axialForce]"
    integrator DisplacementControl 2 1 0.030
    set ok3 [analyze 1]
    puts "$label extend ok=$ok3 axial=[eleResponse 1 axialForce]"
}

run_case "ElasticInit" {
    uniaxialMaterial Elastic 1 1000.0
    uniaxialMaterial InitStrainMaterial 10 1 0.01
}

run_case "TensionOnlyInit" {
    uniaxialMaterial ElasticPPGap 1 1000.0 1.0e12 0.0
    uniaxialMaterial InitStrainMaterial 10 1 0.01
}
