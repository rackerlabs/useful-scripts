#!/bin/bash

export LVM_SUPPRESS_FD_WARNINGS=1

BREAK="============================================================"

NotRun=()              # Array to store all commands not run during script

PrintHeader() {        # Common header used throughout script
    if [[ "$bbcode" = "True" ]] && [[ "$2" == "NoTags" ]]; then
        echo
        echo -ne "$BREAK \n \t ==[b] $1 [/b]== \n$BREAK \n\n";
    elif [[ "$bbcode" = "True" ]] && [[ "$2" == "NoOpen" ]]; then
        echo "[/code]"
        echo
        echo -ne "$BREAK \n \t ==[b] $1 [/b]== \n$BREAK \n\n";
    elif [[ "$bbcode" = "True" ]] && [[ "$2" == "NoClose" ]]; then
        echo
        echo -ne "$BREAK \n \t ==[b] $1 [/b]== \n$BREAK \n\n";
        echo '[code]'
    elif [[ "$bbcode" = "True" ]]; then
        echo "[/code]"
        echo
        echo -ne "$BREAK \n \t ==[b] $1 [/b]== \n$BREAK \n\n";
        echo '[code]'
    else
        echo -ne "\n$BREAK \n \t == $1 == \n$BREAK \n\n";
    fi
}
usage() {              # Print script usage function
    echo "Usage: $0 [-f] [-i] [-b] [-h]"
    echo "           -i, --inode                    Display Inode breakdown"
    echo "           -f, --filesystem <filesystem>  Specify a Filesystem"
    echo "           -b, --bbcode                   Print with bbcode"
    echo "           -h, --help                     Print help (usage)"
    exit 1
}
start_time() {
    intStartTime=$(date +%s)
    PrintHeader "Server Time at start" "NoClose"
    date
}
end_time() {
    intEndTime=$(date +%s);
    intDuration=$((intEndTime-intStartTime));
    PrintHeader "Elapsed Time" "NoClose"
    printf '%dh:%dm:%ds\n' $(($intDuration/3600)) $(($intDuration%3600/60)) $(($intDuration%60));

    PrintHeader "Server Time at completion"
    date;
    if [[ $bbcode = 'True' ]]; then
        echo "[/code]"
    fi
}
filesystem_overview() {
    df -PTh $filesystem;
    echo
    df -PTi $filesystem;
    if [[ $bbcode = 'True' ]]; then
        echo "[/code]"
    fi
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

    if [ $return_code -le 0 ] && [ $( vgs 2>/dev/null | wc -l ) -gt 1 ]; then
        PrintHeader "Volume Group Usage"
        vgs $(df -h $filesystem | grep dev | awk '{print $1}'| cut -d\- -f1| cut -d\/ -f4)
    else
        NotRun+=("vgs")
    fi
}
lsof_check_open_deleted() {  # Check top 5 open deleted files function over 500MB
    open_files=$( lsof 2>/dev/null | awk '/REG/ && /deleted/ {x=3;y=1; print $(NF-x) "  " $(NF-y) }' | sort -nr | uniq  | awk '{ if($1 > 524288000 ) print $1/1048576, "MB ", $NF }')
    if [ "$open_files" ]; then
        PrintHeader "Top 5 Open DELETED Files over 500MB"
        echo -e "$open_files"  | head -5;
    else
        NotRun+=("lsof_large_open_deleted");
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
    PrintHeader "OK Checklist" "NoOpen"
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
        "lsof_large_open_deleted" )
            echo "[OK]      No open DELETED files over 500MB"
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
check_inodes() {
    intNumFiles=20;
    intDepth=5;
    strFsMount=$(df -P $filesystem | awk '$1 !~ /Filesystem/ {print $6}');

    resize 2&> /dev/null;

    start_time

    PrintHeader "Inode Information for [ $strFsMount ]"

    df -PTi $strFsMount | column -t;
    strFsDev=$(df -P $PWD | awk '$0 !~ /Filesystem/ {print $1}');
    PrintHeader "Storage device behind filesystem [ $strFsMount ]"
    echo $strFsDev;
    PrintHeader "Top inode Consumers on [ $strFsMount ]"

    awk '{ printf "%11s \t %-30s\n", $1, $2 }' <(echo "inode-Count Path");
    awk '{ printf "%11'"'"'d \t %-30s\n", $1, $2 } ' <(
     strMounts="$(findmnt -o TARGET -rn | sed 's/^\s*/\^/g' | sed 's/$/\$|/g' | tr -d '\n' | sed 's/|$/\n/')";
           find $strFsMount -maxdepth $intDepth -xdev -type d -print0 2>/dev/null | while IFS= read -rd '' i;
               do if ! echo $i | grep -E "$strMounts";
                   then echo "$(find "$i" -xdev | wc -l ) $i ";
               fi;
           done | sort -n -r | head -n $intNumFiles
    ) ;

    PrintHeader "Bytes per Inode format for [ $strFsMount ]"
    echo "$(printf "%.1f\n" $(echo "$(tune2fs -l $strFsDev | awk -F ": *" '$1 ~ /Inode count/ { inodecount = $2 }; $1 == "Block count" {printf "%s", $2}; $1 == "Block size" {printf "%s", " * " $2 " / " inodecount };' | tr -d '\n') /1024" | bc)) KB per inode"'!';

    PrintHeader "Disk space [ $strFsMount ]"
    filesystem_overview

    end_time

}


# Allow for long options. Code based off https://stackoverflow.com/a/30026641
for arg in "$@"; do
  shift
  case "$arg" in
    "--help")
        set -- "$@" "-h"
        ;;
    "--inode")
        set -- "$@" "-i"
        ;;
    "--bbcode")
        set -- "$@" "-b"
        ;;
    "--filesystem")
        set -- "$@" "-f"
        ;;
    "--"*)
        echo "Invalid option: ${arg}" 1>&2
        usage ${arg}
        exit 2
        ;;
    *)
        set -- "$@" "$arg"
  esac
done


# Checking the script arguments and assigning the appropriate $filesystem
while getopts ":f:ihb" opt; do
    case ${opt} in
    f )
        filesystem=$OPTARG
        ;;
    b )
        bbcode='True'
        ;;
    i )
        inode='True'
        ;;
    \? )
        echo "Invalid option: $OPTARG" 1>&2
        usage
        exit 1
        ;;
    : )
        echo "Invalid option: -f, --filesystem requires an argument" 1>&2
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

# If inode is specified, we only want to get a breakdown of the systems inodes
if [[ "$inode" = "True" ]]; then
    PrintHeader "$filesystem Filesystem Information" "NoTags"
    echo "Checking Inodes. Please note this could take a while to run..."
    check_inodes
# If inode is not specified, run a normal filesystem breakdown
else
    PrintHeader "$filesystem Filesystem Information" "NoClose"
    filesystem_overview
    start_time
    PrintHeader "Largest Directories"
    large_directories
    PrintHeader "Largest Files"
    largest_files
    # Check to see if logical volumes are being used
    logical_volumes

    if  [ "$( which lsof 2>/dev/null )" ]; then
        # Check open deleted filed
        lsof_check_open_deleted
    else
        NotRun+=("lsof_large_open_deleted");
    fi

    # Run home_rack function to check disk usage
    home_rack
    # Print commands/sections not run
    NotRun
    end_time
fi

echo
echo $BREAK
echo

exit 0
