#  read the file one line at a time
# ########################################
puts ">>> Damping_shifter.tcl loaded"
set damping_debug 0
set damping_log_stride 20

 source "tcl_procedures/readColumnFromFile.tcl"
 source "tcl_procedures/interpolate.tcl"
 
 set filename "data/aero_coeffs/C_D_data.txt"
 set column 0
 set CD_x [readColumnFromFile $filename $column]
 set column 1
 set CD_y [readColumnFromFile $filename $column]

 set filename "data/aero_coeffs/C_L_data2.txt"
 set column 0
 set CL_x [readColumnFromFile $filename $column]
 set column 1
 set CL_y [readColumnFromFile $filename $column]

 set filename "data/aero_coeffs/dC_L.txt"
 set column 0
 set dCL_x $CD_x
 set dCL_y [readColumnFromFile $filename $column]

source inputs_aerodynamic_damping.tcl

# ########################################
# define procedure
proc get_element_local_aero_basis {ele} {
	set elenodes [eleNodes $ele]
	set nnodes [llength $elenodes]
	set first_node [lindex $elenodes 0]
	set last_node [lindex $elenodes [expr {$nnodes - 1}]]

	set c1 [nodeCoord $first_node]
	set c2 [nodeCoord $last_node]
	set d1 [nodeDisp $first_node]
	set d2 [nodeDisp $last_node]

	set x1 [expr [lindex $c1 0] + [lindex $d1 0]]
	set y1 [expr [lindex $c1 1] + [lindex $d1 1]]
	set z1 [expr [lindex $c1 2] + [lindex $d1 2]]
	set x2 [expr [lindex $c2 0] + [lindex $d2 0]]
	set y2 [expr [lindex $c2 1] + [lindex $d2 1]]
	set z2 [expr [lindex $c2 2] + [lindex $d2 2]]

	set tx [expr $x2 - $x1]
	set ty [expr $y2 - $y1]
	set tz [expr $z2 - $z1]
	set Le [expr sqrt($tx*$tx + $ty*$ty + $tz*$tz)]
	if {$Le < 1.0e-12} {
		return [list 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 0.0]
	}
	set tx [expr $tx / $Le]
	set ty [expr $ty / $Le]
	set tz [expr $tz / $Le]

	# Local aerodynamic y-axis: global wind direction projected normal to the
	# deformed element tangent.
	set dot_wt $ty
	set byx [expr -$dot_wt*$tx]
	set byy [expr 1.0 - $dot_wt*$ty]
	set byz [expr -$dot_wt*$tz]
	set byn [expr sqrt($byx*$byx + $byy*$byy + $byz*$byz)]
	if {$byn < 1.0e-12} {
		set byx 0.0
		set byy 1.0
		set byz 0.0
		set byn 1.0
	}
	set byx [expr $byx / $byn]
	set byy [expr $byy / $byn]
	set byz [expr $byz / $byn]

	# Local aerodynamic z-axis: global vertical projected into the same normal
	# plane and orthogonalized against local y.
	set dot_zt $tz
	set bzx [expr -$dot_zt*$tx]
	set bzy [expr -$dot_zt*$ty]
	set bzz [expr 1.0 - $dot_zt*$tz]
	set dot_zy [expr $bzx*$byx + $bzy*$byy + $bzz*$byz]
	set bzx [expr $bzx - $dot_zy*$byx]
	set bzy [expr $bzy - $dot_zy*$byy]
	set bzz [expr $bzz - $dot_zy*$byz]
	set bzn [expr sqrt($bzx*$bzx + $bzy*$bzy + $bzz*$bzz)]
	if {$bzn < 1.0e-12} {
		set bzx [expr $ty*$byz - $tz*$byy]
		set bzy [expr $tz*$byx - $tx*$byz]
		set bzz [expr $tx*$byy - $ty*$byx]
		set bzn [expr sqrt($bzx*$bzx + $bzy*$bzy + $bzz*$bzz)]
	}
	if {$bzn < 1.0e-12} {
		set bzx 0.0
		set bzy 0.0
		set bzz 1.0
		set bzn 1.0
	}
	set bzx [expr $bzx / $bzn]
	set bzy [expr $bzy / $bzn]
	set bzz [expr $bzz / $bzn]

	return [list $tx $ty $tz $byx $byy $byz $bzx $bzy $bzz $Le]
}

proc get_node_local_aero_basis {node} {
	set node_tags [lsort -integer [getNodeTags]]
	set first_node [lindex $node_tags 0]
	set last_node [lindex $node_tags end]
	if {$node == $first_node} {
		set n1 $node
		set n2 [lindex $node_tags 1]
	} elseif {$node == $last_node} {
		set n1 [lindex $node_tags end-1]
		set n2 $node
	} else {
		set n1 [expr {$node - 1}]
		set n2 [expr {$node + 1}]
	}

	set c1 [nodeCoord $n1]
	set c2 [nodeCoord $n2]
	set d1 [nodeDisp $n1]
	set d2 [nodeDisp $n2]

	set x1 [expr [lindex $c1 0] + [lindex $d1 0]]
	set y1 [expr [lindex $c1 1] + [lindex $d1 1]]
	set z1 [expr [lindex $c1 2] + [lindex $d1 2]]
	set x2 [expr [lindex $c2 0] + [lindex $d2 0]]
	set y2 [expr [lindex $c2 1] + [lindex $d2 1]]
	set z2 [expr [lindex $c2 2] + [lindex $d2 2]]

	set tx [expr $x2 - $x1]
	set ty [expr $y2 - $y1]
	set tz [expr $z2 - $z1]
	set Ln [expr sqrt($tx*$tx + $ty*$ty + $tz*$tz)]
	if {$Ln < 1.0e-12} {
		return [list 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0]
	}
	set tx [expr $tx / $Ln]
	set ty [expr $ty / $Ln]
	set tz [expr $tz / $Ln]

	set dot_wt $ty
	set byx [expr -$dot_wt*$tx]
	set byy [expr 1.0 - $dot_wt*$ty]
	set byz [expr -$dot_wt*$tz]
	set byn [expr sqrt($byx*$byx + $byy*$byy + $byz*$byz)]
	if {$byn < 1.0e-12} {
		set byx 0.0
		set byy 1.0
		set byz 0.0
		set byn 1.0
	}
	set byx [expr $byx / $byn]
	set byy [expr $byy / $byn]
	set byz [expr $byz / $byn]

	set dot_zt $tz
	set bzx [expr -$dot_zt*$tx]
	set bzy [expr -$dot_zt*$ty]
	set bzz [expr 1.0 - $dot_zt*$tz]
	set dot_zy [expr $bzx*$byx + $bzy*$byy + $bzz*$byz]
	set bzx [expr $bzx - $dot_zy*$byx]
	set bzy [expr $bzy - $dot_zy*$byy]
	set bzz [expr $bzz - $dot_zy*$byz]
	set bzn [expr sqrt($bzx*$bzx + $bzy*$bzy + $bzz*$bzz)]
	if {$bzn < 1.0e-12} {
		set bzx [expr $ty*$byz - $tz*$byy]
		set bzy [expr $tz*$byx - $tx*$byz]
		set bzz [expr $tx*$byy - $ty*$byx]
		set bzn [expr sqrt($bzx*$bzx + $bzy*$bzy + $bzz*$bzz)]
	}
	if {$bzn < 1.0e-12} {
		set bzx 0.0
		set bzy 0.0
		set bzz 1.0
		set bzn 1.0
	}
	set bzx [expr $bzx / $bzn]
	set bzy [expr $bzy / $bzn]
	set bzz [expr $bzz / $bzn]

	return [list $tx $ty $tz $byx $byy $byz $bzx $bzy $bzz]
}

proc apply_quasi_steady_aero_force {} {
	global STKO_VAR_time
	global STKO_VAR_increment
	global CD_x
	global CD_y
	global CL_x
	global CL_y
	global wind_velocity_per_element_H
	global wind_velocity_per_element_V
	global time
	global wind_time_vector
	global ro_air
	global B
	global enable_quasi_steady_aero_force
	global quasi_steady_aero_force_scale
	global quasi_steady_aero_force_log_stride
	global quasi_steady_aero_pattern_tag
	global quasi_steady_aero_series_tag
	global quasi_steady_aero_pattern_active
	global opensees_output_dir

	if {![info exists enable_quasi_steady_aero_force]} {set enable_quasi_steady_aero_force 0}
	if {![info exists quasi_steady_aero_force_scale]} {set quasi_steady_aero_force_scale 1.0}
	if {![info exists quasi_steady_aero_force_log_stride]} {set quasi_steady_aero_force_log_stride 20}
	if {![info exists quasi_steady_aero_pattern_tag]} {set quasi_steady_aero_pattern_tag 901000}
	if {![info exists quasi_steady_aero_series_tag]} {set quasi_steady_aero_series_tag 901000}

	if {[info exists quasi_steady_aero_pattern_active] && $quasi_steady_aero_pattern_active} {
		remove loadPattern $quasi_steady_aero_pattern_tag
		set quasi_steady_aero_pattern_active 0
	}

	if {!$enable_quasi_steady_aero_force} {
		return
	}

	if {![info exists STKO_VAR_time]} {
		set currentTime [getTime]
	} else {
		set currentTime $STKO_VAR_time
	}

	set node_tags [getNodeTags]
	foreach node $node_tags {
		set fy($node) 0.0
		set fz($node) 0.0
	}

	set total_abs_force 0.0
	set max_abs_force 0.0
	set max_alpha_deg 0.0
	set clipped_count 0
	set ele_count 0

	foreach ele [getEleTags] {
		set elenodes [eleNodes $ele]
		set nnodes [llength $elenodes]
		if {$nnodes < 2} {
			continue
		}
		incr ele_count

		set first_node [lindex $elenodes 0]
		set last_node [lindex $elenodes [expr {$nnodes - 1}]]
		set c1 [nodeCoord $first_node]
		set c2 [nodeCoord $last_node]
		set d1 [nodeDisp $first_node]
		set d2 [nodeDisp $last_node]

		set x1 [expr [lindex $c1 0] + [lindex $d1 0]]
		set y1 [expr [lindex $c1 1] + [lindex $d1 1]]
		set z1 [expr [lindex $c1 2] + [lindex $d1 2]]
		set x2 [expr [lindex $c2 0] + [lindex $d2 0]]
		set y2 [expr [lindex $c2 1] + [lindex $d2 1]]
		set z2 [expr [lindex $c2 2] + [lindex $d2 2]]

		set tx [expr $x2 - $x1]
		set ty [expr $y2 - $y1]
		set tz [expr $z2 - $z1]
		set Le [expr sqrt($tx*$tx + $ty*$ty + $tz*$tz)]
		if {$Le < 1.0e-12} {
			continue
		}
		set tx [expr $tx / $Le]
		set ty [expr $ty / $Le]
		set tz [expr $tz / $Le]

		set vmean [list 0.0 0.0 0.0]
		foreach node $elenodes {
			set v [nodeVel $node]
			for {set i 0} {$i < 3} {incr i} {
				lset vmean $i [expr [lindex $vmean $i] + [lindex $v $i]]
			}
		}
		for {set i 0} {$i < 3} {incr i} {
			lset vmean $i [expr [lindex $vmean $i] / $nnodes.0]
		}

		set external_wind_vector_H [lindex $wind_velocity_per_element_H [expr {$ele - 1}]]
		set external_wind_vector_V [lindex $wind_velocity_per_element_V [expr {$ele - 1}]]
		if {[info exists wind_time_vector]} {set aero_time $wind_time_vector} else {set aero_time $time}
		set v_wind_y [interpolate $currentTime $aero_time $external_wind_vector_H]
		set v_wind_z [interpolate $currentTime $aero_time $external_wind_vector_V]

		set v_rel_x [expr 0.0 - [lindex $vmean 0]]
		set v_rel_y [expr $v_wind_y - [lindex $vmean 1]]
		set v_rel_z [expr $v_wind_z - [lindex $vmean 2]]

		# Remove the component parallel to the instantaneous cable axis. This
		# makes the load use the actual displaced local line orientation.
		set v_dot_t [expr $v_rel_x*$tx + $v_rel_y*$ty + $v_rel_z*$tz]
		set vn_x [expr $v_rel_x - $v_dot_t*$tx]
		set vn_y [expr $v_rel_y - $v_dot_t*$ty]
		set vn_z [expr $v_rel_z - $v_dot_t*$tz]
		set U [expr sqrt($vn_x*$vn_x + $vn_y*$vn_y + $vn_z*$vn_z)]
		if {$U < 1.0e-12} {
			continue
		}

		set ey [expr $vn_y / $U]
		set ez [expr $vn_z / $U]
		if {abs($ey) < 1.0e-12} {
			set alpha [expr atan2($ez, $ey)]
		} else {
			set alpha [expr atan($ez/$ey)]
		}
		set alpha_deg [expr abs($alpha) / 3.141592653589793 * 180.0]
		if {$alpha_deg > $max_alpha_deg} {set max_alpha_deg $alpha_deg}
		set alpha_lookup $alpha_deg
		set alpha_max [lindex $CD_x end]
		if {$alpha_lookup > $alpha_max} {
			set alpha_lookup $alpha_max
			incr clipped_count
		}

		set CD [interpolate $alpha_lookup $CD_x $CD_y]
		set CL [interpolate $alpha_lookup $CL_x $CL_y]
		set qL [expr 0.5 * $ro_air * $U * $U * $B * $Le * $quasi_steady_aero_force_scale]

		set drag_y [expr $qL * $CD * $ey]
		set drag_z [expr $qL * $CD * $ez]
		set lift_y [expr -$qL * $CL * $ez]
		set lift_z [expr  $qL * $CL * $ey]
		set ele_fy [expr $drag_y + $lift_y]
		set ele_fz [expr $drag_z + $lift_z]

		foreach node $elenodes {
			set fy($node) [expr $fy($node) + $ele_fy / $nnodes.0]
			set fz($node) [expr $fz($node) + $ele_fz / $nnodes.0]
		}

		set ele_abs_force [expr sqrt($ele_fy*$ele_fy + $ele_fz*$ele_fz)]
		set total_abs_force [expr $total_abs_force + $ele_abs_force]
		if {$ele_abs_force > $max_abs_force} {set max_abs_force $ele_abs_force}
	}

	pattern Plain $quasi_steady_aero_pattern_tag $quasi_steady_aero_series_tag {
		foreach node [getNodeTags] {
			load $node 0 $fy($node) $fz($node) 0 0 0
		}
	}
	set quasi_steady_aero_pattern_active 1

	if {![info exists STKO_VAR_increment] || [expr {$STKO_VAR_increment % $quasi_steady_aero_force_log_stride}] == 0} {
		if {[info exists opensees_output_dir]} {
			set logfile [open "$opensees_output_dir/quasi_steady_aero_force_log.txt" a]
		} else {
			set logfile [open "Output/quasi_steady_aero_force_log.txt" a]
		}
		puts $logfile "$currentTime $total_abs_force $max_abs_force $quasi_steady_aero_force_scale $max_alpha_deg $clipped_count $ele_count"
		close $logfile
	}
}

proc load_incremental_original_force_data {} {
	global incremental_original_force_data_loaded
	global force_data_dir
	global original_force_H_drag
	global original_force_H_lift
	global original_force_V_drag
	global original_force_V_lift
	global original_wind_H
	global original_wind_V

	if {[info exists incremental_original_force_data_loaded] && $incremental_original_force_data_loaded} {
		return
	}
	if {![info exists force_data_dir]} {
		set force_data_dir "data/forces/FORCE_3/SIM1"
	}

	foreach node [getNodeTags] {
		foreach item {H_drag H_lift V_drag V_lift} {
			set filename "$force_data_dir/NODE_${node}_${item}.txt"
			if {[file exists $filename]} {
				set column 0
				set values [readColumnFromFile $filename $column]
			} else {
				set values {}
			}
			if {$item eq "H_drag"} {
				set original_force_H_drag($node) $values
			} elseif {$item eq "H_lift"} {
				set original_force_H_lift($node) $values
			} elseif {$item eq "V_drag"} {
				set original_force_V_drag($node) $values
			} else {
				set original_force_V_lift($node) $values
			}
		}
		foreach item {wind_H wind_V} {
			set filename "$force_data_dir/NODE_${node}_${item}.txt"
			if {[file exists $filename]} {
				set column 0
				set values [readColumnFromFile $filename $column]
			} else {
				set values {}
			}
			if {$item eq "wind_H"} {
				set original_wind_H($node) $values
			} else {
				set original_wind_V($node) $values
			}
		}
	}
	set incremental_original_force_data_loaded 1
}

proc get_incremental_time_series_component {node component currentTime} {
	global time
	global wind_time_vector
	global original_force_H_drag
	global original_force_H_lift
	global original_force_V_drag
	global original_force_V_lift
	global original_wind_H
	global original_wind_V

	if {$component eq "H_drag"} {
		set values $original_force_H_drag($node)
	} elseif {$component eq "H_lift"} {
		set values $original_force_H_lift($node)
	} elseif {$component eq "V_drag"} {
		set values $original_force_V_drag($node)
	} elseif {$component eq "V_lift"} {
		set values $original_force_V_lift($node)
	} elseif {$component eq "wind_H"} {
		set values $original_wind_H($node)
	} else {
		set values $original_wind_V($node)
	}
	if {[llength $values] == 0} {
		return 0.0
	}
	# The force and wind histories are defined on the original fixed wind
	# time vector. Do not index them with STKO_VAR_time_increment, because the
	# transient solver adapts that value during difficult nonlinear response.
	# Using the adaptive substep as a file dt de-synchronizes this real-time
	# branch from the OpenSees Path load.
	if {[info exists wind_time_vector]} {set aero_time $wind_time_vector} else {set aero_time $time}
	return [interpolate $currentTime $aero_time $values]
}

proc apply_incremental_quasi_steady_aero_force {} {
	global STKO_VAR_time
	global STKO_VAR_increment
	global CD_x
	global CD_y
	global CL_x
	global CL_y
	global wind_velocity_per_element_H
	global wind_velocity_per_element_V
	global time
	global wind_time_vector
	global ro_air
	global B
	global node_tributary_lengths
	global incremental_qs_ro_air_density
	global enable_incremental_quasi_steady_aero_force
	global incremental_quasi_steady_aero_force_scale
	global incremental_quasi_steady_aero_force_log_stride
	global incremental_quasi_steady_aero_pattern_tag
	global incremental_quasi_steady_aero_series_tag
	global incremental_quasi_steady_aero_pattern_active
	global incremental_qs_max_alpha_reference_deg
	global incremental_qs_max_alpha_current_deg
	global incremental_qs_clipped_fraction
	global incremental_qs_total_abs_delta_force
	global opensees_output_dir

	if {![info exists enable_incremental_quasi_steady_aero_force]} {set enable_incremental_quasi_steady_aero_force 0}
	if {![info exists incremental_quasi_steady_aero_force_scale]} {set incremental_quasi_steady_aero_force_scale 1.0}
	if {![info exists incremental_quasi_steady_aero_force_log_stride]} {set incremental_quasi_steady_aero_force_log_stride 20}
	if {![info exists incremental_quasi_steady_aero_pattern_tag]} {set incremental_quasi_steady_aero_pattern_tag 902000}
	if {![info exists incremental_quasi_steady_aero_series_tag]} {set incremental_quasi_steady_aero_series_tag 902000}
	if {![info exists incremental_qs_ro_air_density]} {set incremental_qs_ro_air_density $ro_air}

	if {[info exists incremental_quasi_steady_aero_pattern_active] && $incremental_quasi_steady_aero_pattern_active} {
		remove loadPattern $incremental_quasi_steady_aero_pattern_tag
		set incremental_quasi_steady_aero_pattern_active 0
	}

	if {!$enable_incremental_quasi_steady_aero_force} {
		return
	}

	if {![info exists STKO_VAR_time]} {
		set currentTime [getTime]
	} else {
		set currentTime $STKO_VAR_time
	}

	load_incremental_original_force_data

	set node_tags [getNodeTags]
	foreach node $node_tags {
		set fx($node) 0.0
		set fy($node) 0.0
		set fz($node) 0.0
	}

	set F_reference 0.0
	set F_current 0.0
	set Delta_F_motion 0.0
	set total_abs_delta_force 0.0
	set max_abs_delta_force 0.0
	set total_delta_power 0.0
	set total_current_power 0.0
	set total_drag_power 0.0
	set total_lift_power 0.0
	set baseline_mismatch_abs 0.0
	set max_baseline_mismatch_abs 0.0
	set max_alpha_current_deg 0.0
	set max_alpha_reference_deg 0.0
	set clipped_count 0
	set node_count 0
	set write_detailed_log 0
	if {![info exists STKO_VAR_increment] || [expr {$STKO_VAR_increment % $incremental_quasi_steady_aero_force_log_stride}] == 0} {
		set write_detailed_log 1
	}
	if {$write_detailed_log} {
		if {[info exists opensees_output_dir]} {
			set node_power_path "$opensees_output_dir/incremental_qs_node_power_log.csv"
		} else {
			set node_power_path "Output/incremental_qs_node_power_log.csv"
		}
		set node_power_needs_header [expr {![file exists $node_power_path]}]
		set node_power_file [open $node_power_path a]
		if {$node_power_needs_header} {
			puts $node_power_file "time,node,delta_fx,delta_fy,delta_fz,cur_fx,cur_fy,cur_fz,ref_fx,ref_fy,ref_fz,vx,vy,vz,wind_y,wind_z,U_wind,ref_alpha_deg,rel_y,rel_z,delta_power,current_power,drag_power,lift_power,U_rel,alpha_deg,alpha_lookup_deg,CD,CL,clipped,baseline_mismatch_abs"
		}
	}

	foreach node $node_tags {
		incr node_count
		set h_drag [expr 1000.0 * [get_incremental_time_series_component $node "H_drag" $currentTime]]
		set h_lift [expr 1000.0 * [get_incremental_time_series_component $node "H_lift" $currentTime]]
		set v_drag [expr 1000.0 * [get_incremental_time_series_component $node "V_drag" $currentTime]]
		set v_lift [expr 1000.0 * [get_incremental_time_series_component $node "V_lift" $currentTime]]
		set ref_fx 0.0
		set ref_fy [expr $h_drag + $v_lift]
		set ref_fz [expr $h_lift + $v_drag]
		set ref_abs [expr sqrt($ref_fy*$ref_fy + $ref_fz*$ref_fz)]

		set v_wind_y [get_incremental_time_series_component $node "wind_H" $currentTime]
		set v_wind_z [get_incremental_time_series_component $node "wind_V" $currentTime]
		set ref_alpha_deg [expr abs(atan2($v_wind_z, $v_wind_y)) / 3.141592653589793 * 180.0]
		if {$ref_alpha_deg > $max_alpha_reference_deg} {set max_alpha_reference_deg $ref_alpha_deg}
		set v_node [nodeVel $node]
		set v_rel_global_x [expr 0.0 - [lindex $v_node 0]]
		set v_rel_global_y [expr $v_wind_y - [lindex $v_node 1]]
		set v_rel_global_z [expr $v_wind_z - [lindex $v_node 2]]

		set basis [get_node_local_aero_basis $node]
		set byx [lindex $basis 3]
		set byy [lindex $basis 4]
		set byz [lindex $basis 5]
		set bzx [lindex $basis 6]
		set bzy [lindex $basis 7]
		set bzz [lindex $basis 8]
		set rel_y [expr $v_rel_global_x*$byx + $v_rel_global_y*$byy + $v_rel_global_z*$byz]
		set rel_z [expr $v_rel_global_x*$bzx + $v_rel_global_y*$bzy + $v_rel_global_z*$bzz]
		set U [expr sqrt($rel_y*$rel_y + $rel_z*$rel_z)]
		set cur_fx 0.0
		set cur_fy 0.0
		set cur_fz 0.0
		set cur_abs 0.0
		set drag_fx 0.0
		set drag_fy 0.0
		set drag_fz 0.0
		set lift_fx 0.0
		set lift_fy 0.0
		set lift_fz 0.0
		set alpha_deg 0.0
		set alpha_lookup 0.0
		set CD 0.0
		set CL 0.0
		set clipped 0
		set baseline_node_mismatch_abs 0.0
		if {$U >= 1.0e-12} {
			set ey [expr $rel_y / $U]
			set ez [expr $rel_z / $U]
			if {$rel_y < 0.0} {
				set angle_y [expr -$rel_y]
				set angle_z [expr -$rel_z]
			} else {
				set angle_y $rel_y
				set angle_z $rel_z
			}
			if {abs($angle_y) < 1.0e-12} {
				set alpha [expr atan2($angle_z, $angle_y)]
			} else {
				set alpha [expr atan($angle_z/$angle_y)]
			}
			set alpha_deg [expr abs($alpha) / 3.141592653589793 * 180.0]
			if {$alpha_deg > $max_alpha_current_deg} {set max_alpha_current_deg $alpha_deg}
			set alpha_lookup $alpha_deg
			set alpha_max [lindex $CD_x end]
			if {$alpha_lookup > $alpha_max} {
				set alpha_lookup $alpha_max
				incr clipped_count
				set clipped 1
			}
			set CD [interpolate $alpha_lookup $CD_x $CD_y]
			set CL [interpolate $alpha_lookup $CL_x $CL_y]
			set dx_node [lindex $node_tributary_lengths [expr {$node - 1}]]
			set projected_area [expr 3.141592653589793 * $B * $dx_node / 2.0]
			set qA [expr 0.5 * $incremental_qs_ro_air_density * $U * $U * $projected_area * $incremental_quasi_steady_aero_force_scale]
			# Match the original Path-load convention exactly:
			# H_drag -> transverse, V_lift -> transverse,
			# H_lift -> vertical,   V_drag -> vertical.
			# This is intentionally not the usual compact vector form; it keeps
			# the incremental branch baseline-compatible with the precomputed
			# wind-force files.
			set drag_local_y [expr $qA*$CD*$ey]
			set drag_local_z [expr $qA*$CD*$ez]
			set lift_path_y [expr $qA*$CL*$ey]
			set lift_path_z [expr -$qA*$CL*$ez]
			set local_y [expr $drag_local_y + $lift_path_y]
			set local_z [expr $drag_local_z + $lift_path_z]
			set drag_fx [expr $drag_local_y*$byx + $drag_local_z*$bzx]
			set drag_fy [expr $drag_local_y*$byy + $drag_local_z*$bzy]
			set drag_fz [expr $drag_local_y*$byz + $drag_local_z*$bzz]
			set lift_fx [expr $lift_path_y*$byx + $lift_path_z*$bzx]
			set lift_fy [expr $lift_path_y*$byy + $lift_path_z*$bzy]
			set lift_fz [expr $lift_path_y*$byz + $lift_path_z*$bzz]
			set cur_fx [expr $drag_fx + $lift_fx]
			set cur_fy [expr $drag_fy + $lift_fy]
			set cur_fz [expr $drag_fz + $lift_fz]
			set cur_abs [expr sqrt($cur_fx*$cur_fx + $cur_fy*$cur_fy + $cur_fz*$cur_fz)]
		}

		# Zero-motion, global-reference consistency check against the original
		# Path load convention. This should be near zero if the coefficient and
		# component mapping are baseline-compatible.
		set U_ref [expr sqrt($v_wind_y*$v_wind_y + $v_wind_z*$v_wind_z)]
		if {$U_ref >= 1.0e-12} {
			set ref_ey [expr $v_wind_y / $U_ref]
			set ref_ez [expr $v_wind_z / $U_ref]
			set ref_alpha_lookup $ref_alpha_deg
			set alpha_max_ref [lindex $CD_x end]
			if {$ref_alpha_lookup > $alpha_max_ref} {set ref_alpha_lookup $alpha_max_ref}
			set CD_ref [interpolate $ref_alpha_lookup $CD_x $CD_y]
			set CL_ref [interpolate $ref_alpha_lookup $CL_x $CL_y]
			set dx_node_ref [lindex $node_tributary_lengths [expr {$node - 1}]]
			set projected_area_ref [expr 3.141592653589793 * $B * $dx_node_ref / 2.0]
			set qA_ref [expr 0.5 * $incremental_qs_ro_air_density * $U_ref * $U_ref * $projected_area_ref * $incremental_quasi_steady_aero_force_scale]
			set baseline_fy [expr $qA_ref*$CD_ref*$ref_ey + $qA_ref*$CL_ref*$ref_ey]
			set baseline_fz [expr $qA_ref*$CD_ref*$ref_ez - $qA_ref*$CL_ref*$ref_ez]
			set baseline_node_mismatch_abs [expr sqrt(($baseline_fy-$ref_fy)*($baseline_fy-$ref_fy) + ($baseline_fz-$ref_fz)*($baseline_fz-$ref_fz))]
		}

		set delta_fx [expr $cur_fx - $ref_fx]
		set delta_fy [expr $cur_fy - $ref_fy]
		set delta_fz [expr $cur_fz - $ref_fz]
		set delta_abs [expr sqrt($delta_fx*$delta_fx + $delta_fy*$delta_fy + $delta_fz*$delta_fz)]
		set vx [lindex $v_node 0]
		set vy [lindex $v_node 1]
		set vz [lindex $v_node 2]
		set delta_power [expr $delta_fx*$vx + $delta_fy*$vy + $delta_fz*$vz]
		set current_power [expr $cur_fx*$vx + $cur_fy*$vy + $cur_fz*$vz]
		set drag_power [expr $drag_fx*$vx + $drag_fy*$vy + $drag_fz*$vz]
		set lift_power [expr $lift_fx*$vx + $lift_fy*$vy + $lift_fz*$vz]

		set fx($node) $delta_fx
		set fy($node) $delta_fy
		set fz($node) $delta_fz

		set F_reference [expr $F_reference + $ref_abs]
		set F_current [expr $F_current + $cur_abs]
		set Delta_F_motion [expr $Delta_F_motion + $delta_abs]
		set total_abs_delta_force [expr $total_abs_delta_force + $delta_abs]
		set total_delta_power [expr $total_delta_power + $delta_power]
		set total_current_power [expr $total_current_power + $current_power]
		set total_drag_power [expr $total_drag_power + $drag_power]
		set total_lift_power [expr $total_lift_power + $lift_power]
		set baseline_mismatch_abs [expr $baseline_mismatch_abs + $baseline_node_mismatch_abs]
		if {$delta_abs > $max_abs_delta_force} {set max_abs_delta_force $delta_abs}
		if {$baseline_node_mismatch_abs > $max_baseline_mismatch_abs} {set max_baseline_mismatch_abs $baseline_node_mismatch_abs}
		if {$write_detailed_log} {
			puts $node_power_file "$currentTime,$node,$delta_fx,$delta_fy,$delta_fz,$cur_fx,$cur_fy,$cur_fz,$ref_fx,$ref_fy,$ref_fz,$vx,$vy,$vz,$v_wind_y,$v_wind_z,$U_ref,$ref_alpha_deg,$rel_y,$rel_z,$delta_power,$current_power,$drag_power,$lift_power,$U,$alpha_deg,$alpha_lookup,$CD,$CL,$clipped,$baseline_node_mismatch_abs"
		}
	}
	if {$write_detailed_log} {
		close $node_power_file
	}

	pattern Plain $incremental_quasi_steady_aero_pattern_tag $incremental_quasi_steady_aero_series_tag {
		foreach node [getNodeTags] {
			load $node $fx($node) $fy($node) $fz($node) 0 0 0
		}
	}
	set incremental_quasi_steady_aero_pattern_active 1
	set incremental_qs_max_alpha_reference_deg $max_alpha_reference_deg
	set incremental_qs_max_alpha_current_deg $max_alpha_current_deg
	if {$node_count > 0} {
		set incremental_qs_clipped_fraction [expr double($clipped_count) / double($node_count)]
	} else {
		set incremental_qs_clipped_fraction 0.0
	}
	set incremental_qs_total_abs_delta_force $total_abs_delta_force

	if {$write_detailed_log} {
		if {[info exists opensees_output_dir]} {
			set logfile_path "$opensees_output_dir/incremental_quasi_steady_aero_force_log.txt"
		} else {
			set logfile_path "Output/incremental_quasi_steady_aero_force_log.txt"
		}
		set needs_header [expr {![file exists $logfile_path]}]
		set logfile [open $logfile_path a]
		if {$needs_header} {
			puts $logfile "time F_original F_reference F_current Delta_F_motion total_abs_delta_force max_abs_delta_force scale max_alpha_reference_deg max_alpha_current_deg clipped_count node_count total_delta_power total_current_power total_drag_power total_lift_power baseline_mismatch_abs max_baseline_mismatch_abs"
		}
		puts $logfile "$currentTime $F_reference $F_reference $F_current $Delta_F_motion $total_abs_delta_force $max_abs_delta_force $incremental_quasi_steady_aero_force_scale $max_alpha_reference_deg $max_alpha_current_deg $clipped_count $node_count $total_delta_power $total_current_power $total_drag_power $total_lift_power $baseline_mismatch_abs $max_baseline_mismatch_abs"
		close $logfile
	}
}

proc log_element_strain_tension {} {
	global STKO_VAR_time
	global STKO_VAR_increment
	global opensees_output_dir
	global element_axial_EA
	global element_pretension_load
	global element_pretension_loads
	global element_tension_only
	global element_compression_regularization_ratio
	global element_strain_log_stride

	if {![info exists element_strain_log_stride]} {set element_strain_log_stride 1}
	if {[info exists STKO_VAR_increment] && [expr {$STKO_VAR_increment % $element_strain_log_stride}] != 0} {
		return
	}
	if {![info exists STKO_VAR_time]} {
		set currentTime [getTime]
	} else {
		set currentTime $STKO_VAR_time
	}
	if {![info exists element_axial_EA]} {set element_axial_EA 0.0}
	if {![info exists element_pretension_load]} {set element_pretension_load 0.0}
	if {![info exists element_tension_only]} {set element_tension_only 0}
	if {![info exists element_compression_regularization_ratio]} {set element_compression_regularization_ratio 0.0}
	if {[info exists opensees_output_dir]} {
		set elem_path "$opensees_output_dir/element_strain_tension_log.csv"
		set summary_path "$opensees_output_dir/element_strain_tension_summary_log.csv"
	} else {
		set elem_path "Output/element_strain_tension_log.csv"
		set summary_path "Output/element_strain_tension_summary_log.csv"
	}
	set elem_needs_header [expr {![file exists $elem_path]}]
	set elem_file [open $elem_path a]
	if {$elem_needs_header} {
		puts $elem_file "time,element,initial_length,current_length,strain,delta_tension_N,raw_elastic_tension_N,estimated_total_tension_N,is_slack"
	}
	set max_abs_strain 0.0
	set max_abs_tension 0.0
	set max_abs_raw_elastic_tension 0.0
	set min_estimated_tension 1.0e300
	set max_element 0
	set sum_abs_strain 0.0
	set slack_count 0
	set count 0
	foreach ele [getEleTags] {
		set nodes [eleNodes $ele]
		if {[llength $nodes] < 2} {
			continue
		}
		set n1 [lindex $nodes 0]
		set n2 [lindex $nodes end]
		set c1 [nodeCoord $n1]
		set c2 [nodeCoord $n2]
		set d1 [nodeDisp $n1]
		set d2 [nodeDisp $n2]
		set L0 [expr sqrt(pow([lindex $c2 0]-[lindex $c1 0],2) + pow([lindex $c2 1]-[lindex $c1 1],2) + pow([lindex $c2 2]-[lindex $c1 2],2))]
		set x1 [expr [lindex $c1 0] + [lindex $d1 0]]
		set y1 [expr [lindex $c1 1] + [lindex $d1 1]]
		set z1 [expr [lindex $c1 2] + [lindex $d1 2]]
		set x2 [expr [lindex $c2 0] + [lindex $d2 0]]
		set y2 [expr [lindex $c2 1] + [lindex $d2 1]]
		set z2 [expr [lindex $c2 2] + [lindex $d2 2]]
		set Lcur [expr sqrt(pow($x2-$x1,2) + pow($y2-$y1,2) + pow($z2-$z1,2))]
		if {$L0 < 1.0e-12} {
			continue
		}
		set strain [expr ($Lcur - $L0) / $L0]
		set initial_tension $element_pretension_load
		if {[info exists element_pretension_loads] && [llength $element_pretension_loads] >= $ele} {
			set initial_tension [lindex $element_pretension_loads [expr {$ele - 1}]]
		}
		set delta_tension [expr $element_axial_EA * $strain]
		set raw_elastic_tension [expr $initial_tension + $delta_tension]
		set total_tension $raw_elastic_tension
		set is_slack 0
		if {$element_tension_only && $total_tension < 0.0} {
			set total_tension 0.0
			set is_slack 1
		} elseif {$element_compression_regularization_ratio > 0.0 && $total_tension < 0.0} {
			set total_tension [expr {$element_compression_regularization_ratio * $total_tension}]
			set is_slack 1
		}
		set abs_strain [expr abs($strain)]
		set abs_tension [expr abs($total_tension)]
		set abs_raw_elastic_tension [expr abs($raw_elastic_tension)]
		if {$abs_strain > $max_abs_strain} {
			set max_abs_strain $abs_strain
			set max_element $ele
		}
		if {$abs_tension > $max_abs_tension} {
			set max_abs_tension $abs_tension
		}
		if {$abs_raw_elastic_tension > $max_abs_raw_elastic_tension} {
			set max_abs_raw_elastic_tension $abs_raw_elastic_tension
		}
		if {$total_tension < $min_estimated_tension} {
			set min_estimated_tension $total_tension
		}
		if {$is_slack} {
			incr slack_count
		}
		set sum_abs_strain [expr $sum_abs_strain + $abs_strain]
		incr count
		puts $elem_file "$currentTime,$ele,$L0,$Lcur,$strain,$delta_tension,$raw_elastic_tension,$total_tension,$is_slack"
	}
	close $elem_file
	if {$count > 0} {
		set mean_abs_strain [expr $sum_abs_strain / double($count)]
	} else {
		set mean_abs_strain 0.0
		set min_estimated_tension 0.0
	}
	set summary_needs_header [expr {![file exists $summary_path]}]
	set summary_file [open $summary_path a]
	if {$summary_needs_header} {
		puts $summary_file "time,max_abs_strain,mean_abs_strain,max_abs_tension_N,min_estimated_tension_N,max_abs_raw_elastic_tension_N,slack_element_count,max_element"
	}
	puts $summary_file "$currentTime,$max_abs_strain,$mean_abs_strain,$max_abs_tension,$min_estimated_tension,$max_abs_raw_elastic_tension,$slack_count,$max_element"
	close $summary_file
}

proc apply_explicit_aero_damping_force {} {
	global STKO_VAR_time
	global STKO_VAR_increment
	global CD_x
	global CD_y
	global dCL_x
	global dCL_y
	global wind_velocity_per_element_H
	global wind_velocity_per_element_V
	global time
	global wind_time_vector
	global ro_air
	global B
	global L
	global dcl_derivative_scale
	global delta_D_min
	global delta_D_max
	global use_deformed_element_direction
	global enable_explicit_aero_damping_force
	global explicit_aero_damping_force_scale
	global explicit_aero_damping_force_log_stride
	global explicit_aero_damping_pattern_tag
	global explicit_aero_damping_series_tag
	global explicit_aero_damping_pattern_active
	global opensees_output_dir

	if {![info exists enable_explicit_aero_damping_force]} {set enable_explicit_aero_damping_force 0}
	if {![info exists explicit_aero_damping_force_scale]} {set explicit_aero_damping_force_scale 1.0}
	if {![info exists explicit_aero_damping_force_log_stride]} {set explicit_aero_damping_force_log_stride 20}
	if {![info exists dcl_derivative_scale]} {set dcl_derivative_scale 57.2957795131}
	if {![info exists delta_D_min]} {set delta_D_min -1.0e30}
	if {![info exists delta_D_max]} {set delta_D_max 1.0e30}
	if {![info exists use_deformed_element_direction]} {set use_deformed_element_direction 1}
	if {![info exists explicit_aero_damping_pattern_tag]} {set explicit_aero_damping_pattern_tag 900000}
	if {![info exists explicit_aero_damping_series_tag]} {set explicit_aero_damping_series_tag 900000}

	if {[info exists explicit_aero_damping_pattern_active] && $explicit_aero_damping_pattern_active} {
		remove loadPattern $explicit_aero_damping_pattern_tag
		set explicit_aero_damping_pattern_active 0
	}

	if {!$enable_explicit_aero_damping_force} {
		return
	}

	if {![info exists STKO_VAR_time]} {
		set currentTime [getTime]
	} else {
		set currentTime $STKO_VAR_time
	}

	set node_tags [getNodeTags]
	foreach node $node_tags {
		set fx($node) 0.0
		set fy($node) 0.0
		set fz($node) 0.0
	}

	set total_abs_force 0.0
	set max_abs_force 0.0

	foreach ele [getEleTags] {
		set vmean [list 0.0 0.0 0.0]
		set elenodes [eleNodes $ele]
		set nnodes [llength $elenodes]

		foreach node $elenodes {
			set v [nodeVel $node]
			for {set i 0} {$i < 3} {incr i} {
				lset vmean $i [expr [lindex $vmean $i]+[lindex $v $i]]
			}
		}

		for {set i 0} {$i < 3} {incr i} {
			lset vmean $i [expr [lindex $vmean $i] / $nnodes.0]
		}

		if {$use_deformed_element_direction} {
			set basis [get_element_local_aero_basis $ele]
			set byx [lindex $basis 3]
			set byy [lindex $basis 4]
			set byz [lindex $basis 5]
			set bzx [lindex $basis 6]
			set bzy [lindex $basis 7]
			set bzz [lindex $basis 8]
		} else {
			set byx 0.0
			set byy 1.0
			set byz 0.0
			set bzx 0.0
			set bzy 0.0
			set bzz 1.0
		}

		set external_wind_vector_H [lindex $wind_velocity_per_element_H [expr $ele-1]]
		set external_wind_vector_V [lindex $wind_velocity_per_element_V [expr $ele-1]]

		if {[info exists wind_time_vector]} {set aero_time $wind_time_vector} else {set aero_time $time}
		set v_wind_y [interpolate $currentTime $aero_time $external_wind_vector_H]
		set v_wind_z [interpolate $currentTime $aero_time $external_wind_vector_V]

		set v_cable_global_x [lindex $vmean 0]
		set v_cable_global_y [lindex $vmean 1]
		set v_cable_global_z [lindex $vmean 2]
		set v_rel_global_x [expr 0.0 - $v_cable_global_x]
		set v_rel_global_y [expr $v_wind_y - $v_cable_global_y]
		set v_rel_global_z [expr $v_wind_z - $v_cable_global_z]

		set v_cable_y [expr $v_cable_global_x*$byx + $v_cable_global_y*$byy + $v_cable_global_z*$byz]
		set v_cable_z [expr $v_cable_global_x*$bzx + $v_cable_global_y*$bzy + $v_cable_global_z*$bzz]
		set v_rel_y [expr $v_rel_global_x*$byx + $v_rel_global_y*$byy + $v_rel_global_z*$byz]
		set v_rel_z [expr $v_rel_global_x*$bzx + $v_rel_global_y*$bzy + $v_rel_global_z*$bzz]
		set v_total [expr (($v_rel_y**2)+($v_rel_z**2))**0.5]

		# Match adapt_damp's aerodynamic lookup convention: keep the along-wind
		# relative component positive before converting to an attack angle.
		if {$v_rel_y < 0.0} {
			set v_rel_angle_y [expr -$v_rel_y]
			set v_rel_angle_z [expr -$v_rel_z]
		} else {
			set v_rel_angle_y $v_rel_y
			set v_rel_angle_z $v_rel_z
		}
		if {abs($v_rel_angle_y) < 1.0e-12} {
			set alpha [expr atan2($v_rel_angle_z, $v_rel_angle_y)]
		} else {
			set alpha [expr atan($v_rel_angle_z/$v_rel_angle_y)]
		}
		set alpha_deg [expr abs($alpha)/3.141592653589793*180.0]
		set alpha_max [lindex $CD_x end]
		if {$alpha_deg > $alpha_max} {set alpha_deg $alpha_max}

		set CD [interpolate $alpha_deg $CD_x $CD_y]
		set dCL_table [interpolate $alpha_deg $dCL_x $dCL_y]
		set dCL [expr $dCL_table * $dcl_derivative_scale]
		set delta_D [expr $dCL + $CD]
		if {$delta_D < $delta_D_min} {set delta_D $delta_D_min}
		if {$delta_D > $delta_D_max} {set delta_D $delta_D_max}

		# Equivalent explicit aerodynamic damping coefficient for the element.
		# c_aero < 0 injects energy because F = -c_aero * velocity.
		set c_aero [expr $explicit_aero_damping_force_scale * $ro_air * $v_total * $B * $L * $delta_D / 2.0]
		set ele_f_local_y [expr -$c_aero * $v_cable_y]
		set ele_f_local_z [expr -$c_aero * $v_cable_z]
		set ele_fx [expr $ele_f_local_y*$byx + $ele_f_local_z*$bzx]
		set ele_fy [expr $ele_f_local_y*$byy + $ele_f_local_z*$bzy]
		set ele_fz [expr $ele_f_local_y*$byz + $ele_f_local_z*$bzz]

		foreach node $elenodes {
			set fx($node) [expr $fx($node) + $ele_fx / $nnodes.0]
			set fy($node) [expr $fy($node) + $ele_fy / $nnodes.0]
			set fz($node) [expr $fz($node) + $ele_fz / $nnodes.0]
		}

		set ele_abs_force [expr (($ele_fx**2)+($ele_fy**2)+($ele_fz**2))**0.5]
		set total_abs_force [expr $total_abs_force + $ele_abs_force]
		if {$ele_abs_force > $max_abs_force} {set max_abs_force $ele_abs_force}
	}

	pattern Plain $explicit_aero_damping_pattern_tag $explicit_aero_damping_series_tag {
		foreach node [getNodeTags] {
			load $node $fx($node) $fy($node) $fz($node) 0 0 0
		}
	}
	set explicit_aero_damping_pattern_active 1

	if {![info exists STKO_VAR_increment] || [expr {$STKO_VAR_increment % $explicit_aero_damping_force_log_stride}] == 0} {
		if {[info exists opensees_output_dir]} {
			set logfile [open "$opensees_output_dir/explicit_aero_damping_force_log.txt" a]
		} else {
			set logfile [open "Output/explicit_aero_damping_force_log.txt" a]
		}
		puts $logfile "$currentTime $total_abs_force $max_abs_force $explicit_aero_damping_force_scale"
		close $logfile
	}
}

proc adapt_damp {} {

	global STKO_VAR_analyze_done
	global STKO_VAR_time
	global CD_x
	global CD_y
	global dCL_x
	global dCL_y
	global wind_velocity_per_element_H
	global wind_velocity_per_element_V
	global time
	global wind_time_vector
	global ro_air
	global B
	global L
	global MassM
	global omegaN
	global xi_structural
	global enable_aero_damping_update
	global dcl_derivative_scale
	global delta_D_min
	global delta_D_max
	global use_deformed_element_direction
	global damping_writeback_mode
	global STKO_VAR_increment
	global damping_debug
	global damping_log_stride
	global opensees_output_dir

    if {![info exists STKO_VAR_analyze_done]} {
        puts ">>>CheckPoint >DONE_IN< STKO_VAR_analyze_done not defined yet. Skipping adapt_damp."
        return
    }

    if {![info exists STKO_VAR_time]} {
        puts ">>>CheckPoint >TIME_IN< STKO_VAR_time not defined yet. Skipping adapt_damp."
        return
    }



	# ✅ 新增：用于存储上一步阻尼
	global prev_xi_total_list

	if {$STKO_VAR_analyze_done == 0} {
		if {![info exists enable_aero_damping_update]} {set enable_aero_damping_update 1}
		if {!$enable_aero_damping_update} {
			return
		}
		if {![info exists dcl_derivative_scale]} {set dcl_derivative_scale 57.2957795131}
		if {![info exists delta_D_min]} {set delta_D_min -1.0e30}
		if {![info exists delta_D_max]} {set delta_D_max 1.0e30}
		if {![info exists use_deformed_element_direction]} {set use_deformed_element_direction 1}
		if {![info exists damping_writeback_mode]} {set damping_writeback_mode "record_only"}
		
		set dd [expr int($STKO_VAR_time/10)*0.1]
		if {$dd > 0.1} {set dd -0.1}

		foreach ele [getEleTags] {
			set vmean [list 0.0 0.0 0.0]
			set elenodes [eleNodes $ele]
			set nnodes [llength $elenodes]

			foreach node $elenodes {
				set v [nodeVel $node]
				for {set i 0} {$i < 3} {incr i} { 
					lset vmean $i [expr [lindex $vmean $i]+[lindex $v $i]]
				}
			}

			for {set i 0} {$i < 3} {incr i} { 
				lset vmean $i [expr [lindex $vmean $i] / $nnodes.0]
			}

			set currentTime [getTime]

			if {$use_deformed_element_direction} {
				set basis [get_element_local_aero_basis $ele]
				set byx [lindex $basis 3]
				set byy [lindex $basis 4]
				set byz [lindex $basis 5]
				set bzx [lindex $basis 6]
				set bzy [lindex $basis 7]
				set bzz [lindex $basis 8]
			} else {
				set byx 0.0
				set byy 1.0
				set byz 0.0
				set bzx 0.0
				set bzy 0.0
				set bzz 1.0
			}

			set external_wind_vector_H [lindex $wind_velocity_per_element_H [expr $ele-1]]
			set external_wind_vector_V [lindex $wind_velocity_per_element_V [expr $ele-1]]

			if {[info exists wind_time_vector]} {set aero_time $wind_time_vector} else {set aero_time $time}
			set v_wind_x [interpolate $currentTime $aero_time $external_wind_vector_H]
			set v_wind_z [interpolate $currentTime $aero_time $external_wind_vector_V]

			set v_cable_global_x [lindex $vmean 0]
			set v_cable_global_y [lindex $vmean 1]
			set v_cable_global_z [lindex $vmean 2]
			set v_rel_global_x [expr 0.0 - $v_cable_global_x]
			set v_rel_global_y [expr $v_wind_x - $v_cable_global_y]
			set v_rel_global_z [expr $v_wind_z - $v_cable_global_z]

			set v_rel_x_raw [expr $v_rel_global_x*$byx + $v_rel_global_y*$byy + $v_rel_global_z*$byz]
			set v_rel_z_raw [expr $v_rel_global_x*$bzx + $v_rel_global_y*$bzy + $v_rel_global_z*$bzz]

			if {$v_rel_x_raw < 0.0} {
				set v_rel_x [expr -$v_rel_x_raw]
				set v_rel_z [expr -$v_rel_z_raw]
			} else {
				set v_rel_x $v_rel_x_raw
				set v_rel_z $v_rel_z_raw
			}
			set v_total [expr (($v_rel_x**2)+($v_rel_z**2))**0.5]

			if {abs($v_rel_x) < 1.0e-12} {
				set alpha [expr atan2($v_rel_z, $v_rel_x)]
			} else {
				set alpha [expr atan($v_rel_z/$v_rel_x)]
			}

			set alpha_deg [expr abs($alpha)/3.141592653589793*180.0]
			set alpha_max [lindex $CD_x end]
			if {$alpha_deg > $alpha_max} {set alpha_deg $alpha_max}
			set CD  [interpolate $alpha_deg $CD_x $CD_y]
			# dC_L.txt is tabulated per degree from the original MATLAB file.
			# Den Hartog's criterion requires dC_L/dalpha with alpha in radians.
			set dCL_table [interpolate $alpha_deg $dCL_x $dCL_y]
			set dCL [expr $dCL_table * $dcl_derivative_scale]
			set delta_D [expr $dCL + $CD]
			if {$delta_D < $delta_D_min} {set delta_D $delta_D_min}
			if {$delta_D > $delta_D_max} {set delta_D $delta_D_max}

			if {![info exists xi_structural]} {set xi_structural 0.01}
			if {$enable_aero_damping_update} {
				set xi_aero [expr $ro_air*$v_total*$B*$L/4/$MassM/$omegaN*$delta_D]
			} else {
				set xi_aero 0.0
			}
			set xi_total [expr $xi_structural + $xi_aero]

			set should_writeback 1
			set xi_writeback $xi_total
			if {$damping_writeback_mode eq "record_only"} {
				set should_writeback 0
			} elseif {$damping_writeback_mode eq "structural_only"} {
				set xi_writeback $xi_structural
			} elseif {$damping_writeback_mode eq "aero_only"} {
				set xi_writeback $xi_aero
			} elseif {$damping_writeback_mode eq "total"} {
				set xi_writeback $xi_total
			} else {
				error "Unknown damping_writeback_mode: $damping_writeback_mode"
			}

			# ✅ 新增：检查是否变化
			set prev_xi 0.0
			if {[info exists prev_xi_total_list($ele)]} {
				set prev_xi $prev_xi_total_list($ele)
			}
			set diff [expr abs($xi_total - $prev_xi)]
			if {$diff > 1e-6} {
				if {$damping_debug} {
					puts ">>> Time $STKO_VAR_time | Element $ele: Damping changed from $prev_xi to $xi_total"
				}

				if {![info exists STKO_VAR_increment] || [expr {$STKO_VAR_increment % $damping_log_stride}] == 0} {
					if {[info exists opensees_output_dir]} {
						set logfile [open "$opensees_output_dir/damping_change_log.txt" a]
					} else {
						set logfile [open "Output/damping_change_log.txt" a]
					}
					puts $logfile "$STKO_VAR_time $ele $prev_xi $xi_total"
					close $logfile
				}
			}

			# ✅ 更新全局记录
			set prev_xi_total_list($ele) $xi_total

			if {$should_writeback} {
				setElementRayleighDampingFactors $ele [expr 2*$xi_writeback*$omegaN] 0.0 0.0 0.0
			}
		}
	}
}


# append to custom functions
if {![info exists enable_explicit_aero_damping_force]} {set enable_explicit_aero_damping_force 0}
if {![info exists explicit_aero_damping_series_tag]} {set explicit_aero_damping_series_tag 900000}
if {$enable_explicit_aero_damping_force} {
	timeSeries Constant $explicit_aero_damping_series_tag
	global STKO_VAR_OnBeforeAnalyze_CustomFunctions
	lappend STKO_VAR_OnBeforeAnalyze_CustomFunctions apply_explicit_aero_damping_force
	puts ">>> Registered explicit aerodynamic damping force: $STKO_VAR_OnBeforeAnalyze_CustomFunctions"
}

if {![info exists enable_quasi_steady_aero_force]} {set enable_quasi_steady_aero_force 0}
if {![info exists quasi_steady_aero_series_tag]} {set quasi_steady_aero_series_tag 901000}
if {$enable_quasi_steady_aero_force} {
	timeSeries Constant $quasi_steady_aero_series_tag
	global STKO_VAR_OnBeforeAnalyze_CustomFunctions
	lappend STKO_VAR_OnBeforeAnalyze_CustomFunctions apply_quasi_steady_aero_force
	puts ">>> Registered quasi-steady aerodynamic force: $STKO_VAR_OnBeforeAnalyze_CustomFunctions"
}

if {![info exists enable_incremental_quasi_steady_aero_force]} {set enable_incremental_quasi_steady_aero_force 0}
if {![info exists incremental_quasi_steady_aero_series_tag]} {set incremental_quasi_steady_aero_series_tag 902000}
if {$enable_incremental_quasi_steady_aero_force} {
	timeSeries Constant $incremental_quasi_steady_aero_series_tag
	global STKO_VAR_OnBeforeAnalyze_CustomFunctions
	lappend STKO_VAR_OnBeforeAnalyze_CustomFunctions apply_incremental_quasi_steady_aero_force
	puts ">>> Registered incremental quasi-steady aerodynamic force: $STKO_VAR_OnBeforeAnalyze_CustomFunctions"
}

global STKO_VAR_OnAfterAnalyze_CustomFunctions
lappend STKO_VAR_OnAfterAnalyze_CustomFunctions adapt_damp
lappend STKO_VAR_OnAfterAnalyze_CustomFunctions log_element_strain_tension
puts ">>> !!!!!Registered functions after append: $STKO_VAR_OnAfterAnalyze_CustomFunctions"

