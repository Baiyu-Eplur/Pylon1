wipe; 
set process_id [getPID]; 
set is_parallel 0; 
model basic -ndm 3 -ndf 6; 
timeSeries Linear 10000; 
set opensees_output_dir "."
node 1 0.000000 0.000000 0.000000; 
mass 1 2.638453 2.638453 2.638453 0 0 0; 
node 2 3.228000 0.000000 -0.415566; 
mass 2 5.276041 5.276041 5.276041 0 0 0; 
node 3 6.456000 0.000000 -0.822693; 
mass 3 5.274329 5.274329 5.274329 0 0 0; 
node 4 9.684000 0.000000 -1.221382; 
mass 4 5.272653 5.272653 5.272653 0 0 0; 
node 5 12.912000 0.000000 -1.611637; 
mass 5 5.271011 5.271011 5.271011 0 0 0; 
node 6 16.140000 0.000000 -1.993459; 
mass 6 5.269406 5.269406 5.269406 0 0 0; 
node 7 19.368000 0.000000 -2.366853; 
mass 7 5.267836 5.267836 5.267836 0 0 0; 
node 8 22.596000 0.000000 -2.731819; 
mass 8 5.266301 5.266301 5.266301 0 0 0; 
node 9 25.824000 0.000000 -3.088362; 
mass 9 5.264802 5.264802 5.264802 0 0 0; 
node 10 29.052000 0.000000 -3.436482; 
mass 10 5.263338 5.263338 5.263338 0 0 0; 
node 11 32.280000 0.000000 -3.776182; 
mass 11 5.261909 5.261909 5.261909 0 0 0; 
node 12 35.508000 0.000000 -4.107465; 
mass 12 5.260516 5.260516 5.260516 0 0 0; 
node 13 38.736000 0.000000 -4.430334; 
mass 13 5.259158 5.259158 5.259158 0 0 0; 
node 14 41.964000 0.000000 -4.744789; 
mass 14 5.257836 5.257836 5.257836 0 0 0; 
node 15 45.192000 0.000000 -5.050833; 
mass 15 5.256549 5.256549 5.256549 0 0 0; 
node 16 48.420000 0.000000 -5.348468; 
mass 16 5.255297 5.255297 5.255297 0 0 0; 
node 17 51.648000 0.000000 -5.637697; 
mass 17 5.254081 5.254081 5.254081 0 0 0; 
node 18 54.876000 0.000000 -5.918521; 
mass 18 5.252900 5.252900 5.252900 0 0 0; 
node 19 58.104000 0.000000 -6.190942; 
mass 19 5.251755 5.251755 5.251755 0 0 0; 
node 20 61.332000 0.000000 -6.454961; 
mass 20 5.250644 5.250644 5.250644 0 0 0; 
node 21 64.560000 0.000000 -6.710582; 
mass 21 5.249569 5.249569 5.249569 0 0 0; 
node 22 67.788000 0.000000 -6.957805; 
mass 22 5.248530 5.248530 5.248530 0 0 0; 
node 23 71.016000 0.000000 -7.196631; 
mass 23 5.247525 5.247525 5.247525 0 0 0; 
node 24 74.244000 0.000000 -7.427064; 
mass 24 5.246556 5.246556 5.246556 0 0 0; 
node 25 77.472000 0.000000 -7.649104; 
mass 25 5.245623 5.245623 5.245623 0 0 0; 
node 26 80.700000 0.000000 -7.862752; 
mass 26 5.244724 5.244724 5.244724 0 0 0; 
node 27 83.928000 0.000000 -8.068010; 
mass 27 5.243861 5.243861 5.243861 0 0 0; 
node 28 87.156000 0.000000 -8.264880; 
mass 28 5.243033 5.243033 5.243033 0 0 0; 
node 29 90.384000 0.000000 -8.453363; 
mass 29 5.242241 5.242241 5.242241 0 0 0; 
node 30 93.612000 0.000000 -8.633460; 
mass 30 5.241483 5.241483 5.241483 0 0 0; 
node 31 96.840000 0.000000 -8.805172; 
mass 31 5.240761 5.240761 5.240761 0 0 0; 
node 32 100.068000 0.000000 -8.968501; 
mass 32 5.240074 5.240074 5.240074 0 0 0; 
node 33 103.296000 0.000000 -9.123447; 
mass 33 5.239423 5.239423 5.239423 0 0 0; 
node 34 106.524000 0.000000 -9.270012; 
mass 34 5.238806 5.238806 5.238806 0 0 0; 
node 35 109.752000 0.000000 -9.408197; 
mass 35 5.238225 5.238225 5.238225 0 0 0; 
node 36 112.980000 0.000000 -9.538002; 
mass 36 5.237680 5.237680 5.237680 0 0 0; 
node 37 116.208000 0.000000 -9.659428; 
mass 37 5.237169 5.237169 5.237169 0 0 0; 
node 38 119.436000 0.000000 -9.772477; 
mass 38 5.236694 5.236694 5.236694 0 0 0; 
node 39 122.664000 0.000000 -9.877149; 
mass 39 5.236253 5.236253 5.236253 0 0 0; 
node 40 125.892000 0.000000 -9.973444; 
mass 40 5.235848 5.235848 5.235848 0 0 0; 
node 41 129.120000 0.000000 -10.061364; 
mass 41 5.235479 5.235479 5.235479 0 0 0; 
node 42 132.348000 0.000000 -10.140908; 
mass 42 5.235144 5.235144 5.235144 0 0 0; 
node 43 135.576000 0.000000 -10.212078; 
mass 43 5.234845 5.234845 5.234845 0 0 0; 
node 44 138.804000 0.000000 -10.274874; 
mass 44 5.234581 5.234581 5.234581 0 0 0; 
node 45 142.032000 0.000000 -10.329296; 
mass 45 5.234352 5.234352 5.234352 0 0 0; 
node 46 145.260000 0.000000 -10.375345; 
mass 46 5.234158 5.234158 5.234158 0 0 0; 
node 47 148.488000 0.000000 -10.413021; 
mass 47 5.234000 5.234000 5.234000 0 0 0; 
node 48 151.716000 0.000000 -10.442325; 
mass 48 5.233877 5.233877 5.233877 0 0 0; 
node 49 154.944000 0.000000 -10.463255; 
mass 49 5.233789 5.233789 5.233789 0 0 0; 
node 50 158.172000 0.000000 -10.475814; 
mass 50 5.233736 5.233736 5.233736 0 0 0; 
node 51 161.400000 0.000000 -10.480000; 
mass 51 5.233718 5.233718 5.233718 0 0 0; 
node 52 164.628000 0.000000 -10.475814; 
mass 52 5.233736 5.233736 5.233736 0 0 0; 
node 53 167.856000 0.000000 -10.463255; 
mass 53 5.233789 5.233789 5.233789 0 0 0; 
node 54 171.084000 0.000000 -10.442325; 
mass 54 5.233877 5.233877 5.233877 0 0 0; 
node 55 174.312000 0.000000 -10.413021; 
mass 55 5.234000 5.234000 5.234000 0 0 0; 
node 56 177.540000 0.000000 -10.375345; 
mass 56 5.234158 5.234158 5.234158 0 0 0; 
node 57 180.768000 0.000000 -10.329296; 
mass 57 5.234352 5.234352 5.234352 0 0 0; 
node 58 183.996000 0.000000 -10.274874; 
mass 58 5.234581 5.234581 5.234581 0 0 0; 
node 59 187.224000 0.000000 -10.212078; 
mass 59 5.234845 5.234845 5.234845 0 0 0; 
node 60 190.452000 0.000000 -10.140908; 
mass 60 5.235144 5.235144 5.235144 0 0 0; 
node 61 193.680000 0.000000 -10.061364; 
mass 61 5.235479 5.235479 5.235479 0 0 0; 
node 62 196.908000 0.000000 -9.973444; 
mass 62 5.235848 5.235848 5.235848 0 0 0; 
node 63 200.136000 0.000000 -9.877149; 
mass 63 5.236253 5.236253 5.236253 0 0 0; 
node 64 203.364000 0.000000 -9.772477; 
mass 64 5.236694 5.236694 5.236694 0 0 0; 
node 65 206.592000 0.000000 -9.659428; 
mass 65 5.237169 5.237169 5.237169 0 0 0; 
node 66 209.820000 0.000000 -9.538002; 
mass 66 5.237680 5.237680 5.237680 0 0 0; 
node 67 213.048000 0.000000 -9.408197; 
mass 67 5.238225 5.238225 5.238225 0 0 0; 
node 68 216.276000 0.000000 -9.270012; 
mass 68 5.238806 5.238806 5.238806 0 0 0; 
node 69 219.504000 0.000000 -9.123447; 
mass 69 5.239423 5.239423 5.239423 0 0 0; 
node 70 222.732000 0.000000 -8.968501; 
mass 70 5.240074 5.240074 5.240074 0 0 0; 
node 71 225.960000 0.000000 -8.805172; 
mass 71 5.240761 5.240761 5.240761 0 0 0; 
node 72 229.188000 0.000000 -8.633460; 
mass 72 5.241483 5.241483 5.241483 0 0 0; 
node 73 232.416000 0.000000 -8.453363; 
mass 73 5.242241 5.242241 5.242241 0 0 0; 
node 74 235.644000 0.000000 -8.264880; 
mass 74 5.243033 5.243033 5.243033 0 0 0; 
node 75 238.872000 0.000000 -8.068010; 
mass 75 5.243861 5.243861 5.243861 0 0 0; 
node 76 242.100000 0.000000 -7.862752; 
mass 76 5.244724 5.244724 5.244724 0 0 0; 
node 77 245.328000 0.000000 -7.649104; 
mass 77 5.245623 5.245623 5.245623 0 0 0; 
node 78 248.556000 0.000000 -7.427064; 
mass 78 5.246556 5.246556 5.246556 0 0 0; 
node 79 251.784000 0.000000 -7.196631; 
mass 79 5.247525 5.247525 5.247525 0 0 0; 
node 80 255.012000 0.000000 -6.957805; 
mass 80 5.248530 5.248530 5.248530 0 0 0; 
node 81 258.240000 0.000000 -6.710582; 
mass 81 5.249569 5.249569 5.249569 0 0 0; 
node 82 261.468000 0.000000 -6.454961; 
mass 82 5.250644 5.250644 5.250644 0 0 0; 
node 83 264.696000 0.000000 -6.190942; 
mass 83 5.251755 5.251755 5.251755 0 0 0; 
node 84 267.924000 0.000000 -5.918521; 
mass 84 5.252900 5.252900 5.252900 0 0 0; 
node 85 271.152000 0.000000 -5.637697; 
mass 85 5.254081 5.254081 5.254081 0 0 0; 
node 86 274.380000 0.000000 -5.348468; 
mass 86 5.255297 5.255297 5.255297 0 0 0; 
node 87 277.608000 0.000000 -5.050833; 
mass 87 5.256549 5.256549 5.256549 0 0 0; 
node 88 280.836000 0.000000 -4.744789; 
mass 88 5.257836 5.257836 5.257836 0 0 0; 
node 89 284.064000 0.000000 -4.430334; 
mass 89 5.259158 5.259158 5.259158 0 0 0; 
node 90 287.292000 0.000000 -4.107465; 
mass 90 5.260516 5.260516 5.260516 0 0 0; 
node 91 290.520000 0.000000 -3.776182; 
mass 91 5.261909 5.261909 5.261909 0 0 0; 
node 92 293.748000 0.000000 -3.436482; 
mass 92 5.263338 5.263338 5.263338 0 0 0; 
node 93 296.976000 0.000000 -3.088362; 
mass 93 5.264802 5.264802 5.264802 0 0 0; 
node 94 300.204000 0.000000 -2.731819; 
mass 94 5.266301 5.266301 5.266301 0 0 0; 
node 95 303.432000 0.000000 -2.366853; 
mass 95 5.267836 5.267836 5.267836 0 0 0; 
node 96 306.660000 0.000000 -1.993459; 
mass 96 5.269406 5.269406 5.269406 0 0 0; 
node 97 309.888000 0.000000 -1.611637; 
mass 97 5.271011 5.271011 5.271011 0 0 0; 
node 98 313.116000 0.000000 -1.221382; 
mass 98 5.272653 5.272653 5.272653 0 0 0; 
node 99 316.344000 0.000000 -0.822693; 
mass 99 5.274329 5.274329 5.274329 0 0 0; 
node 100 319.572000 0.000000 -0.415566; 
mass 100 5.276041 5.276041 5.276041 0 0 0; 
node 101 322.800000 0.000000 0.000000; 
mass 101 2.638453 2.638453 2.638453 0 0 0; 
uniaxialMaterial ElasticPPGap 1 69000000000.000000 205029170.824339 0.0;
uniaxialMaterial InitStrainMaterial 10 1 4.457156e-04;
element corotTruss 1 1 2 0.000643323091391 10; 
element corotTruss 2 2 3 0.000643323091391 10; 
element corotTruss 3 3 4 0.000643323091391 10; 
element corotTruss 4 4 5 0.000643323091391 10; 
element corotTruss 5 5 6 0.000643323091391 10; 
element corotTruss 6 6 7 0.000643323091391 10; 
element corotTruss 7 7 8 0.000643323091391 10; 
element corotTruss 8 8 9 0.000643323091391 10; 
element corotTruss 9 9 10 0.000643323091391 10; 
element corotTruss 10 10 11 0.000643323091391 10; 
element corotTruss 11 11 12 0.000643323091391 10; 
element corotTruss 12 12 13 0.000643323091391 10; 
element corotTruss 13 13 14 0.000643323091391 10; 
element corotTruss 14 14 15 0.000643323091391 10; 
element corotTruss 15 15 16 0.000643323091391 10; 
element corotTruss 16 16 17 0.000643323091391 10; 
element corotTruss 17 17 18 0.000643323091391 10; 
element corotTruss 18 18 19 0.000643323091391 10; 
element corotTruss 19 19 20 0.000643323091391 10; 
element corotTruss 20 20 21 0.000643323091391 10; 
element corotTruss 21 21 22 0.000643323091391 10; 
element corotTruss 22 22 23 0.000643323091391 10; 
element corotTruss 23 23 24 0.000643323091391 10; 
element corotTruss 24 24 25 0.000643323091391 10; 
element corotTruss 25 25 26 0.000643323091391 10; 
element corotTruss 26 26 27 0.000643323091391 10; 
element corotTruss 27 27 28 0.000643323091391 10; 
element corotTruss 28 28 29 0.000643323091391 10; 
element corotTruss 29 29 30 0.000643323091391 10; 
element corotTruss 30 30 31 0.000643323091391 10; 
element corotTruss 31 31 32 0.000643323091391 10; 
element corotTruss 32 32 33 0.000643323091391 10; 
element corotTruss 33 33 34 0.000643323091391 10; 
element corotTruss 34 34 35 0.000643323091391 10; 
element corotTruss 35 35 36 0.000643323091391 10; 
element corotTruss 36 36 37 0.000643323091391 10; 
element corotTruss 37 37 38 0.000643323091391 10; 
element corotTruss 38 38 39 0.000643323091391 10; 
element corotTruss 39 39 40 0.000643323091391 10; 
element corotTruss 40 40 41 0.000643323091391 10; 
element corotTruss 41 41 42 0.000643323091391 10; 
element corotTruss 42 42 43 0.000643323091391 10; 
element corotTruss 43 43 44 0.000643323091391 10; 
element corotTruss 44 44 45 0.000643323091391 10; 
element corotTruss 45 45 46 0.000643323091391 10; 
element corotTruss 46 46 47 0.000643323091391 10; 
element corotTruss 47 47 48 0.000643323091391 10; 
element corotTruss 48 48 49 0.000643323091391 10; 
element corotTruss 49 49 50 0.000643323091391 10; 
element corotTruss 50 50 51 0.000643323091391 10; 
element corotTruss 51 51 52 0.000643323091391 10; 
element corotTruss 52 52 53 0.000643323091391 10; 
element corotTruss 53 53 54 0.000643323091391 10; 
element corotTruss 54 54 55 0.000643323091391 10; 
element corotTruss 55 55 56 0.000643323091391 10; 
element corotTruss 56 56 57 0.000643323091391 10; 
element corotTruss 57 57 58 0.000643323091391 10; 
element corotTruss 58 58 59 0.000643323091391 10; 
element corotTruss 59 59 60 0.000643323091391 10; 
element corotTruss 60 60 61 0.000643323091391 10; 
element corotTruss 61 61 62 0.000643323091391 10; 
element corotTruss 62 62 63 0.000643323091391 10; 
element corotTruss 63 63 64 0.000643323091391 10; 
element corotTruss 64 64 65 0.000643323091391 10; 
element corotTruss 65 65 66 0.000643323091391 10; 
element corotTruss 66 66 67 0.000643323091391 10; 
element corotTruss 67 67 68 0.000643323091391 10; 
element corotTruss 68 68 69 0.000643323091391 10; 
element corotTruss 69 69 70 0.000643323091391 10; 
element corotTruss 70 70 71 0.000643323091391 10; 
element corotTruss 71 71 72 0.000643323091391 10; 
element corotTruss 72 72 73 0.000643323091391 10; 
element corotTruss 73 73 74 0.000643323091391 10; 
element corotTruss 74 74 75 0.000643323091391 10; 
element corotTruss 75 75 76 0.000643323091391 10; 
element corotTruss 76 76 77 0.000643323091391 10; 
element corotTruss 77 77 78 0.000643323091391 10; 
element corotTruss 78 78 79 0.000643323091391 10; 
element corotTruss 79 79 80 0.000643323091391 10; 
element corotTruss 80 80 81 0.000643323091391 10; 
element corotTruss 81 81 82 0.000643323091391 10; 
element corotTruss 82 82 83 0.000643323091391 10; 
element corotTruss 83 83 84 0.000643323091391 10; 
element corotTruss 84 84 85 0.000643323091391 10; 
element corotTruss 85 85 86 0.000643323091391 10; 
element corotTruss 86 86 87 0.000643323091391 10; 
element corotTruss 87 87 88 0.000643323091391 10; 
element corotTruss 88 88 89 0.000643323091391 10; 
element corotTruss 89 89 90 0.000643323091391 10; 
element corotTruss 90 90 91 0.000643323091391 10; 
element corotTruss 91 91 92 0.000643323091391 10; 
element corotTruss 92 92 93 0.000643323091391 10; 
element corotTruss 93 93 94 0.000643323091391 10; 
element corotTruss 94 94 95 0.000643323091391 10; 
element corotTruss 95 95 96 0.000643323091391 10; 
element corotTruss 96 96 97 0.000643323091391 10; 
element corotTruss 97 97 98 0.000643323091391 10; 
element corotTruss 98 98 99 0.000643323091391 10; 
element corotTruss 99 99 100 0.000643323091391 10; 
element corotTruss 100 100 101 0.000643323091391 10; 
# a list of all monitor and custom function actors to be called by the MonitorFunction; 
set all_custom_functions {}; 
set all_monitor_actors {}; 
# the main custom function caller that will call all actors in $all_monitor_actors and in $all_custom_functions list; 
proc CustomFunctionCaller {step_id dt T n_iter norm perc process_id is_parallel} {; 
	global all_monitor_actors; 
	global all_custom_functions; 
	# Call monitors: we pass the parameters needed; 
	foreach p $all_monitor_actors {; 
		$p $step_id $dt $T $n_iter $norm $perc $process_id $is_parallel; 
	}; 
	# Call all other custom functions; 
	foreach p $all_custom_functions {; 
		$p; 
	}; 
}; 
fix 1 1 1 1 1 1 1; 
fix 2 0 0 0 1 1 1; 
fix 3 0 0 0 1 1 1; 
fix 4 0 0 0 1 1 1; 
fix 5 0 0 0 1 1 1; 
fix 6 0 0 0 1 1 1; 
fix 7 0 0 0 1 1 1; 
fix 8 0 0 0 1 1 1; 
fix 9 0 0 0 1 1 1; 
fix 10 0 0 0 1 1 1; 
fix 11 0 0 0 1 1 1; 
fix 12 0 0 0 1 1 1; 
fix 13 0 0 0 1 1 1; 
fix 14 0 0 0 1 1 1; 
fix 15 0 0 0 1 1 1; 
fix 16 0 0 0 1 1 1; 
fix 17 0 0 0 1 1 1; 
fix 18 0 0 0 1 1 1; 
fix 19 0 0 0 1 1 1; 
fix 20 0 0 0 1 1 1; 
fix 21 0 0 0 1 1 1; 
fix 22 0 0 0 1 1 1; 
fix 23 0 0 0 1 1 1; 
fix 24 0 0 0 1 1 1; 
fix 25 0 0 0 1 1 1; 
fix 26 0 0 0 1 1 1; 
fix 27 0 0 0 1 1 1; 
fix 28 0 0 0 1 1 1; 
fix 29 0 0 0 1 1 1; 
fix 30 0 0 0 1 1 1; 
fix 31 0 0 0 1 1 1; 
fix 32 0 0 0 1 1 1; 
fix 33 0 0 0 1 1 1; 
fix 34 0 0 0 1 1 1; 
fix 35 0 0 0 1 1 1; 
fix 36 0 0 0 1 1 1; 
fix 37 0 0 0 1 1 1; 
fix 38 0 0 0 1 1 1; 
fix 39 0 0 0 1 1 1; 
fix 40 0 0 0 1 1 1; 
fix 41 0 0 0 1 1 1; 
fix 42 0 0 0 1 1 1; 
fix 43 0 0 0 1 1 1; 
fix 44 0 0 0 1 1 1; 
fix 45 0 0 0 1 1 1; 
fix 46 0 0 0 1 1 1; 
fix 47 0 0 0 1 1 1; 
fix 48 0 0 0 1 1 1; 
fix 49 0 0 0 1 1 1; 
fix 50 0 0 0 1 1 1; 
fix 51 0 0 0 1 1 1; 
fix 52 0 0 0 1 1 1; 
fix 53 0 0 0 1 1 1; 
fix 54 0 0 0 1 1 1; 
fix 55 0 0 0 1 1 1; 
fix 56 0 0 0 1 1 1; 
fix 57 0 0 0 1 1 1; 
fix 58 0 0 0 1 1 1; 
fix 59 0 0 0 1 1 1; 
fix 60 0 0 0 1 1 1; 
fix 61 0 0 0 1 1 1; 
fix 62 0 0 0 1 1 1; 
fix 63 0 0 0 1 1 1; 
fix 64 0 0 0 1 1 1; 
fix 65 0 0 0 1 1 1; 
fix 66 0 0 0 1 1 1; 
fix 67 0 0 0 1 1 1; 
fix 68 0 0 0 1 1 1; 
fix 69 0 0 0 1 1 1; 
fix 70 0 0 0 1 1 1; 
fix 71 0 0 0 1 1 1; 
fix 72 0 0 0 1 1 1; 
fix 73 0 0 0 1 1 1; 
fix 74 0 0 0 1 1 1; 
fix 75 0 0 0 1 1 1; 
fix 76 0 0 0 1 1 1; 
fix 77 0 0 0 1 1 1; 
fix 78 0 0 0 1 1 1; 
fix 79 0 0 0 1 1 1; 
fix 80 0 0 0 1 1 1; 
fix 81 0 0 0 1 1 1; 
fix 82 0 0 0 1 1 1; 
fix 83 0 0 0 1 1 1; 
fix 84 0 0 0 1 1 1; 
fix 85 0 0 0 1 1 1; 
fix 86 0 0 0 1 1 1; 
fix 87 0 0 0 1 1 1; 
fix 88 0 0 0 1 1 1; 
fix 89 0 0 0 1 1 1; 
fix 90 0 0 0 1 1 1; 
fix 91 0 0 0 1 1 1; 
fix 92 0 0 0 1 1 1; 
fix 93 0 0 0 1 1 1; 
fix 94 0 0 0 1 1 1; 
fix 95 0 0 0 1 1 1; 
fix 96 0 0 0 1 1 1; 
fix 97 0 0 0 1 1 1; 
fix 98 0 0 0 1 1 1; 
fix 99 0 0 0 1 1 1; 
fix 100 0 0 0 1 1 1; 
fix 101 1 1 1 1 1 1; 
pattern Plain 200000 10000 { 
load 1 0 0 -25.874385 0 0 0; 
load 2 0 0 -51.740289 0 0 0; 
load 3 0 0 -51.723500 0 0 0; 
load 4 0 0 -51.707058 0 0 0; 
load 5 0 0 -51.690965 0 0 0; 
load 6 0 0 -51.675219 0 0 0; 
load 7 0 0 -51.659820 0 0 0; 
load 8 0 0 -51.644769 0 0 0; 
load 9 0 0 -51.630066 0 0 0; 
load 10 0 0 -51.615710 0 0 0; 
load 11 0 0 -51.601701 0 0 0; 
load 12 0 0 -51.588039 0 0 0; 
load 13 0 0 -51.574725 0 0 0; 
load 14 0 0 -51.561757 0 0 0; 
load 15 0 0 -51.549136 0 0 0; 
load 16 0 0 -51.536862 0 0 0; 
load 17 0 0 -51.524934 0 0 0; 
load 18 0 0 -51.513353 0 0 0; 
load 19 0 0 -51.502119 0 0 0; 
load 20 0 0 -51.491231 0 0 0; 
load 21 0 0 -51.480690 0 0 0; 
load 22 0 0 -51.470495 0 0 0; 
load 23 0 0 -51.460646 0 0 0; 
load 24 0 0 -51.451143 0 0 0; 
load 25 0 0 -51.441986 0 0 0; 
load 26 0 0 -51.433176 0 0 0; 
load 27 0 0 -51.424711 0 0 0; 
load 28 0 0 -51.416592 0 0 0; 
load 29 0 0 -51.408819 0 0 0; 
load 30 0 0 -51.401392 0 0 0; 
load 31 0 0 -51.394311 0 0 0; 
load 32 0 0 -51.387576 0 0 0; 
load 33 0 0 -51.381186 0 0 0; 
load 34 0 0 -51.375142 0 0 0; 
load 35 0 0 -51.369443 0 0 0; 
load 36 0 0 -51.364090 0 0 0; 
load 37 0 0 -51.359083 0 0 0; 
load 38 0 0 -51.354421 0 0 0; 
load 39 0 0 -51.350104 0 0 0; 
load 40 0 0 -51.346133 0 0 0; 
load 41 0 0 -51.342507 0 0 0; 
load 42 0 0 -51.339227 0 0 0; 
load 43 0 0 -51.336292 0 0 0; 
load 44 0 0 -51.333702 0 0 0; 
load 45 0 0 -51.331458 0 0 0; 
load 46 0 0 -51.329559 0 0 0; 
load 47 0 0 -51.328005 0 0 0; 
load 48 0 0 -51.326797 0 0 0; 
load 49 0 0 -51.325934 0 0 0; 
load 50 0 0 -51.325416 0 0 0; 
load 51 0 0 -51.325243 0 0 0; 
load 52 0 0 -51.325416 0 0 0; 
load 53 0 0 -51.325934 0 0 0; 
load 54 0 0 -51.326797 0 0 0; 
load 55 0 0 -51.328005 0 0 0; 
load 56 0 0 -51.329559 0 0 0; 
load 57 0 0 -51.331458 0 0 0; 
load 58 0 0 -51.333702 0 0 0; 
load 59 0 0 -51.336292 0 0 0; 
load 60 0 0 -51.339227 0 0 0; 
load 61 0 0 -51.342507 0 0 0; 
load 62 0 0 -51.346133 0 0 0; 
load 63 0 0 -51.350104 0 0 0; 
load 64 0 0 -51.354421 0 0 0; 
load 65 0 0 -51.359083 0 0 0; 
load 66 0 0 -51.364090 0 0 0; 
load 67 0 0 -51.369443 0 0 0; 
load 68 0 0 -51.375142 0 0 0; 
load 69 0 0 -51.381186 0 0 0; 
load 70 0 0 -51.387576 0 0 0; 
load 71 0 0 -51.394311 0 0 0; 
load 72 0 0 -51.401392 0 0 0; 
load 73 0 0 -51.408819 0 0 0; 
load 74 0 0 -51.416592 0 0 0; 
load 75 0 0 -51.424711 0 0 0; 
load 76 0 0 -51.433176 0 0 0; 
load 77 0 0 -51.441986 0 0 0; 
load 78 0 0 -51.451143 0 0 0; 
load 79 0 0 -51.460646 0 0 0; 
load 80 0 0 -51.470495 0 0 0; 
load 81 0 0 -51.480690 0 0 0; 
load 82 0 0 -51.491231 0 0 0; 
load 83 0 0 -51.502119 0 0 0; 
load 84 0 0 -51.513353 0 0 0; 
load 85 0 0 -51.524934 0 0 0; 
load 86 0 0 -51.536862 0 0 0; 
load 87 0 0 -51.549136 0 0 0; 
load 88 0 0 -51.561757 0 0 0; 
load 89 0 0 -51.574725 0 0 0; 
load 90 0 0 -51.588039 0 0 0; 
load 91 0 0 -51.601701 0 0 0; 
load 92 0 0 -51.615710 0 0 0; 
load 93 0 0 -51.630066 0 0 0; 
load 94 0 0 -51.644769 0 0 0; 
load 95 0 0 -51.659820 0 0 0; 
load 96 0 0 -51.675219 0 0 0; 
load 97 0 0 -51.690965 0 0 0; 
load 98 0 0 -51.707058 0 0 0; 
load 99 0 0 -51.723500 0 0 0; 
load 100 0 0 -51.740289 0 0 0; 
load 101 0 0 -25.874385 0 0 0; 
}; 
set wind_data_dir "data/wind/SIM1"
set wind_time_file "data/aero_coeffs/time.txt"
source tcl_procedures/Wind_velocity_reader.tcl
constraints Transformation
numberer Plain
system FullGeneral
test NormDispIncr 1.00e-03 200
algorithm KrylovNewton
integrator LoadControl 0.0
analysis Static
recorder Element -file Element1.out -time -ele 1 force; 
recorder Node -file Static.out -nodeRange 1 101 -dof 3 disp; 
set total_time 1.0
set initial_num_incr 20
set time 0.0
set time_increment [expr $total_time / $initial_num_incr]
integrator LoadControl $time_increment 
for {set increment_counter 1} {$increment_counter <= $initial_num_incr} {incr increment_counter} { 
	if {$process_id == 0} { 
		puts "Increment: $increment_counter. time_increment = $time_increment. Current time = $time" 
	} 
	set ok [analyze 1 ] 
	#barrier 
	if {$ok == 0} { 
		set num_iter [testIter] 
		set time [expr $time + $time_increment] 
		# print statistics 
		set norms [testNorms] 
		if {$num_iter > 0} {set last_norm [lindex $norms [expr $num_iter-1]]} else {set last_norm 0.0} 
		if {$process_id == 0} { 
		} 
		# Call Custom Functions 
		set perc [expr $time/$total_time] 
		CustomFunctionCaller $increment_counter $time_increment $time $num_iter $last_norm $perc $process_id $is_parallel 
	} else { 
		error "ERROR: the analysis did not converge" 
	} 
} 
if {$process_id == 0} { 
	puts "Target time has been reached. Current time = $time" 
	puts "SUCCESS." 
} 
loadConst -time 0.0
set force_data_dir "data/forces/FORCE_3/SIM1"
timeSeries Path 1 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_1_H_drag.txt -factor 1
pattern Plain 101 1 {
load 1 0 1000 0 0 0 0
} 
timeSeries Path 2 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_2_H_drag.txt -factor 1
pattern Plain 102 2 {
load 2 0 1000 0 0 0 0
} 
timeSeries Path 3 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_3_H_drag.txt -factor 1
pattern Plain 103 3 {
load 3 0 1000 0 0 0 0
} 
timeSeries Path 4 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_4_H_drag.txt -factor 1
pattern Plain 104 4 {
load 4 0 1000 0 0 0 0
} 
timeSeries Path 5 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_5_H_drag.txt -factor 1
pattern Plain 105 5 {
load 5 0 1000 0 0 0 0
} 
timeSeries Path 6 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_6_H_drag.txt -factor 1
pattern Plain 106 6 {
load 6 0 1000 0 0 0 0
} 
timeSeries Path 7 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_7_H_drag.txt -factor 1
pattern Plain 107 7 {
load 7 0 1000 0 0 0 0
} 
timeSeries Path 8 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_8_H_drag.txt -factor 1
pattern Plain 108 8 {
load 8 0 1000 0 0 0 0
} 
timeSeries Path 9 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_9_H_drag.txt -factor 1
pattern Plain 109 9 {
load 9 0 1000 0 0 0 0
} 
timeSeries Path 10 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_10_H_drag.txt -factor 1
pattern Plain 110 10 {
load 10 0 1000 0 0 0 0
} 
timeSeries Path 11 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_11_H_drag.txt -factor 1
pattern Plain 111 11 {
load 11 0 1000 0 0 0 0
} 
timeSeries Path 12 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_12_H_drag.txt -factor 1
pattern Plain 112 12 {
load 12 0 1000 0 0 0 0
} 
timeSeries Path 13 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_13_H_drag.txt -factor 1
pattern Plain 113 13 {
load 13 0 1000 0 0 0 0
} 
timeSeries Path 14 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_14_H_drag.txt -factor 1
pattern Plain 114 14 {
load 14 0 1000 0 0 0 0
} 
timeSeries Path 15 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_15_H_drag.txt -factor 1
pattern Plain 115 15 {
load 15 0 1000 0 0 0 0
} 
timeSeries Path 16 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_16_H_drag.txt -factor 1
pattern Plain 116 16 {
load 16 0 1000 0 0 0 0
} 
timeSeries Path 17 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_17_H_drag.txt -factor 1
pattern Plain 117 17 {
load 17 0 1000 0 0 0 0
} 
timeSeries Path 18 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_18_H_drag.txt -factor 1
pattern Plain 118 18 {
load 18 0 1000 0 0 0 0
} 
timeSeries Path 19 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_19_H_drag.txt -factor 1
pattern Plain 119 19 {
load 19 0 1000 0 0 0 0
} 
timeSeries Path 20 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_20_H_drag.txt -factor 1
pattern Plain 120 20 {
load 20 0 1000 0 0 0 0
} 
timeSeries Path 21 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_21_H_drag.txt -factor 1
pattern Plain 121 21 {
load 21 0 1000 0 0 0 0
} 
timeSeries Path 22 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_22_H_drag.txt -factor 1
pattern Plain 122 22 {
load 22 0 1000 0 0 0 0
} 
timeSeries Path 23 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_23_H_drag.txt -factor 1
pattern Plain 123 23 {
load 23 0 1000 0 0 0 0
} 
timeSeries Path 24 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_24_H_drag.txt -factor 1
pattern Plain 124 24 {
load 24 0 1000 0 0 0 0
} 
timeSeries Path 25 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_25_H_drag.txt -factor 1
pattern Plain 125 25 {
load 25 0 1000 0 0 0 0
} 
timeSeries Path 26 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_26_H_drag.txt -factor 1
pattern Plain 126 26 {
load 26 0 1000 0 0 0 0
} 
timeSeries Path 27 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_27_H_drag.txt -factor 1
pattern Plain 127 27 {
load 27 0 1000 0 0 0 0
} 
timeSeries Path 28 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_28_H_drag.txt -factor 1
pattern Plain 128 28 {
load 28 0 1000 0 0 0 0
} 
timeSeries Path 29 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_29_H_drag.txt -factor 1
pattern Plain 129 29 {
load 29 0 1000 0 0 0 0
} 
timeSeries Path 30 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_30_H_drag.txt -factor 1
pattern Plain 130 30 {
load 30 0 1000 0 0 0 0
} 
timeSeries Path 31 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_31_H_drag.txt -factor 1
pattern Plain 131 31 {
load 31 0 1000 0 0 0 0
} 
timeSeries Path 32 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_32_H_drag.txt -factor 1
pattern Plain 132 32 {
load 32 0 1000 0 0 0 0
} 
timeSeries Path 33 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_33_H_drag.txt -factor 1
pattern Plain 133 33 {
load 33 0 1000 0 0 0 0
} 
timeSeries Path 34 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_34_H_drag.txt -factor 1
pattern Plain 134 34 {
load 34 0 1000 0 0 0 0
} 
timeSeries Path 35 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_35_H_drag.txt -factor 1
pattern Plain 135 35 {
load 35 0 1000 0 0 0 0
} 
timeSeries Path 36 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_36_H_drag.txt -factor 1
pattern Plain 136 36 {
load 36 0 1000 0 0 0 0
} 
timeSeries Path 37 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_37_H_drag.txt -factor 1
pattern Plain 137 37 {
load 37 0 1000 0 0 0 0
} 
timeSeries Path 38 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_38_H_drag.txt -factor 1
pattern Plain 138 38 {
load 38 0 1000 0 0 0 0
} 
timeSeries Path 39 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_39_H_drag.txt -factor 1
pattern Plain 139 39 {
load 39 0 1000 0 0 0 0
} 
timeSeries Path 40 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_40_H_drag.txt -factor 1
pattern Plain 140 40 {
load 40 0 1000 0 0 0 0
} 
timeSeries Path 41 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_41_H_drag.txt -factor 1
pattern Plain 141 41 {
load 41 0 1000 0 0 0 0
} 
timeSeries Path 42 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_42_H_drag.txt -factor 1
pattern Plain 142 42 {
load 42 0 1000 0 0 0 0
} 
timeSeries Path 43 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_43_H_drag.txt -factor 1
pattern Plain 143 43 {
load 43 0 1000 0 0 0 0
} 
timeSeries Path 44 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_44_H_drag.txt -factor 1
pattern Plain 144 44 {
load 44 0 1000 0 0 0 0
} 
timeSeries Path 45 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_45_H_drag.txt -factor 1
pattern Plain 145 45 {
load 45 0 1000 0 0 0 0
} 
timeSeries Path 46 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_46_H_drag.txt -factor 1
pattern Plain 146 46 {
load 46 0 1000 0 0 0 0
} 
timeSeries Path 47 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_47_H_drag.txt -factor 1
pattern Plain 147 47 {
load 47 0 1000 0 0 0 0
} 
timeSeries Path 48 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_48_H_drag.txt -factor 1
pattern Plain 148 48 {
load 48 0 1000 0 0 0 0
} 
timeSeries Path 49 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_49_H_drag.txt -factor 1
pattern Plain 149 49 {
load 49 0 1000 0 0 0 0
} 
timeSeries Path 50 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_50_H_drag.txt -factor 1
pattern Plain 150 50 {
load 50 0 1000 0 0 0 0
} 
timeSeries Path 51 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_51_H_drag.txt -factor 1
pattern Plain 151 51 {
load 51 0 1000 0 0 0 0
} 
timeSeries Path 52 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_52_H_drag.txt -factor 1
pattern Plain 152 52 {
load 52 0 1000 0 0 0 0
} 
timeSeries Path 53 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_53_H_drag.txt -factor 1
pattern Plain 153 53 {
load 53 0 1000 0 0 0 0
} 
timeSeries Path 54 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_54_H_drag.txt -factor 1
pattern Plain 154 54 {
load 54 0 1000 0 0 0 0
} 
timeSeries Path 55 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_55_H_drag.txt -factor 1
pattern Plain 155 55 {
load 55 0 1000 0 0 0 0
} 
timeSeries Path 56 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_56_H_drag.txt -factor 1
pattern Plain 156 56 {
load 56 0 1000 0 0 0 0
} 
timeSeries Path 57 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_57_H_drag.txt -factor 1
pattern Plain 157 57 {
load 57 0 1000 0 0 0 0
} 
timeSeries Path 58 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_58_H_drag.txt -factor 1
pattern Plain 158 58 {
load 58 0 1000 0 0 0 0
} 
timeSeries Path 59 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_59_H_drag.txt -factor 1
pattern Plain 159 59 {
load 59 0 1000 0 0 0 0
} 
timeSeries Path 60 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_60_H_drag.txt -factor 1
pattern Plain 160 60 {
load 60 0 1000 0 0 0 0
} 
timeSeries Path 61 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_61_H_drag.txt -factor 1
pattern Plain 161 61 {
load 61 0 1000 0 0 0 0
} 
timeSeries Path 62 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_62_H_drag.txt -factor 1
pattern Plain 162 62 {
load 62 0 1000 0 0 0 0
} 
timeSeries Path 63 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_63_H_drag.txt -factor 1
pattern Plain 163 63 {
load 63 0 1000 0 0 0 0
} 
timeSeries Path 64 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_64_H_drag.txt -factor 1
pattern Plain 164 64 {
load 64 0 1000 0 0 0 0
} 
timeSeries Path 65 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_65_H_drag.txt -factor 1
pattern Plain 165 65 {
load 65 0 1000 0 0 0 0
} 
timeSeries Path 66 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_66_H_drag.txt -factor 1
pattern Plain 166 66 {
load 66 0 1000 0 0 0 0
} 
timeSeries Path 67 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_67_H_drag.txt -factor 1
pattern Plain 167 67 {
load 67 0 1000 0 0 0 0
} 
timeSeries Path 68 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_68_H_drag.txt -factor 1
pattern Plain 168 68 {
load 68 0 1000 0 0 0 0
} 
timeSeries Path 69 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_69_H_drag.txt -factor 1
pattern Plain 169 69 {
load 69 0 1000 0 0 0 0
} 
timeSeries Path 70 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_70_H_drag.txt -factor 1
pattern Plain 170 70 {
load 70 0 1000 0 0 0 0
} 
timeSeries Path 71 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_71_H_drag.txt -factor 1
pattern Plain 171 71 {
load 71 0 1000 0 0 0 0
} 
timeSeries Path 72 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_72_H_drag.txt -factor 1
pattern Plain 172 72 {
load 72 0 1000 0 0 0 0
} 
timeSeries Path 73 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_73_H_drag.txt -factor 1
pattern Plain 173 73 {
load 73 0 1000 0 0 0 0
} 
timeSeries Path 74 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_74_H_drag.txt -factor 1
pattern Plain 174 74 {
load 74 0 1000 0 0 0 0
} 
timeSeries Path 75 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_75_H_drag.txt -factor 1
pattern Plain 175 75 {
load 75 0 1000 0 0 0 0
} 
timeSeries Path 76 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_76_H_drag.txt -factor 1
pattern Plain 176 76 {
load 76 0 1000 0 0 0 0
} 
timeSeries Path 77 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_77_H_drag.txt -factor 1
pattern Plain 177 77 {
load 77 0 1000 0 0 0 0
} 
timeSeries Path 78 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_78_H_drag.txt -factor 1
pattern Plain 178 78 {
load 78 0 1000 0 0 0 0
} 
timeSeries Path 79 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_79_H_drag.txt -factor 1
pattern Plain 179 79 {
load 79 0 1000 0 0 0 0
} 
timeSeries Path 80 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_80_H_drag.txt -factor 1
pattern Plain 180 80 {
load 80 0 1000 0 0 0 0
} 
timeSeries Path 81 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_81_H_drag.txt -factor 1
pattern Plain 181 81 {
load 81 0 1000 0 0 0 0
} 
timeSeries Path 82 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_82_H_drag.txt -factor 1
pattern Plain 182 82 {
load 82 0 1000 0 0 0 0
} 
timeSeries Path 83 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_83_H_drag.txt -factor 1
pattern Plain 183 83 {
load 83 0 1000 0 0 0 0
} 
timeSeries Path 84 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_84_H_drag.txt -factor 1
pattern Plain 184 84 {
load 84 0 1000 0 0 0 0
} 
timeSeries Path 85 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_85_H_drag.txt -factor 1
pattern Plain 185 85 {
load 85 0 1000 0 0 0 0
} 
timeSeries Path 86 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_86_H_drag.txt -factor 1
pattern Plain 186 86 {
load 86 0 1000 0 0 0 0
} 
timeSeries Path 87 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_87_H_drag.txt -factor 1
pattern Plain 187 87 {
load 87 0 1000 0 0 0 0
} 
timeSeries Path 88 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_88_H_drag.txt -factor 1
pattern Plain 188 88 {
load 88 0 1000 0 0 0 0
} 
timeSeries Path 89 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_89_H_drag.txt -factor 1
pattern Plain 189 89 {
load 89 0 1000 0 0 0 0
} 
timeSeries Path 90 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_90_H_drag.txt -factor 1
pattern Plain 190 90 {
load 90 0 1000 0 0 0 0
} 
timeSeries Path 91 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_91_H_drag.txt -factor 1
pattern Plain 191 91 {
load 91 0 1000 0 0 0 0
} 
timeSeries Path 92 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_92_H_drag.txt -factor 1
pattern Plain 192 92 {
load 92 0 1000 0 0 0 0
} 
timeSeries Path 93 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_93_H_drag.txt -factor 1
pattern Plain 193 93 {
load 93 0 1000 0 0 0 0
} 
timeSeries Path 94 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_94_H_drag.txt -factor 1
pattern Plain 194 94 {
load 94 0 1000 0 0 0 0
} 
timeSeries Path 95 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_95_H_drag.txt -factor 1
pattern Plain 195 95 {
load 95 0 1000 0 0 0 0
} 
timeSeries Path 96 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_96_H_drag.txt -factor 1
pattern Plain 196 96 {
load 96 0 1000 0 0 0 0
} 
timeSeries Path 97 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_97_H_drag.txt -factor 1
pattern Plain 197 97 {
load 97 0 1000 0 0 0 0
} 
timeSeries Path 98 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_98_H_drag.txt -factor 1
pattern Plain 198 98 {
load 98 0 1000 0 0 0 0
} 
timeSeries Path 99 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_99_H_drag.txt -factor 1
pattern Plain 199 99 {
load 99 0 1000 0 0 0 0
} 
timeSeries Path 100 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_100_H_drag.txt -factor 1
pattern Plain 200 100 {
load 100 0 1000 0 0 0 0
} 
timeSeries Path 101 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_101_H_drag.txt -factor 1
pattern Plain 201 101 {
load 101 0 1000 0 0 0 0
} 
timeSeries Path 102 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_1_H_lift.txt -factor 1
pattern Plain 202 102 {
load 1 0 0 1000 0 0 0
} 
timeSeries Path 103 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_2_H_lift.txt -factor 1
pattern Plain 203 103 {
load 2 0 0 1000 0 0 0
} 
timeSeries Path 104 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_3_H_lift.txt -factor 1
pattern Plain 204 104 {
load 3 0 0 1000 0 0 0
} 
timeSeries Path 105 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_4_H_lift.txt -factor 1
pattern Plain 205 105 {
load 4 0 0 1000 0 0 0
} 
timeSeries Path 106 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_5_H_lift.txt -factor 1
pattern Plain 206 106 {
load 5 0 0 1000 0 0 0
} 
timeSeries Path 107 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_6_H_lift.txt -factor 1
pattern Plain 207 107 {
load 6 0 0 1000 0 0 0
} 
timeSeries Path 108 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_7_H_lift.txt -factor 1
pattern Plain 208 108 {
load 7 0 0 1000 0 0 0
} 
timeSeries Path 109 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_8_H_lift.txt -factor 1
pattern Plain 209 109 {
load 8 0 0 1000 0 0 0
} 
timeSeries Path 110 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_9_H_lift.txt -factor 1
pattern Plain 210 110 {
load 9 0 0 1000 0 0 0
} 
timeSeries Path 111 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_10_H_lift.txt -factor 1
pattern Plain 211 111 {
load 10 0 0 1000 0 0 0
} 
timeSeries Path 112 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_11_H_lift.txt -factor 1
pattern Plain 212 112 {
load 11 0 0 1000 0 0 0
} 
timeSeries Path 113 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_12_H_lift.txt -factor 1
pattern Plain 213 113 {
load 12 0 0 1000 0 0 0
} 
timeSeries Path 114 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_13_H_lift.txt -factor 1
pattern Plain 214 114 {
load 13 0 0 1000 0 0 0
} 
timeSeries Path 115 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_14_H_lift.txt -factor 1
pattern Plain 215 115 {
load 14 0 0 1000 0 0 0
} 
timeSeries Path 116 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_15_H_lift.txt -factor 1
pattern Plain 216 116 {
load 15 0 0 1000 0 0 0
} 
timeSeries Path 117 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_16_H_lift.txt -factor 1
pattern Plain 217 117 {
load 16 0 0 1000 0 0 0
} 
timeSeries Path 118 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_17_H_lift.txt -factor 1
pattern Plain 218 118 {
load 17 0 0 1000 0 0 0
} 
timeSeries Path 119 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_18_H_lift.txt -factor 1
pattern Plain 219 119 {
load 18 0 0 1000 0 0 0
} 
timeSeries Path 120 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_19_H_lift.txt -factor 1
pattern Plain 220 120 {
load 19 0 0 1000 0 0 0
} 
timeSeries Path 121 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_20_H_lift.txt -factor 1
pattern Plain 221 121 {
load 20 0 0 1000 0 0 0
} 
timeSeries Path 122 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_21_H_lift.txt -factor 1
pattern Plain 222 122 {
load 21 0 0 1000 0 0 0
} 
timeSeries Path 123 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_22_H_lift.txt -factor 1
pattern Plain 223 123 {
load 22 0 0 1000 0 0 0
} 
timeSeries Path 124 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_23_H_lift.txt -factor 1
pattern Plain 224 124 {
load 23 0 0 1000 0 0 0
} 
timeSeries Path 125 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_24_H_lift.txt -factor 1
pattern Plain 225 125 {
load 24 0 0 1000 0 0 0
} 
timeSeries Path 126 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_25_H_lift.txt -factor 1
pattern Plain 226 126 {
load 25 0 0 1000 0 0 0
} 
timeSeries Path 127 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_26_H_lift.txt -factor 1
pattern Plain 227 127 {
load 26 0 0 1000 0 0 0
} 
timeSeries Path 128 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_27_H_lift.txt -factor 1
pattern Plain 228 128 {
load 27 0 0 1000 0 0 0
} 
timeSeries Path 129 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_28_H_lift.txt -factor 1
pattern Plain 229 129 {
load 28 0 0 1000 0 0 0
} 
timeSeries Path 130 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_29_H_lift.txt -factor 1
pattern Plain 230 130 {
load 29 0 0 1000 0 0 0
} 
timeSeries Path 131 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_30_H_lift.txt -factor 1
pattern Plain 231 131 {
load 30 0 0 1000 0 0 0
} 
timeSeries Path 132 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_31_H_lift.txt -factor 1
pattern Plain 232 132 {
load 31 0 0 1000 0 0 0
} 
timeSeries Path 133 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_32_H_lift.txt -factor 1
pattern Plain 233 133 {
load 32 0 0 1000 0 0 0
} 
timeSeries Path 134 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_33_H_lift.txt -factor 1
pattern Plain 234 134 {
load 33 0 0 1000 0 0 0
} 
timeSeries Path 135 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_34_H_lift.txt -factor 1
pattern Plain 235 135 {
load 34 0 0 1000 0 0 0
} 
timeSeries Path 136 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_35_H_lift.txt -factor 1
pattern Plain 236 136 {
load 35 0 0 1000 0 0 0
} 
timeSeries Path 137 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_36_H_lift.txt -factor 1
pattern Plain 237 137 {
load 36 0 0 1000 0 0 0
} 
timeSeries Path 138 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_37_H_lift.txt -factor 1
pattern Plain 238 138 {
load 37 0 0 1000 0 0 0
} 
timeSeries Path 139 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_38_H_lift.txt -factor 1
pattern Plain 239 139 {
load 38 0 0 1000 0 0 0
} 
timeSeries Path 140 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_39_H_lift.txt -factor 1
pattern Plain 240 140 {
load 39 0 0 1000 0 0 0
} 
timeSeries Path 141 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_40_H_lift.txt -factor 1
pattern Plain 241 141 {
load 40 0 0 1000 0 0 0
} 
timeSeries Path 142 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_41_H_lift.txt -factor 1
pattern Plain 242 142 {
load 41 0 0 1000 0 0 0
} 
timeSeries Path 143 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_42_H_lift.txt -factor 1
pattern Plain 243 143 {
load 42 0 0 1000 0 0 0
} 
timeSeries Path 144 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_43_H_lift.txt -factor 1
pattern Plain 244 144 {
load 43 0 0 1000 0 0 0
} 
timeSeries Path 145 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_44_H_lift.txt -factor 1
pattern Plain 245 145 {
load 44 0 0 1000 0 0 0
} 
timeSeries Path 146 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_45_H_lift.txt -factor 1
pattern Plain 246 146 {
load 45 0 0 1000 0 0 0
} 
timeSeries Path 147 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_46_H_lift.txt -factor 1
pattern Plain 247 147 {
load 46 0 0 1000 0 0 0
} 
timeSeries Path 148 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_47_H_lift.txt -factor 1
pattern Plain 248 148 {
load 47 0 0 1000 0 0 0
} 
timeSeries Path 149 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_48_H_lift.txt -factor 1
pattern Plain 249 149 {
load 48 0 0 1000 0 0 0
} 
timeSeries Path 150 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_49_H_lift.txt -factor 1
pattern Plain 250 150 {
load 49 0 0 1000 0 0 0
} 
timeSeries Path 151 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_50_H_lift.txt -factor 1
pattern Plain 251 151 {
load 50 0 0 1000 0 0 0
} 
timeSeries Path 152 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_51_H_lift.txt -factor 1
pattern Plain 252 152 {
load 51 0 0 1000 0 0 0
} 
timeSeries Path 153 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_52_H_lift.txt -factor 1
pattern Plain 253 153 {
load 52 0 0 1000 0 0 0
} 
timeSeries Path 154 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_53_H_lift.txt -factor 1
pattern Plain 254 154 {
load 53 0 0 1000 0 0 0
} 
timeSeries Path 155 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_54_H_lift.txt -factor 1
pattern Plain 255 155 {
load 54 0 0 1000 0 0 0
} 
timeSeries Path 156 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_55_H_lift.txt -factor 1
pattern Plain 256 156 {
load 55 0 0 1000 0 0 0
} 
timeSeries Path 157 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_56_H_lift.txt -factor 1
pattern Plain 257 157 {
load 56 0 0 1000 0 0 0
} 
timeSeries Path 158 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_57_H_lift.txt -factor 1
pattern Plain 258 158 {
load 57 0 0 1000 0 0 0
} 
timeSeries Path 159 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_58_H_lift.txt -factor 1
pattern Plain 259 159 {
load 58 0 0 1000 0 0 0
} 
timeSeries Path 160 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_59_H_lift.txt -factor 1
pattern Plain 260 160 {
load 59 0 0 1000 0 0 0
} 
timeSeries Path 161 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_60_H_lift.txt -factor 1
pattern Plain 261 161 {
load 60 0 0 1000 0 0 0
} 
timeSeries Path 162 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_61_H_lift.txt -factor 1
pattern Plain 262 162 {
load 61 0 0 1000 0 0 0
} 
timeSeries Path 163 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_62_H_lift.txt -factor 1
pattern Plain 263 163 {
load 62 0 0 1000 0 0 0
} 
timeSeries Path 164 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_63_H_lift.txt -factor 1
pattern Plain 264 164 {
load 63 0 0 1000 0 0 0
} 
timeSeries Path 165 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_64_H_lift.txt -factor 1
pattern Plain 265 165 {
load 64 0 0 1000 0 0 0
} 
timeSeries Path 166 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_65_H_lift.txt -factor 1
pattern Plain 266 166 {
load 65 0 0 1000 0 0 0
} 
timeSeries Path 167 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_66_H_lift.txt -factor 1
pattern Plain 267 167 {
load 66 0 0 1000 0 0 0
} 
timeSeries Path 168 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_67_H_lift.txt -factor 1
pattern Plain 268 168 {
load 67 0 0 1000 0 0 0
} 
timeSeries Path 169 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_68_H_lift.txt -factor 1
pattern Plain 269 169 {
load 68 0 0 1000 0 0 0
} 
timeSeries Path 170 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_69_H_lift.txt -factor 1
pattern Plain 270 170 {
load 69 0 0 1000 0 0 0
} 
timeSeries Path 171 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_70_H_lift.txt -factor 1
pattern Plain 271 171 {
load 70 0 0 1000 0 0 0
} 
timeSeries Path 172 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_71_H_lift.txt -factor 1
pattern Plain 272 172 {
load 71 0 0 1000 0 0 0
} 
timeSeries Path 173 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_72_H_lift.txt -factor 1
pattern Plain 273 173 {
load 72 0 0 1000 0 0 0
} 
timeSeries Path 174 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_73_H_lift.txt -factor 1
pattern Plain 274 174 {
load 73 0 0 1000 0 0 0
} 
timeSeries Path 175 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_74_H_lift.txt -factor 1
pattern Plain 275 175 {
load 74 0 0 1000 0 0 0
} 
timeSeries Path 176 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_75_H_lift.txt -factor 1
pattern Plain 276 176 {
load 75 0 0 1000 0 0 0
} 
timeSeries Path 177 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_76_H_lift.txt -factor 1
pattern Plain 277 177 {
load 76 0 0 1000 0 0 0
} 
timeSeries Path 178 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_77_H_lift.txt -factor 1
pattern Plain 278 178 {
load 77 0 0 1000 0 0 0
} 
timeSeries Path 179 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_78_H_lift.txt -factor 1
pattern Plain 279 179 {
load 78 0 0 1000 0 0 0
} 
timeSeries Path 180 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_79_H_lift.txt -factor 1
pattern Plain 280 180 {
load 79 0 0 1000 0 0 0
} 
timeSeries Path 181 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_80_H_lift.txt -factor 1
pattern Plain 281 181 {
load 80 0 0 1000 0 0 0
} 
timeSeries Path 182 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_81_H_lift.txt -factor 1
pattern Plain 282 182 {
load 81 0 0 1000 0 0 0
} 
timeSeries Path 183 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_82_H_lift.txt -factor 1
pattern Plain 283 183 {
load 82 0 0 1000 0 0 0
} 
timeSeries Path 184 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_83_H_lift.txt -factor 1
pattern Plain 284 184 {
load 83 0 0 1000 0 0 0
} 
timeSeries Path 185 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_84_H_lift.txt -factor 1
pattern Plain 285 185 {
load 84 0 0 1000 0 0 0
} 
timeSeries Path 186 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_85_H_lift.txt -factor 1
pattern Plain 286 186 {
load 85 0 0 1000 0 0 0
} 
timeSeries Path 187 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_86_H_lift.txt -factor 1
pattern Plain 287 187 {
load 86 0 0 1000 0 0 0
} 
timeSeries Path 188 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_87_H_lift.txt -factor 1
pattern Plain 288 188 {
load 87 0 0 1000 0 0 0
} 
timeSeries Path 189 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_88_H_lift.txt -factor 1
pattern Plain 289 189 {
load 88 0 0 1000 0 0 0
} 
timeSeries Path 190 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_89_H_lift.txt -factor 1
pattern Plain 290 190 {
load 89 0 0 1000 0 0 0
} 
timeSeries Path 191 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_90_H_lift.txt -factor 1
pattern Plain 291 191 {
load 90 0 0 1000 0 0 0
} 
timeSeries Path 192 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_91_H_lift.txt -factor 1
pattern Plain 292 192 {
load 91 0 0 1000 0 0 0
} 
timeSeries Path 193 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_92_H_lift.txt -factor 1
pattern Plain 293 193 {
load 92 0 0 1000 0 0 0
} 
timeSeries Path 194 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_93_H_lift.txt -factor 1
pattern Plain 294 194 {
load 93 0 0 1000 0 0 0
} 
timeSeries Path 195 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_94_H_lift.txt -factor 1
pattern Plain 295 195 {
load 94 0 0 1000 0 0 0
} 
timeSeries Path 196 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_95_H_lift.txt -factor 1
pattern Plain 296 196 {
load 95 0 0 1000 0 0 0
} 
timeSeries Path 197 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_96_H_lift.txt -factor 1
pattern Plain 297 197 {
load 96 0 0 1000 0 0 0
} 
timeSeries Path 198 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_97_H_lift.txt -factor 1
pattern Plain 298 198 {
load 97 0 0 1000 0 0 0
} 
timeSeries Path 199 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_98_H_lift.txt -factor 1
pattern Plain 299 199 {
load 98 0 0 1000 0 0 0
} 
timeSeries Path 200 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_99_H_lift.txt -factor 1
pattern Plain 300 200 {
load 99 0 0 1000 0 0 0
} 
timeSeries Path 201 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_100_H_lift.txt -factor 1
pattern Plain 301 201 {
load 100 0 0 1000 0 0 0
} 
timeSeries Path 202 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_101_H_lift.txt -factor 1
pattern Plain 302 202 {
load 101 0 0 1000 0 0 0
} 
timeSeries Path 203 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_1_V_drag.txt -factor 1
pattern Plain 303 203 {
load 1 0 0 1000 0 0 0
} 
timeSeries Path 204 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_2_V_drag.txt -factor 1
pattern Plain 304 204 {
load 2 0 0 1000 0 0 0
} 
timeSeries Path 205 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_3_V_drag.txt -factor 1
pattern Plain 305 205 {
load 3 0 0 1000 0 0 0
} 
timeSeries Path 206 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_4_V_drag.txt -factor 1
pattern Plain 306 206 {
load 4 0 0 1000 0 0 0
} 
timeSeries Path 207 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_5_V_drag.txt -factor 1
pattern Plain 307 207 {
load 5 0 0 1000 0 0 0
} 
timeSeries Path 208 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_6_V_drag.txt -factor 1
pattern Plain 308 208 {
load 6 0 0 1000 0 0 0
} 
timeSeries Path 209 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_7_V_drag.txt -factor 1
pattern Plain 309 209 {
load 7 0 0 1000 0 0 0
} 
timeSeries Path 210 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_8_V_drag.txt -factor 1
pattern Plain 310 210 {
load 8 0 0 1000 0 0 0
} 
timeSeries Path 211 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_9_V_drag.txt -factor 1
pattern Plain 311 211 {
load 9 0 0 1000 0 0 0
} 
timeSeries Path 212 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_10_V_drag.txt -factor 1
pattern Plain 312 212 {
load 10 0 0 1000 0 0 0
} 
timeSeries Path 213 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_11_V_drag.txt -factor 1
pattern Plain 313 213 {
load 11 0 0 1000 0 0 0
} 
timeSeries Path 214 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_12_V_drag.txt -factor 1
pattern Plain 314 214 {
load 12 0 0 1000 0 0 0
} 
timeSeries Path 215 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_13_V_drag.txt -factor 1
pattern Plain 315 215 {
load 13 0 0 1000 0 0 0
} 
timeSeries Path 216 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_14_V_drag.txt -factor 1
pattern Plain 316 216 {
load 14 0 0 1000 0 0 0
} 
timeSeries Path 217 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_15_V_drag.txt -factor 1
pattern Plain 317 217 {
load 15 0 0 1000 0 0 0
} 
timeSeries Path 218 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_16_V_drag.txt -factor 1
pattern Plain 318 218 {
load 16 0 0 1000 0 0 0
} 
timeSeries Path 219 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_17_V_drag.txt -factor 1
pattern Plain 319 219 {
load 17 0 0 1000 0 0 0
} 
timeSeries Path 220 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_18_V_drag.txt -factor 1
pattern Plain 320 220 {
load 18 0 0 1000 0 0 0
} 
timeSeries Path 221 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_19_V_drag.txt -factor 1
pattern Plain 321 221 {
load 19 0 0 1000 0 0 0
} 
timeSeries Path 222 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_20_V_drag.txt -factor 1
pattern Plain 322 222 {
load 20 0 0 1000 0 0 0
} 
timeSeries Path 223 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_21_V_drag.txt -factor 1
pattern Plain 323 223 {
load 21 0 0 1000 0 0 0
} 
timeSeries Path 224 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_22_V_drag.txt -factor 1
pattern Plain 324 224 {
load 22 0 0 1000 0 0 0
} 
timeSeries Path 225 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_23_V_drag.txt -factor 1
pattern Plain 325 225 {
load 23 0 0 1000 0 0 0
} 
timeSeries Path 226 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_24_V_drag.txt -factor 1
pattern Plain 326 226 {
load 24 0 0 1000 0 0 0
} 
timeSeries Path 227 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_25_V_drag.txt -factor 1
pattern Plain 327 227 {
load 25 0 0 1000 0 0 0
} 
timeSeries Path 228 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_26_V_drag.txt -factor 1
pattern Plain 328 228 {
load 26 0 0 1000 0 0 0
} 
timeSeries Path 229 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_27_V_drag.txt -factor 1
pattern Plain 329 229 {
load 27 0 0 1000 0 0 0
} 
timeSeries Path 230 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_28_V_drag.txt -factor 1
pattern Plain 330 230 {
load 28 0 0 1000 0 0 0
} 
timeSeries Path 231 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_29_V_drag.txt -factor 1
pattern Plain 331 231 {
load 29 0 0 1000 0 0 0
} 
timeSeries Path 232 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_30_V_drag.txt -factor 1
pattern Plain 332 232 {
load 30 0 0 1000 0 0 0
} 
timeSeries Path 233 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_31_V_drag.txt -factor 1
pattern Plain 333 233 {
load 31 0 0 1000 0 0 0
} 
timeSeries Path 234 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_32_V_drag.txt -factor 1
pattern Plain 334 234 {
load 32 0 0 1000 0 0 0
} 
timeSeries Path 235 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_33_V_drag.txt -factor 1
pattern Plain 335 235 {
load 33 0 0 1000 0 0 0
} 
timeSeries Path 236 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_34_V_drag.txt -factor 1
pattern Plain 336 236 {
load 34 0 0 1000 0 0 0
} 
timeSeries Path 237 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_35_V_drag.txt -factor 1
pattern Plain 337 237 {
load 35 0 0 1000 0 0 0
} 
timeSeries Path 238 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_36_V_drag.txt -factor 1
pattern Plain 338 238 {
load 36 0 0 1000 0 0 0
} 
timeSeries Path 239 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_37_V_drag.txt -factor 1
pattern Plain 339 239 {
load 37 0 0 1000 0 0 0
} 
timeSeries Path 240 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_38_V_drag.txt -factor 1
pattern Plain 340 240 {
load 38 0 0 1000 0 0 0
} 
timeSeries Path 241 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_39_V_drag.txt -factor 1
pattern Plain 341 241 {
load 39 0 0 1000 0 0 0
} 
timeSeries Path 242 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_40_V_drag.txt -factor 1
pattern Plain 342 242 {
load 40 0 0 1000 0 0 0
} 
timeSeries Path 243 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_41_V_drag.txt -factor 1
pattern Plain 343 243 {
load 41 0 0 1000 0 0 0
} 
timeSeries Path 244 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_42_V_drag.txt -factor 1
pattern Plain 344 244 {
load 42 0 0 1000 0 0 0
} 
timeSeries Path 245 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_43_V_drag.txt -factor 1
pattern Plain 345 245 {
load 43 0 0 1000 0 0 0
} 
timeSeries Path 246 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_44_V_drag.txt -factor 1
pattern Plain 346 246 {
load 44 0 0 1000 0 0 0
} 
timeSeries Path 247 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_45_V_drag.txt -factor 1
pattern Plain 347 247 {
load 45 0 0 1000 0 0 0
} 
timeSeries Path 248 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_46_V_drag.txt -factor 1
pattern Plain 348 248 {
load 46 0 0 1000 0 0 0
} 
timeSeries Path 249 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_47_V_drag.txt -factor 1
pattern Plain 349 249 {
load 47 0 0 1000 0 0 0
} 
timeSeries Path 250 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_48_V_drag.txt -factor 1
pattern Plain 350 250 {
load 48 0 0 1000 0 0 0
} 
timeSeries Path 251 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_49_V_drag.txt -factor 1
pattern Plain 351 251 {
load 49 0 0 1000 0 0 0
} 
timeSeries Path 252 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_50_V_drag.txt -factor 1
pattern Plain 352 252 {
load 50 0 0 1000 0 0 0
} 
timeSeries Path 253 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_51_V_drag.txt -factor 1
pattern Plain 353 253 {
load 51 0 0 1000 0 0 0
} 
timeSeries Path 254 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_52_V_drag.txt -factor 1
pattern Plain 354 254 {
load 52 0 0 1000 0 0 0
} 
timeSeries Path 255 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_53_V_drag.txt -factor 1
pattern Plain 355 255 {
load 53 0 0 1000 0 0 0
} 
timeSeries Path 256 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_54_V_drag.txt -factor 1
pattern Plain 356 256 {
load 54 0 0 1000 0 0 0
} 
timeSeries Path 257 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_55_V_drag.txt -factor 1
pattern Plain 357 257 {
load 55 0 0 1000 0 0 0
} 
timeSeries Path 258 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_56_V_drag.txt -factor 1
pattern Plain 358 258 {
load 56 0 0 1000 0 0 0
} 
timeSeries Path 259 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_57_V_drag.txt -factor 1
pattern Plain 359 259 {
load 57 0 0 1000 0 0 0
} 
timeSeries Path 260 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_58_V_drag.txt -factor 1
pattern Plain 360 260 {
load 58 0 0 1000 0 0 0
} 
timeSeries Path 261 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_59_V_drag.txt -factor 1
pattern Plain 361 261 {
load 59 0 0 1000 0 0 0
} 
timeSeries Path 262 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_60_V_drag.txt -factor 1
pattern Plain 362 262 {
load 60 0 0 1000 0 0 0
} 
timeSeries Path 263 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_61_V_drag.txt -factor 1
pattern Plain 363 263 {
load 61 0 0 1000 0 0 0
} 
timeSeries Path 264 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_62_V_drag.txt -factor 1
pattern Plain 364 264 {
load 62 0 0 1000 0 0 0
} 
timeSeries Path 265 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_63_V_drag.txt -factor 1
pattern Plain 365 265 {
load 63 0 0 1000 0 0 0
} 
timeSeries Path 266 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_64_V_drag.txt -factor 1
pattern Plain 366 266 {
load 64 0 0 1000 0 0 0
} 
timeSeries Path 267 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_65_V_drag.txt -factor 1
pattern Plain 367 267 {
load 65 0 0 1000 0 0 0
} 
timeSeries Path 268 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_66_V_drag.txt -factor 1
pattern Plain 368 268 {
load 66 0 0 1000 0 0 0
} 
timeSeries Path 269 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_67_V_drag.txt -factor 1
pattern Plain 369 269 {
load 67 0 0 1000 0 0 0
} 
timeSeries Path 270 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_68_V_drag.txt -factor 1
pattern Plain 370 270 {
load 68 0 0 1000 0 0 0
} 
timeSeries Path 271 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_69_V_drag.txt -factor 1
pattern Plain 371 271 {
load 69 0 0 1000 0 0 0
} 
timeSeries Path 272 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_70_V_drag.txt -factor 1
pattern Plain 372 272 {
load 70 0 0 1000 0 0 0
} 
timeSeries Path 273 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_71_V_drag.txt -factor 1
pattern Plain 373 273 {
load 71 0 0 1000 0 0 0
} 
timeSeries Path 274 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_72_V_drag.txt -factor 1
pattern Plain 374 274 {
load 72 0 0 1000 0 0 0
} 
timeSeries Path 275 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_73_V_drag.txt -factor 1
pattern Plain 375 275 {
load 73 0 0 1000 0 0 0
} 
timeSeries Path 276 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_74_V_drag.txt -factor 1
pattern Plain 376 276 {
load 74 0 0 1000 0 0 0
} 
timeSeries Path 277 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_75_V_drag.txt -factor 1
pattern Plain 377 277 {
load 75 0 0 1000 0 0 0
} 
timeSeries Path 278 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_76_V_drag.txt -factor 1
pattern Plain 378 278 {
load 76 0 0 1000 0 0 0
} 
timeSeries Path 279 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_77_V_drag.txt -factor 1
pattern Plain 379 279 {
load 77 0 0 1000 0 0 0
} 
timeSeries Path 280 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_78_V_drag.txt -factor 1
pattern Plain 380 280 {
load 78 0 0 1000 0 0 0
} 
timeSeries Path 281 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_79_V_drag.txt -factor 1
pattern Plain 381 281 {
load 79 0 0 1000 0 0 0
} 
timeSeries Path 282 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_80_V_drag.txt -factor 1
pattern Plain 382 282 {
load 80 0 0 1000 0 0 0
} 
timeSeries Path 283 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_81_V_drag.txt -factor 1
pattern Plain 383 283 {
load 81 0 0 1000 0 0 0
} 
timeSeries Path 284 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_82_V_drag.txt -factor 1
pattern Plain 384 284 {
load 82 0 0 1000 0 0 0
} 
timeSeries Path 285 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_83_V_drag.txt -factor 1
pattern Plain 385 285 {
load 83 0 0 1000 0 0 0
} 
timeSeries Path 286 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_84_V_drag.txt -factor 1
pattern Plain 386 286 {
load 84 0 0 1000 0 0 0
} 
timeSeries Path 287 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_85_V_drag.txt -factor 1
pattern Plain 387 287 {
load 85 0 0 1000 0 0 0
} 
timeSeries Path 288 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_86_V_drag.txt -factor 1
pattern Plain 388 288 {
load 86 0 0 1000 0 0 0
} 
timeSeries Path 289 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_87_V_drag.txt -factor 1
pattern Plain 389 289 {
load 87 0 0 1000 0 0 0
} 
timeSeries Path 290 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_88_V_drag.txt -factor 1
pattern Plain 390 290 {
load 88 0 0 1000 0 0 0
} 
timeSeries Path 291 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_89_V_drag.txt -factor 1
pattern Plain 391 291 {
load 89 0 0 1000 0 0 0
} 
timeSeries Path 292 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_90_V_drag.txt -factor 1
pattern Plain 392 292 {
load 90 0 0 1000 0 0 0
} 
timeSeries Path 293 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_91_V_drag.txt -factor 1
pattern Plain 393 293 {
load 91 0 0 1000 0 0 0
} 
timeSeries Path 294 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_92_V_drag.txt -factor 1
pattern Plain 394 294 {
load 92 0 0 1000 0 0 0
} 
timeSeries Path 295 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_93_V_drag.txt -factor 1
pattern Plain 395 295 {
load 93 0 0 1000 0 0 0
} 
timeSeries Path 296 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_94_V_drag.txt -factor 1
pattern Plain 396 296 {
load 94 0 0 1000 0 0 0
} 
timeSeries Path 297 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_95_V_drag.txt -factor 1
pattern Plain 397 297 {
load 95 0 0 1000 0 0 0
} 
timeSeries Path 298 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_96_V_drag.txt -factor 1
pattern Plain 398 298 {
load 96 0 0 1000 0 0 0
} 
timeSeries Path 299 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_97_V_drag.txt -factor 1
pattern Plain 399 299 {
load 97 0 0 1000 0 0 0
} 
timeSeries Path 300 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_98_V_drag.txt -factor 1
pattern Plain 400 300 {
load 98 0 0 1000 0 0 0
} 
timeSeries Path 301 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_99_V_drag.txt -factor 1
pattern Plain 401 301 {
load 99 0 0 1000 0 0 0
} 
timeSeries Path 302 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_100_V_drag.txt -factor 1
pattern Plain 402 302 {
load 100 0 0 1000 0 0 0
} 
timeSeries Path 303 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_101_V_drag.txt -factor 1
pattern Plain 403 303 {
load 101 0 0 1000 0 0 0
} 
timeSeries Path 304 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_1_V_lift.txt -factor 1
pattern Plain 404 304 {
load 1 0 1000 0 0 0 0
} 
timeSeries Path 305 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_2_V_lift.txt -factor 1
pattern Plain 405 305 {
load 2 0 1000 0 0 0 0
} 
timeSeries Path 306 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_3_V_lift.txt -factor 1
pattern Plain 406 306 {
load 3 0 1000 0 0 0 0
} 
timeSeries Path 307 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_4_V_lift.txt -factor 1
pattern Plain 407 307 {
load 4 0 1000 0 0 0 0
} 
timeSeries Path 308 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_5_V_lift.txt -factor 1
pattern Plain 408 308 {
load 5 0 1000 0 0 0 0
} 
timeSeries Path 309 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_6_V_lift.txt -factor 1
pattern Plain 409 309 {
load 6 0 1000 0 0 0 0
} 
timeSeries Path 310 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_7_V_lift.txt -factor 1
pattern Plain 410 310 {
load 7 0 1000 0 0 0 0
} 
timeSeries Path 311 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_8_V_lift.txt -factor 1
pattern Plain 411 311 {
load 8 0 1000 0 0 0 0
} 
timeSeries Path 312 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_9_V_lift.txt -factor 1
pattern Plain 412 312 {
load 9 0 1000 0 0 0 0
} 
timeSeries Path 313 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_10_V_lift.txt -factor 1
pattern Plain 413 313 {
load 10 0 1000 0 0 0 0
} 
timeSeries Path 314 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_11_V_lift.txt -factor 1
pattern Plain 414 314 {
load 11 0 1000 0 0 0 0
} 
timeSeries Path 315 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_12_V_lift.txt -factor 1
pattern Plain 415 315 {
load 12 0 1000 0 0 0 0
} 
timeSeries Path 316 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_13_V_lift.txt -factor 1
pattern Plain 416 316 {
load 13 0 1000 0 0 0 0
} 
timeSeries Path 317 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_14_V_lift.txt -factor 1
pattern Plain 417 317 {
load 14 0 1000 0 0 0 0
} 
timeSeries Path 318 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_15_V_lift.txt -factor 1
pattern Plain 418 318 {
load 15 0 1000 0 0 0 0
} 
timeSeries Path 319 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_16_V_lift.txt -factor 1
pattern Plain 419 319 {
load 16 0 1000 0 0 0 0
} 
timeSeries Path 320 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_17_V_lift.txt -factor 1
pattern Plain 420 320 {
load 17 0 1000 0 0 0 0
} 
timeSeries Path 321 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_18_V_lift.txt -factor 1
pattern Plain 421 321 {
load 18 0 1000 0 0 0 0
} 
timeSeries Path 322 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_19_V_lift.txt -factor 1
pattern Plain 422 322 {
load 19 0 1000 0 0 0 0
} 
timeSeries Path 323 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_20_V_lift.txt -factor 1
pattern Plain 423 323 {
load 20 0 1000 0 0 0 0
} 
timeSeries Path 324 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_21_V_lift.txt -factor 1
pattern Plain 424 324 {
load 21 0 1000 0 0 0 0
} 
timeSeries Path 325 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_22_V_lift.txt -factor 1
pattern Plain 425 325 {
load 22 0 1000 0 0 0 0
} 
timeSeries Path 326 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_23_V_lift.txt -factor 1
pattern Plain 426 326 {
load 23 0 1000 0 0 0 0
} 
timeSeries Path 327 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_24_V_lift.txt -factor 1
pattern Plain 427 327 {
load 24 0 1000 0 0 0 0
} 
timeSeries Path 328 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_25_V_lift.txt -factor 1
pattern Plain 428 328 {
load 25 0 1000 0 0 0 0
} 
timeSeries Path 329 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_26_V_lift.txt -factor 1
pattern Plain 429 329 {
load 26 0 1000 0 0 0 0
} 
timeSeries Path 330 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_27_V_lift.txt -factor 1
pattern Plain 430 330 {
load 27 0 1000 0 0 0 0
} 
timeSeries Path 331 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_28_V_lift.txt -factor 1
pattern Plain 431 331 {
load 28 0 1000 0 0 0 0
} 
timeSeries Path 332 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_29_V_lift.txt -factor 1
pattern Plain 432 332 {
load 29 0 1000 0 0 0 0
} 
timeSeries Path 333 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_30_V_lift.txt -factor 1
pattern Plain 433 333 {
load 30 0 1000 0 0 0 0
} 
timeSeries Path 334 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_31_V_lift.txt -factor 1
pattern Plain 434 334 {
load 31 0 1000 0 0 0 0
} 
timeSeries Path 335 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_32_V_lift.txt -factor 1
pattern Plain 435 335 {
load 32 0 1000 0 0 0 0
} 
timeSeries Path 336 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_33_V_lift.txt -factor 1
pattern Plain 436 336 {
load 33 0 1000 0 0 0 0
} 
timeSeries Path 337 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_34_V_lift.txt -factor 1
pattern Plain 437 337 {
load 34 0 1000 0 0 0 0
} 
timeSeries Path 338 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_35_V_lift.txt -factor 1
pattern Plain 438 338 {
load 35 0 1000 0 0 0 0
} 
timeSeries Path 339 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_36_V_lift.txt -factor 1
pattern Plain 439 339 {
load 36 0 1000 0 0 0 0
} 
timeSeries Path 340 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_37_V_lift.txt -factor 1
pattern Plain 440 340 {
load 37 0 1000 0 0 0 0
} 
timeSeries Path 341 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_38_V_lift.txt -factor 1
pattern Plain 441 341 {
load 38 0 1000 0 0 0 0
} 
timeSeries Path 342 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_39_V_lift.txt -factor 1
pattern Plain 442 342 {
load 39 0 1000 0 0 0 0
} 
timeSeries Path 343 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_40_V_lift.txt -factor 1
pattern Plain 443 343 {
load 40 0 1000 0 0 0 0
} 
timeSeries Path 344 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_41_V_lift.txt -factor 1
pattern Plain 444 344 {
load 41 0 1000 0 0 0 0
} 
timeSeries Path 345 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_42_V_lift.txt -factor 1
pattern Plain 445 345 {
load 42 0 1000 0 0 0 0
} 
timeSeries Path 346 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_43_V_lift.txt -factor 1
pattern Plain 446 346 {
load 43 0 1000 0 0 0 0
} 
timeSeries Path 347 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_44_V_lift.txt -factor 1
pattern Plain 447 347 {
load 44 0 1000 0 0 0 0
} 
timeSeries Path 348 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_45_V_lift.txt -factor 1
pattern Plain 448 348 {
load 45 0 1000 0 0 0 0
} 
timeSeries Path 349 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_46_V_lift.txt -factor 1
pattern Plain 449 349 {
load 46 0 1000 0 0 0 0
} 
timeSeries Path 350 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_47_V_lift.txt -factor 1
pattern Plain 450 350 {
load 47 0 1000 0 0 0 0
} 
timeSeries Path 351 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_48_V_lift.txt -factor 1
pattern Plain 451 351 {
load 48 0 1000 0 0 0 0
} 
timeSeries Path 352 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_49_V_lift.txt -factor 1
pattern Plain 452 352 {
load 49 0 1000 0 0 0 0
} 
timeSeries Path 353 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_50_V_lift.txt -factor 1
pattern Plain 453 353 {
load 50 0 1000 0 0 0 0
} 
timeSeries Path 354 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_51_V_lift.txt -factor 1
pattern Plain 454 354 {
load 51 0 1000 0 0 0 0
} 
timeSeries Path 355 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_52_V_lift.txt -factor 1
pattern Plain 455 355 {
load 52 0 1000 0 0 0 0
} 
timeSeries Path 356 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_53_V_lift.txt -factor 1
pattern Plain 456 356 {
load 53 0 1000 0 0 0 0
} 
timeSeries Path 357 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_54_V_lift.txt -factor 1
pattern Plain 457 357 {
load 54 0 1000 0 0 0 0
} 
timeSeries Path 358 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_55_V_lift.txt -factor 1
pattern Plain 458 358 {
load 55 0 1000 0 0 0 0
} 
timeSeries Path 359 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_56_V_lift.txt -factor 1
pattern Plain 459 359 {
load 56 0 1000 0 0 0 0
} 
timeSeries Path 360 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_57_V_lift.txt -factor 1
pattern Plain 460 360 {
load 57 0 1000 0 0 0 0
} 
timeSeries Path 361 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_58_V_lift.txt -factor 1
pattern Plain 461 361 {
load 58 0 1000 0 0 0 0
} 
timeSeries Path 362 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_59_V_lift.txt -factor 1
pattern Plain 462 362 {
load 59 0 1000 0 0 0 0
} 
timeSeries Path 363 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_60_V_lift.txt -factor 1
pattern Plain 463 363 {
load 60 0 1000 0 0 0 0
} 
timeSeries Path 364 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_61_V_lift.txt -factor 1
pattern Plain 464 364 {
load 61 0 1000 0 0 0 0
} 
timeSeries Path 365 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_62_V_lift.txt -factor 1
pattern Plain 465 365 {
load 62 0 1000 0 0 0 0
} 
timeSeries Path 366 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_63_V_lift.txt -factor 1
pattern Plain 466 366 {
load 63 0 1000 0 0 0 0
} 
timeSeries Path 367 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_64_V_lift.txt -factor 1
pattern Plain 467 367 {
load 64 0 1000 0 0 0 0
} 
timeSeries Path 368 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_65_V_lift.txt -factor 1
pattern Plain 468 368 {
load 65 0 1000 0 0 0 0
} 
timeSeries Path 369 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_66_V_lift.txt -factor 1
pattern Plain 469 369 {
load 66 0 1000 0 0 0 0
} 
timeSeries Path 370 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_67_V_lift.txt -factor 1
pattern Plain 470 370 {
load 67 0 1000 0 0 0 0
} 
timeSeries Path 371 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_68_V_lift.txt -factor 1
pattern Plain 471 371 {
load 68 0 1000 0 0 0 0
} 
timeSeries Path 372 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_69_V_lift.txt -factor 1
pattern Plain 472 372 {
load 69 0 1000 0 0 0 0
} 
timeSeries Path 373 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_70_V_lift.txt -factor 1
pattern Plain 473 373 {
load 70 0 1000 0 0 0 0
} 
timeSeries Path 374 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_71_V_lift.txt -factor 1
pattern Plain 474 374 {
load 71 0 1000 0 0 0 0
} 
timeSeries Path 375 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_72_V_lift.txt -factor 1
pattern Plain 475 375 {
load 72 0 1000 0 0 0 0
} 
timeSeries Path 376 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_73_V_lift.txt -factor 1
pattern Plain 476 376 {
load 73 0 1000 0 0 0 0
} 
timeSeries Path 377 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_74_V_lift.txt -factor 1
pattern Plain 477 377 {
load 74 0 1000 0 0 0 0
} 
timeSeries Path 378 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_75_V_lift.txt -factor 1
pattern Plain 478 378 {
load 75 0 1000 0 0 0 0
} 
timeSeries Path 379 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_76_V_lift.txt -factor 1
pattern Plain 479 379 {
load 76 0 1000 0 0 0 0
} 
timeSeries Path 380 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_77_V_lift.txt -factor 1
pattern Plain 480 380 {
load 77 0 1000 0 0 0 0
} 
timeSeries Path 381 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_78_V_lift.txt -factor 1
pattern Plain 481 381 {
load 78 0 1000 0 0 0 0
} 
timeSeries Path 382 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_79_V_lift.txt -factor 1
pattern Plain 482 382 {
load 79 0 1000 0 0 0 0
} 
timeSeries Path 383 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_80_V_lift.txt -factor 1
pattern Plain 483 383 {
load 80 0 1000 0 0 0 0
} 
timeSeries Path 384 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_81_V_lift.txt -factor 1
pattern Plain 484 384 {
load 81 0 1000 0 0 0 0
} 
timeSeries Path 385 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_82_V_lift.txt -factor 1
pattern Plain 485 385 {
load 82 0 1000 0 0 0 0
} 
timeSeries Path 386 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_83_V_lift.txt -factor 1
pattern Plain 486 386 {
load 83 0 1000 0 0 0 0
} 
timeSeries Path 387 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_84_V_lift.txt -factor 1
pattern Plain 487 387 {
load 84 0 1000 0 0 0 0
} 
timeSeries Path 388 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_85_V_lift.txt -factor 1
pattern Plain 488 388 {
load 85 0 1000 0 0 0 0
} 
timeSeries Path 389 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_86_V_lift.txt -factor 1
pattern Plain 489 389 {
load 86 0 1000 0 0 0 0
} 
timeSeries Path 390 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_87_V_lift.txt -factor 1
pattern Plain 490 390 {
load 87 0 1000 0 0 0 0
} 
timeSeries Path 391 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_88_V_lift.txt -factor 1
pattern Plain 491 391 {
load 88 0 1000 0 0 0 0
} 
timeSeries Path 392 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_89_V_lift.txt -factor 1
pattern Plain 492 392 {
load 89 0 1000 0 0 0 0
} 
timeSeries Path 393 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_90_V_lift.txt -factor 1
pattern Plain 493 393 {
load 90 0 1000 0 0 0 0
} 
timeSeries Path 394 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_91_V_lift.txt -factor 1
pattern Plain 494 394 {
load 91 0 1000 0 0 0 0
} 
timeSeries Path 395 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_92_V_lift.txt -factor 1
pattern Plain 495 395 {
load 92 0 1000 0 0 0 0
} 
timeSeries Path 396 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_93_V_lift.txt -factor 1
pattern Plain 496 396 {
load 93 0 1000 0 0 0 0
} 
timeSeries Path 397 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_94_V_lift.txt -factor 1
pattern Plain 497 397 {
load 94 0 1000 0 0 0 0
} 
timeSeries Path 398 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_95_V_lift.txt -factor 1
pattern Plain 498 398 {
load 95 0 1000 0 0 0 0
} 
timeSeries Path 399 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_96_V_lift.txt -factor 1
pattern Plain 499 399 {
load 96 0 1000 0 0 0 0
} 
timeSeries Path 400 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_97_V_lift.txt -factor 1
pattern Plain 500 400 {
load 97 0 1000 0 0 0 0
} 
timeSeries Path 401 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_98_V_lift.txt -factor 1
pattern Plain 501 401 {
load 98 0 1000 0 0 0 0
} 
timeSeries Path 402 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_99_V_lift.txt -factor 1
pattern Plain 502 402 {
load 99 0 1000 0 0 0 0
} 
timeSeries Path 403 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_100_V_lift.txt -factor 1
pattern Plain 503 403 {
load 100 0 1000 0 0 0 0
} 
timeSeries Path 404 -dt 0.05 -filePath data/forces/FORCE_3/SIM1/NODE_101_V_lift.txt -factor 1
pattern Plain 504 404 {
load 101 0 1000 0 0 0 0
} 
recorder Node -file Dynamic.out -time -nodeRange 1 101 -dof 1 2 3 disp; 
recorder Node -file Reaction.out -time -node 1 -dof 1 2 3 reaction; 
recorder Node -file SupportReactions.out -time -node 1 101 -dof 1 2 3 reaction; 
recorder Node -file Velocity.out -time -nodeRange 1 101 -dof 1 2 3 vel; 
recorder Node -file Accel.out    -time -nodeRange 1 101 -dof 1 2 3 accel; 
wipeAnalysis
rayleigh 0.021489 0 0 0
constraints Transformation
numberer Plain
system FullGeneral
test NormDispIncr 1.00e-06 100
algorithm KrylovNewton;
integrator Newmark 0.5 0.25
analysis Transient
set total_duration 72.0000
set initial_num_incr 1440
set STKO_VAR_time_increment 0.050000
source tcl_procedures/Damping_shifter.tcl
source tcl_procedures/dynamic2.tcl
# Done! 
puts "ANALYSIS SUCCESSFULLY FINISHED" 
exit; 

