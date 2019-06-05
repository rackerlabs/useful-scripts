#!/bin/bash

export LVM_SUPPRESS_FD_WARNINGS=1

BREAK="============================================================"

NotRun=()              # Array to store all commands not run during script

PrintFirstHeader(){
    if [[ $bbcode = 'True' ]]; then  
        echo -ne "\n$BREAK \n \t == $1 == \n$BREAK \n\n";
        echo "[code]"
    else
        echo -ne "\n$BREAK \n \t == $1 == \n$BREAK \n\n";
    fi
}
PrintHeader() {        # Common header used throughout script
    if [[ $bbcode = 'True' ]]; then
        echo "[/code]"
        echo
        echo -ne "$BREAK \n \t == $1 == \n$BREAK \n\n";
        echo '[code]'
    else
        echo -ne "\n$BREAK \n \t == $1 == \n$BREAK \n\n";
    fi
}
usage() {              # Print script usage function
    echo "Usage: $0 [-f] [-b] [-h]"
    echo "           -f filesystem        Specify a Filesystem"
    echo "           -b                   Print with bbcode"
    echo "           -h                   Print help (usage)"
    exit 1
}
filesystem_overview() {
    df -PTh $filesystem;
    echo
    df -PTi $filesystem;
}
large_directories() {
    if [[ ! $( du -hcx --max-depth=2 $filesystem 2>/dev/null | grep -P '^([0-9]\.*)*G(?!.*(\btotal\b|\./$))' ) ]]; then
        du -hcx --max-depth=2 $filesystem 2>/dev/null | sort -rnk1,1 | head -10 | column -t 2>/dev/null;
    else
        du -hcx --max-depth=2 $filesystem 2>/dev/null | grep -P '^([0-9]\.*)*G(?!.*(\btotal\b|\./$))' | sort -rnk1,1 | head -10 | column -t 2>/dev/null ;
    fi
}
largest_files() {
    find $filesystem -mount -ignore_readdir_race -type f -exec du {} + 2>&1 | sort -rnk1,1 | head -20 | awk 'BEGIN{ CONVFMT="%.2f";}{ $1=( $1 / 1024 )"M"; print;}' | column -t 2>/dev/null
}
logical_volumes() {
    df_zero=$( df -h $filesystem | awk '/dev/ {print $1}'| cut -d\- -f1| cut -d\/ -f4 )
    vgs_output=$( vgs $(df -h $filesystem | awk '/dev/ {print $1}'| cut -d\- -f1| cut -d\/ -f4) &>/dev/null )
    return_code=$?

    if [ $return_code -le 0 ] && [ $( vgs | wc -l ) -gt 1  ]; then
        PrintHeader "Volume Group Usage"
        vgs $(df -h $filesystem | grep dev | awk '{print $1}'| cut -d\- -f1| cut -d\/ -f4)
    else
        NotRun+=("vgs")
    fi
}
lsof_check_number() {  # Check deleted files function
    if [ "$( lsof | awk '/REG/ && !/stat: No such file or directory/ && !/DEL/ {if ($NF=="(deleted)") {x=3;y=1} else {x=2;y=0}; {print $(NF-x) "  " $(NF-y) } }'  | awk '{ if($1 > 1000000000 ) print $1/1048576, "MB ", $NF }'  )" ] && [ "$( which lsof 2>/dev/null )" ]; then
        PrintHeader "Open Deleted Files Over 1GB"
        lsof | awk '/REG/ && !/stat: No such file or directory/ && !/DEL/ {if ($NF=="(deleted)") {x=3;y=1} else {x=2;y=0}; {print $(NF-x) "  " $(NF-y) } }'  | sort -n -u  | awk '{ if($1 > 1000000000 ) print $1/1048576, "MB ", $NF }' | tail -5 | head -5 ;
    else
        NotRun+=("lsof_large")
    fi
}
home_rack() {         # Check disk usage in /home/rack
    if [ -d "/home/rack" ]; then
        rack=$( du -s /home/rack | awk '{print $1}' )
        if [ $rack -gt 1048576 ]; then
            if [[ $bbcode = 'True' ]]; then
                PrintHeader "[b]/home/rack/ LARGE! Please check[/b]"
            else
                PrintHeader "/home/rack/ LARGE! Please check"
            fi
            echo "[WARNING] $( du -h /home/rack --max-depth=1  | sort -rh |head -5 2>/dev/null )"
        else
            NotRun+=("home_rack")
        fi
    else
        NotRun+=("home_rack_exists_false")
    fi
}
NotRun() {           # Print a list of commands not run at the end of the script
    if [[ $bbcode = 'True' ]]; then
        echo "[/code]"
    fi
    echo -ne "\n$BREAK \n \t == "OK Check List" == \n$BREAK \n\n";
    echo "The following have been checked and are ok: "
    echo

    for i in "${NotRun[@]}"; do

        case $i in

        "vgs" )
            echo "[OK]      No Volume groups (vgs) found"
        ;;
        "lsof" )
            echo "[CHECK]   lsof not found, cannot check 'Open Deleted Files'"
        ;;
        "lsof_large" )
            echo "[OK]      No deleted files over 1GB"
        ;;
        "home_rack" )
            printf "[OK]      /home/rack smaller than 1GB: $(($rack / 1024)) MB\n"
        ;;
        "home_rack_exists_false" )
            echo "[WARNING] /home/rack does not appear to exist"
        ;;
        esac
    done
}


# Checking the script arguments and assigning the appropriate $filesystem
while getopts ":f:hb" opt; do
    case ${opt} in
    f )
        filesystem=$OPTARG
        ;;
    b )
        bbcode='True'
        ;;
    \? )
        echo "Invalid option: $OPTARG" 1>&2
        usage
        exit 1
        ;;
    : )
        echo "Invalid option: -$OPTARG requires an argument" 1>&2
        exit 1
        ;;
    h )
        usage
        exit 0
    esac
done
shift $((OPTIND -1))


if [ -z $filesystem ]; then
    filesystem='/'
elif [ ! -d $filesystem ]; then
    echo "Invalid Filesystem"
    echo
    usage
fi

echo


##############################################################################################

PrintFirstHeader "$filesystem Filesystem Information"

filesystem_overview

PrintHeader "Largest Directories"

large_directories

PrintHeader "Largest Files"

largest_files

# Check to see if logical volumes are being used
logical_volumes

# Check if lsof is installed
lsof_check_number

# Run home_rack function to check disk usage
home_rack

# Print commands/sections not run
NotRun

echo
echo $BREAK
echo

exit 0

