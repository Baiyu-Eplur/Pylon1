proc readColumnFromFile {filename column} {
    set file [open $filename r]
    set result {}
    while {[gets $file line] >= 0} {
        lappend result [lindex [split $line] $column]
    }
    close $file
    return $result
}


# Example usage:
# set filename "data.txt"
# set column 1  ;# Change to the column index you want to read (0-based indexing)

# set columnData [readColumnFromFile $filename $column]
# puts "Data read from column $column in $filename:"
# puts $columnData