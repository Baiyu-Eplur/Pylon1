# Acquire the procedure to load a specific column from a txt file
source "tcl_procedures/readColumnFromFile.tcl"

# This operation should be done onese at the beginning to acquire time and length of the vectors containing the wind data
if {![info exists wind_time_file]} {
	set wind_time_file "data/aero_coeffs/time.txt"
}
if {![info exists wind_data_dir]} {
	set wind_data_dir "data/wind/SIM1"
}
set filename $wind_time_file; # Name of the file
set column 0;                       # Column to acquire 
set time [readColumnFromFile $filename $column]; # Time vector supporting the wind simulation
set wind_time_vector $time; # Preserve the wind/force time vector even if static solvers reuse the variable name "time"
set ndata [llength $time]; # Length of the wind simulation

# Preallocation of the final result
set wind_velocity_per_element_H {}

# The following for loop explores all the finite elements in the model, acquires the wind velocities at the two nodes,
# it averages them, and then it stores them in a matrix having 
# number or rows equal to the number of elements
# number of columns equal to the simulated wind velocities
foreach ele [getEleTags] {

            # List intialisation for the final result #################
			set num_columns $ndata  ;# You can change this to any number you want
			# Create an empty list
			set vmean_simulated {}
			# Populate the list with zeros
			for {set i 0} {$i < $num_columns} {incr i} {
			lappend vmean_simulated 0
			}
			############################################################
			
			set elenodes [eleNodes $ele];   # it proides the ID of the nodes belonging to the finite element	
			set nnodes [llength $elenodes]; # it provides the number of nodes of the finite element 
			
			# Forloop on the nodes of each element to acquire the wind velocities at the two nodes and average them
			foreach node $elenodes {
				
				set filename "${wind_data_dir}/NODE_${node}_wind_H.txt"; # Definition of the name of the file
				
				set column 0; # Definition of the column ID in txt file
				set vel [readColumnFromFile $filename $column]; # Acquisition of the data from the file
				
				# Forloop to populate the simulated vector of wind velocity.
				for {set i 0} {$i < $num_columns} {incr i} { 
					set v_sum [lindex $vmean_simulated $i]
					set v_cur [lindex $vel $i]

					if {$v_sum eq ""} { set v_sum 0.0 }
					if {$v_cur eq ""} { set v_cur 0.0 }

					lset vmean_simulated $i [expr {$v_sum + $v_cur}]
				}

				# for {set i 0} {$i < $num_columns} {incr i} { 
				#	lset vmean_simulated $i [expr [lindex $vmean_simulated $i]+[lindex $vel $i]]
				#}
			}
			
			# Forloop to average the wind velocity for the single element
			for {set i 0} {$i < $num_columns} {incr i} { 
			lset vmean_simulated $i [expr [lindex $vmean_simulated $i] / $nnodes.0]
			}
			
			lappend wind_velocity_per_element_H $vmean_simulated

		}
		
# Preallocation of the final result
set wind_velocity_per_element_V {}

# The following for loop explores all the finite elements in the model, acquires the wind velocities at the two nodes,
# it averages them, and then it stores them in a matrix having 
# number or rows equal to the number of elements
# number of columns equal to the simulated wind velocities
foreach ele [getEleTags] {

            # List intialisation for the final result #################
			set num_columns $ndata  ;# You can change this to any number you want
			# Create an empty list
			set vmean_simulated {}
			# Populate the list with zeros
			for {set i 0} {$i < $num_columns} {incr i} {
			lappend vmean_simulated 0
			}
			############################################################
			
			set elenodes [eleNodes $ele];   # it proides the ID of the nodes belonging to the finite element	
			set nnodes [llength $elenodes]; # it provides the number of nodes of the finite element 
			
			# Forloop on the nodes of each element to acquire the wind velocities at the two nodes and average them
			foreach node $elenodes {
				
				set filename "${wind_data_dir}/NODE_${node}_wind_V.txt"; # Definition of the name of the file
				
				set column 0; # Definition of the column ID in txt file
				set vel [readColumnFromFile $filename $column]; # Acquisition of the data from the file
				
				# Forloop to populate the simulated vector of wind velocity
				for {set i 0} {$i < $num_columns} {incr i} { 
					lset vmean_simulated $i [expr [lindex $vmean_simulated $i]+[lindex $vel $i]]
				}
			}
			
			# Forloop to average the wind velocity for the single element
			for {set i 0} {$i < $num_columns} {incr i} { 
			lset vmean_simulated $i [expr [lindex $vmean_simulated $i] / $nnodes.0]
			}
			
			lappend wind_velocity_per_element_V $vmean_simulated

		}
