proc interpolate {target_x vec1 vec2} {
    set n [llength $vec1]
    set m [llength $vec2]
    if {$n == 0 || $m == 0} {
        error "interpolate: empty input vector"
    }
    if {$n != $m} {
        error "interpolate: vec1 and vec2 length mismatch"
    }

    set x_first [lindex $vec1 0]
    set y_first [lindex $vec2 0]
    if {$target_x <= $x_first} {
        return $y_first
    }

    set x_last [lindex $vec1 end]
    set y_last [lindex $vec2 end]
    if {$target_x >= $x_last} {
        return $y_last
    }

    for {set i 1} {$i < $n} {incr i} {
        set x2 [lindex $vec1 $i]
        if {$target_x <= $x2} {
            set x1 [lindex $vec1 [expr {$i - 1}]]
            set y1 [lindex $vec2 [expr {$i - 1}]]
            set y2 [lindex $vec2 $i]
            if {abs($x2 - $x1) < 1.0e-14} {
                return $y2
            }
            return [expr {$y1 + ($y2 - $y1) * ($target_x - $x1) / ($x2 - $x1)}]
        }
    }

    return $y_last
}
