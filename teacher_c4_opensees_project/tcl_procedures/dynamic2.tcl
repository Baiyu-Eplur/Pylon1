set dynamic_debug 0
if {$dynamic_debug} {
	puts ">>> STKO_VAR_OnAfterAnalyze_CustomFunctions before loop: $STKO_VAR_OnAfterAnalyze_CustomFunctions"
}
if {![info exists STKO_VAR_time]} {
	set STKO_VAR_time 0.0
}

# analyses command
# domainChange
# constraints Transformation
# numberer RCM
# system UmfPack
# test NormUnbalance 0.0001 20  
# algorithm Newton
# integrator Newmark 0.0 0.0
# analysis Transient
# ======================================================================================
# ADAPTIVE TRANSIENT ANALYSIS
# ======================================================================================

# ======================================================================================
# USER INPUT DATA
# ======================================================================================

# duration and initial time step
# set total_duration 10.0
# set initial_num_incr 100

# =================================================================================
# STKO COMMON VARIABLES (STKO_VAR_***)
# =================================================================================
set STKO_VAR_process_id 0
# # The result from analyze command  (0 if succesfull)
# set STKO_VAR_analyze_done 0
# # The alternative result from after-analyze custom functions (0 if succesfull)
# set STKO_VAR_afterAnalyze_done 0
# # The increment counter in the current stage
# set STKO_VAR_increment 0
# # The current time
# set STKO_VAR_time 0.0
# # The current time increment
# set STKO_VAR_time_increment 0.0
# # The initial time increment
# set STKO_VAR_initial_time_increment 0.0
# # The current stage percentage
# set STKO_VAR_percentage 0.0
# # The last number of iterations
# set STKO_VAR_num_iter 0
# # The last error norm
# set STKO_VAR_error_norm 0.0
# # A list of custom functions called before solving the current time step
if {![info exists STKO_VAR_OnBeforeAnalyze_CustomFunctions]} {
	set STKO_VAR_OnBeforeAnalyze_CustomFunctions {}
}
# # A list of custom functions called after solving the current time step
# set STKO_VAR_OnAfterAnalyze_CustomFunctions {}
# # A list of monitor functions
# set STKO_VAR_MonitorFunctions {}
# # for backward compatibility (STKO version < 3.1.0).
# # It is now deprecated and will be removed in future versions.
# set all_custom_functions {}

proc write_analysis_status {status message} {
	global STKO_VAR_time
	global STKO_VAR_percentage
	global STKO_VAR_increment
	global STKO_VAR_analyze_done
	global total_duration
	puts "ANALYSIS_STATUS $status"
	puts "ANALYSIS_MESSAGE $message"
	if {[info exists STKO_VAR_time]} {puts "ANALYSIS_TIME $STKO_VAR_time"}
	if {[info exists total_duration]} {puts "ANALYSIS_TARGET_TIME $total_duration"}
	if {[info exists STKO_VAR_percentage]} {puts "ANALYSIS_PROGRESS [expr $STKO_VAR_percentage * 100.0]"}
	if {[info exists STKO_VAR_increment]} {puts "ANALYSIS_INCREMENT $STKO_VAR_increment"}
	if {[info exists STKO_VAR_analyze_done]} {puts "ANALYZE_RETURN_CODE $STKO_VAR_analyze_done"}
}

proc check_event_stop {} {
	global event_stop_enabled
	global event_stop_max_displacement_m
	global event_stop_max_velocity_mps
	global event_stop_max_acceleration_mps2
	global event_stop_min_effective_damping
	global event_stop_max_alpha_deg
	global event_stop_max_clipped_fraction
	global event_stop_reason
	global event_stop_max_disp
	global event_stop_max_vel
	global event_stop_max_accel
	global event_stop_min_xi
	global event_stop_max_alpha
	global event_stop_clipped_fraction
	global prev_xi_total_list
	global incremental_qs_max_alpha_current_deg
	global incremental_qs_clipped_fraction
	global STKO_VAR_time
	global opensees_output_dir

	if {![info exists event_stop_enabled]} {set event_stop_enabled 0}
	if {!$event_stop_enabled} {return 0}
	if {![info exists event_stop_max_displacement_m]} {set event_stop_max_displacement_m 1.0e30}
	if {![info exists event_stop_max_velocity_mps]} {set event_stop_max_velocity_mps 1.0e30}
	if {![info exists event_stop_max_acceleration_mps2]} {set event_stop_max_acceleration_mps2 1.0e30}
	if {![info exists event_stop_min_effective_damping]} {set event_stop_min_effective_damping -1.0e30}
	if {![info exists event_stop_max_alpha_deg]} {set event_stop_max_alpha_deg 1.0e30}
	if {![info exists event_stop_max_clipped_fraction]} {set event_stop_max_clipped_fraction 1.0e30}

	set max_disp 0.0
	set max_vel 0.0
	set max_accel 0.0
	foreach node [getNodeTags] {
		set d [nodeDisp $node]
		set v [nodeVel $node]
		set a [nodeAccel $node]
		set disp_y [lindex $d 1]
		set disp_z [lindex $d 2]
		set vel_y [lindex $v 1]
		set vel_z [lindex $v 2]
		set accel_y [lindex $a 1]
		set accel_z [lindex $a 2]
		set disp_env [expr sqrt($disp_y*$disp_y + $disp_z*$disp_z)]
		set vel_env [expr sqrt($vel_y*$vel_y + $vel_z*$vel_z)]
		set accel_env [expr sqrt($accel_y*$accel_y + $accel_z*$accel_z)]
		if {$disp_env > $max_disp} {set max_disp $disp_env}
		if {$vel_env > $max_vel} {set max_vel $vel_env}
		if {$accel_env > $max_accel} {set max_accel $accel_env}
	}

	set min_xi 1.0e30
	if {[array exists prev_xi_total_list]} {
		foreach ele [array names prev_xi_total_list] {
			if {$prev_xi_total_list($ele) < $min_xi} {set min_xi $prev_xi_total_list($ele)}
		}
	}
	set max_alpha 0.0
	if {[info exists incremental_qs_max_alpha_current_deg]} {
		set max_alpha $incremental_qs_max_alpha_current_deg
	}
	set clipped_fraction 0.0
	if {[info exists incremental_qs_clipped_fraction]} {
		set clipped_fraction $incremental_qs_clipped_fraction
	}

	set reason ""
	if {$max_disp >= $event_stop_max_displacement_m} {
		set reason "event_stop_max_displacement"
	} elseif {$max_vel >= $event_stop_max_velocity_mps} {
		set reason "event_stop_max_velocity"
	} elseif {$max_accel >= $event_stop_max_acceleration_mps2} {
		set reason "event_stop_max_acceleration"
	} elseif {$min_xi <= $event_stop_min_effective_damping} {
		set reason "event_stop_min_effective_damping"
	} elseif {$max_alpha >= $event_stop_max_alpha_deg} {
		set reason "event_stop_max_alpha"
	} elseif {$clipped_fraction >= $event_stop_max_clipped_fraction} {
		set reason "event_stop_clipped_fraction"
	}

	if {$reason ne ""} {
		set event_stop_reason $reason
		set event_stop_max_disp $max_disp
		set event_stop_max_vel $max_vel
		set event_stop_max_accel $max_accel
		set event_stop_min_xi $min_xi
		set event_stop_max_alpha $max_alpha
		set event_stop_clipped_fraction $clipped_fraction
		if {[info exists opensees_output_dir]} {
			set event_path "$opensees_output_dir/event_stop_log.txt"
		} else {
			set event_path "Output/event_stop_log.txt"
		}
		set event_file [open $event_path a]
		puts $event_file "$STKO_VAR_time $reason $max_disp $max_vel $max_accel $min_xi $max_alpha $clipped_fraction"
		close $event_file
		return 1
	}
	return 0
}

# # Call functions before the analyze command.
proc STKO_CALL_OnBeforeAnalyze {} {
	global STKO_VAR_OnBeforeAnalyze_CustomFunctions
	foreach item $STKO_VAR_OnBeforeAnalyze_CustomFunctions {
		$item
	}
}
# Call functions after the analyze command.
# proc STKO_CALL_OnAfterAnalyze {} {
	# global STKO_VAR_analyze_done
	# global STKO_VAR_OnAfterAnalyze_CustomFunctions
	# global all_custom_functions
	# # global STKO_VAR_MonitorFunctions
	# foreach item $STKO_VAR_OnAfterAnalyze_CustomFunctions {
		# $item
	# }
	# if {$STKO_VAR_analyze_done == 0} {
		# foreach item $all_custom_functions {
			# $item
		# }
		# #foreach item $STKO_VAR_MonitorFunctions {
		# #	$item
		# #}
	# }
# }

proc STKO_CALL_OnAfterAnalyze {} {
	global STKO_VAR_analyze_done
	global STKO_VAR_OnAfterAnalyze_CustomFunctions
	global all_custom_functions
	global dynamic_debug

	# 检查是否有函数被注册进 STKO_VAR_OnAfterAnalyze_CustomFunctions
	if {$dynamic_debug} {
		puts ">>> CheckPoint >Excution Start< in Calling STKO_CALL_OnAfterAnalyze..."
		puts ">>> Registered functions: $STKO_VAR_OnAfterAnalyze_CustomFunctions"
	}

	foreach item $STKO_VAR_OnAfterAnalyze_CustomFunctions {
		if {$dynamic_debug} {
			puts ">>> CheckPoint >Excution In Process< Calling custom afterAnalyze function: $item"
		}
		$item
	}

	if {$STKO_VAR_analyze_done == 0} {
		foreach item $all_custom_functions {
			if {$dynamic_debug} {
				puts ">>> Calling custom function (legacy): $item"
			}
			$item
		}
	}
	
}


# parameters for adaptive time step
set max_factor 1.0
set min_factor 1e-06
set max_factor_increment 1.5
set min_factor_increment 1e-06
set max_iter 20
set desired_iter 10

set STKO_VAR_increment 1
set factor 1.0
set old_factor $factor
set STKO_VAR_time 0.0
set initial_time_increment [expr $total_duration / $initial_num_incr]
set time_tolerance [expr abs($initial_time_increment) * 1.0e-8]

set STKO_VAR_initial_time_increment $initial_time_increment

if {$dynamic_debug} {
	puts ">>> STKO_VAR_OnAfterAnalyze_CustomFunctions before loop: $STKO_VAR_OnAfterAnalyze_CustomFunctions"
}

global STKO_VAR_analyze_done
global STKO_VAR_time
global STKO_VAR_time_increment

while 1 {
	
	# check end of analysis
	if {[expr abs($STKO_VAR_time)] >= [expr abs($total_duration)]} {
		if {$STKO_VAR_process_id == 0} {
			puts "Target time has been reached. Current time = $STKO_VAR_time"
			puts "SUCCESS."
		}
		write_analysis_status "success" "target_time_reached"
		break
	}
	
	# compute new adapted time increment
	set STKO_VAR_time_increment [expr $initial_time_increment * $factor]
	if {[expr abs($STKO_VAR_time + $STKO_VAR_time_increment)] > [expr abs($total_duration) - $time_tolerance]} {
		set STKO_VAR_time_increment [expr $total_duration - $STKO_VAR_time]
	}
	
	# update integrator
	integrator Newmark 0.5 0.25
	
	# before analyze
	STKO_CALL_OnBeforeAnalyze
	
	# perform this step
	set STKO_VAR_analyze_done [analyze 1 $STKO_VAR_time_increment]
	
	# update common variables
	if {$STKO_VAR_analyze_done == 0} {
		set STKO_VAR_num_iter [testIter]
		set STKO_VAR_time [expr $STKO_VAR_time + $STKO_VAR_time_increment]
		set STKO_VAR_percentage [expr $STKO_VAR_time/$total_duration]
		set norms [testNorms]
		if {$STKO_VAR_num_iter > 0} {set STKO_VAR_error_norm [lindex $norms [expr $STKO_VAR_num_iter-1]]} else {set STKO_VAR_error_norm 0.0}
	}
	
	
	# 检查 STKO_VAR_analyze_done 是否存在!!!!
	if {![info exists STKO_VAR_analyze_done]} {
		puts ">>> CheckPoint >DONE_OUT< STKO_VAR_analyze_done not defined yet. Skipping adapt_damp."
		return
	} else {
		if {$dynamic_debug} {
			puts ">>> CheckPoint>DONE_OUT< STKO_VAR_analyze_done = $STKO_VAR_analyze_done."
		}
	}

	# 检查 STKO_VAR_time 是否存在!!!!!
	if {![info exists STKO_VAR_time]} {
		puts ">>> CheckPoint >DONE_OUT< STKO_VAR_time not defined yet. Skipping adapt_damp."
		return
	} else {
		if {$dynamic_debug} {
			puts ">>> CheckPoint >DONE_OUT< STKO_VAR_time = $STKO_VAR_time."
		}
	}

	
	# after analyze
	set STKO_VAR_afterAnalyze_done 0
	STKO_CALL_OnAfterAnalyze
	if {$STKO_VAR_analyze_done == 0 && [check_event_stop]} {
		if {$STKO_VAR_process_id == 0} {
			puts "EVENT STOP: $event_stop_reason at time $STKO_VAR_time"
		}
		write_analysis_status "event_stop" $event_stop_reason
		break
	}
	
	# check convergence
	if {$STKO_VAR_analyze_done == 0} {
		
		# print statistics
		if {$STKO_VAR_process_id == 0} {
			puts [format "Increment: %6d | Iterations: %4d | Norm: %8.3e | Progress: %7.3f %%" $STKO_VAR_increment $STKO_VAR_num_iter  $STKO_VAR_error_norm [expr $STKO_VAR_percentage*100.0]]
		# 显示示例阻尼系数（假设你全局定义了 prev_xi_total_list 变量）
			# 这里以第1个单元为例
			if {[info exists prev_xi_total_list(1)]} {
				puts [format ">>> Damping of Element 1 at time %.3f = %.6f" $STKO_VAR_time $prev_xi_total_list(1)]
			} else {
				puts ">>> Damping of Element 1 not yet initialized."
			}
		}
		
		# update adaptive factor
		set factor_increment [expr min($max_factor_increment, [expr double($desired_iter) / double($STKO_VAR_num_iter)])]
		
		# check STKO_VAR_afterAnalyze_done. Simulate a reduction similar to non-convergence
		if {$STKO_VAR_afterAnalyze_done != 0} {
			set factor_increment [expr max($min_factor_increment, [expr double($desired_iter) / double($max_iter)])]
			if {$STKO_VAR_process_id == 0} {
				puts "Reducing increment factor due to custom error controls. Factor = $factor"
			}
		}
		
		set factor [expr $factor * $factor_increment]
		if {$factor > $max_factor} {
			set factor $max_factor
		}
		if {$STKO_VAR_process_id == 0} {
			if {$factor > $old_factor} {
				puts "Increasing increment factor due to faster convergence. Factor = $factor"
			}
		}
		set old_factor $factor
		
		# ── REALTIME MONITOR: flush state every step ──────────────────
		if {0 && [expr $STKO_VAR_increment % 1] == 0} {
			if {[info exists opensees_output_dir]} {
				set rt_file [open "$opensees_output_dir/realtime_state.txt" w]
			} else {
				set rt_file [open "Output/realtime_state.txt" w]
			}
			set mid_node [expr int(([llength [getNodeTags]] + 1) / 2)]
			set disp_mid  [nodeDisp  $mid_node]
			set vel_mid   [nodeVel   $mid_node]
			set accel_mid [nodeAccel $mid_node]
			puts $rt_file "TIME $STKO_VAR_time"
			puts $rt_file "PROGRESS [expr $STKO_VAR_percentage * 100.0]"
			puts $rt_file "DISP_Y  [lindex $disp_mid  1]"
			puts $rt_file "DISP_Z  [lindex $disp_mid  2]"
			puts $rt_file "VEL_Y   [lindex $vel_mid   1]"
			puts $rt_file "VEL_Z   [lindex $vel_mid   2]"
			puts $rt_file "ACCEL_Y [lindex $accel_mid 1]"
			puts $rt_file "ACCEL_Z [lindex $accel_mid 2]"
			close $rt_file
		}
		# ── END REALTIME MONITOR ──────────────────────────────────────

		# increment time step
		incr STKO_VAR_increment
		
	} else {
		
		# update adaptive factor
		set STKO_VAR_num_iter $max_iter
		set factor_increment [expr max($min_factor_increment, [expr double($desired_iter) / double($STKO_VAR_num_iter)])]
		set factor [expr $factor * $factor_increment]
		if {$STKO_VAR_process_id == 0} {
			puts "Reducing increment factor due to non convergence. Factor = $factor"
		}
		if {$factor < $min_factor} {
			if {$STKO_VAR_process_id == 0} {
				puts "ERROR: current factor is less then the minimum allowed ($factor < $min_factor)"
				puts "Giving up"
			}
			write_analysis_status "failed" "analysis_did_not_converge_min_factor_reached"
			error "ERROR: the analysis did not converge"
		}
	}
	
}

wipeAnalysis

# Done!
puts "ANALYSIS SUCCESSFULLY FINISHED"
