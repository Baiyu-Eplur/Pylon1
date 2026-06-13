proc run_case {mat_cmd label pos_disp neg_disp} {
    wipe
    model basic -ndm 3 -ndf 3
    eval $mat_cmd
    node 1 0 0 0
    node 2 1 0 0
    fix 1 1 1 1
    fix 2 0 1 1
    element corotTruss 1 1 2 1.0 1
    timeSeries Linear 1
    pattern Plain 1 1 {
        load 2 1 0 0
    }
    constraints Plain
    numberer Plain
    system FullGeneral
    test NormDispIncr 1.0e-12 50
    algorithm Newton
    integrator DisplacementControl 2 1 $pos_disp
    analysis Static
    set ok1 [analyze 1]
    set fpos [eleResponse 1 axialForce]
    integrator DisplacementControl 2 1 $neg_disp
    set ok2 [analyze 1]
    set fneg [eleResponse 1 axialForce]
    puts "$label ok_pos=$ok1 f_after_pos=$fpos ok_neg=$ok2 f_after_neg=$fneg"
}

run_case {uniaxialMaterial Elastic 1 1000.0} "Elastic" 0.01 -0.02
run_case {uniaxialMaterial ENT 1 1000.0} "ENT" 0.01 -0.02
run_case {uniaxialMaterial ElasticPPGap 1 1000.0 1.0e12 0.0} "ElasticPPGap_FyPos" 0.01 -0.02
run_case {uniaxialMaterial ElasticPPGap 1 1000.0 -1.0e12 0.0} "ElasticPPGap_FyNeg" 0.01 -0.02
