#!/bin/bash
# This script is designed to automate creating and verifying subrepos
# Every git subrepo clone will be verified with a sha1sum to prove they are identical to the cloned repo
# Every update/fetch for a sub repo will be presented with an output of the commit differences

# Colours and Formating

REPOURL_RAW="https://raw.githubusercontent.com/rackerlabs/useful-scripts/"

# EF<letter> = End Formatting <option>
UNDERLINE="\e[4m"
EFU="\e[24m"
GREEN='\033[0;32m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
EFC='\033[0m'

unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)
        SHACOMMAND="sha1sum"
    ;;
    Darwin*)
        SHACOMMAND="shasum"
    ;;
    *)
        echo "Unknown OS"
        exit 1
    ;;
esac

# Usage info
usage() {              # Print script usage function
    echo "Usage: $0 [options]"
    echo "          -a, --add     <reponame> <url>   Specify name of new repo"
    echo "          -a, --add     <reponame> <url> -b <release>
                                           Specify name of new repo and a specific release"
    echo "          -u, --update  <reponame>         Update existing repo"
    echo "          -c, --check   <reponame>         Check for updates on existing repo"
    echo "          -v, --verify  <reponame> [local] Verifies local branch (not been pushed to git)"
    echo ""
    echo "          -h, --help                      Print help (usage)"
    exit 1
}

# Gracefully close script with a message
error_message() {
    printf '%s\n' "$1" >&2
    exit 1
}

# Make sure any changes are made to a sub branch. This ensured a PR is made and no direct
# "git push" is made to the master branch
check_local_branch() {
    if ! [[ "$2" == "" ]]; then
        update="-$2"
    else
        update="$2"
    fi
    branch_name=$(echo "$1" | sed 's/\///g')
    answer=""
    current_branch=$(git symbolic-ref --short -q HEAD)

    if [[ "$current_branch" == "master" ]]; then
        echo
        echo -e "$RED""Error: You appear to be working on the master branch!$EFC"
        echo "Updating/adding should be added to a sub branch."
        echo
        while [[ ! ( "$answer" =~ (y|Y|ye|Ye|yes|YES|Yes)$ ) ]]; do
            echo -n "Would you like to autocreate a new branch ($branch_name$update-$(date +'%Y-%m-%d'))? (y|n) "
            read answer </dev/tty
            if [[ $(git branch | grep "$branch_name$update-$(date +'%Y-%m-%d')" | cut -d ' ' -f3) ]]; then
                echo -e "$RED""Error: branch name already exists"
                echo -e "Exiting.....$EFC"
                echo
                exit 1
            else
                case $answer in
                y|ye|yes|Y|YES|Ye|Yes )
                    git checkout -b $branch_name$update-$(date +"%Y-%m-%d") 2>/dev/null
                ;;
                n|N|no|NO )
                    exit 1
                ;;
                esac
            fi
        done
    fi
}

# If "update/check" then make sure repo exists. If "add", make sure repo does not exist
repo_exist_check() {
    _pwd=$(pwd)

    if [ "$1" == "" ]; then
        error_message '
Please provide a directory argument'
    elif [ "$1" == "empty" ] && [ -d "$_pwd/$2" ]; then
        error_message '
Directory '"$_pwd/$2"' already exists.
Please make sure directory does NOT exist for new subrepos'
    elif ! [ "$1" == "empty" ] && ! [ -d "$_pwd/$2" ]; then
        error_message '
Please check repo "'"$1"'", it does not appear to exist'
    fi
}

# Verify the URL provided as an argument to add as a subrepo
clone_repo() {
    _new_repo_name="$1"
    _url="$2"

    if [[ ! $3 = '' ]]; then
        git subrepo clone "$_url" "$_new_repo_name" --branch "$3"
    else
        git subrepo clone "$_url" "$_new_repo_name"
    fi

    # Now verifying
    validate_current_commit "$_new_repo_name" "local"
}

# Not everything in a subrepo needs to be checksum'd. Only the file being executed
# This function finds the appropriate file(s) and asks you to select if more than 1 executable file exists
find_checksum_file() {
    _files=$(for i in $(find $1 -type d -exec ls '{}' ';' | grep ".sh\|.py\|mysqltuner.pl\|apache2buddy.pl" | grep -v 'setup\|test\|php-fpmpal.sh\|php-fpmpal.py\|cron'); do echo $i; done)

    counter=1

    if [ $( echo $_files | wc -w) -le 1 ]; then
        selection="$_files"
    else
        echo
        for i in $_files; do
            echo $counter" -" $i
            counter=$((counter + 1))
        done
        echo "Which option number would you like to check? "
        read input </dev/tty
        echo
        selection=$(echo $_files | cut -d " " -f $input)
        echo "Your option was "$input "which is ""$selection"
    fi
}

# Checks repo master branch with cloned repo commit hash - verify sha1sum
validate_current_commit() {
    _trailingslash="$_pwd/$1/.gitrepo"
    _notrailingslash="$_pwd/$1.gitrepo"
    repo_location="$2"

    if [ -a "$_notrailingslash" 2>/dev/null ]; then
        _subrepo_information="$_notrailingslash"
        _subrepo_name="$1"
        _dir="$_pwd/$1"
    elif [ -a "$_trailingslash" 2>/dev/null ]; then
        _subrepo_information="$_trailingslash"
        _subrepo_name="$1/"
        _dir="$_pwd/$1/"
    else
        echo
        echo -e "$RED""$1.gitrepo" "repo does not appear to exist.""$EFC"
        echo "You can only check for updates against the master branch"
        exit 1
    fi

    find_checksum_file "$_pwd/$1"

    case "$repo_location" in
        "verify")  # Verifying the commit hash is valid
        branch_name=$(git symbolic-ref --short -q HEAD)
        repo_location="remote"

        raw_subrepo="$REPOURL_RAW""$branch_name/$_subrepo_name"
        subrepo_sha1sum=$(curl -s "$raw_subrepo$selection" | ${SHACOMMAND} | awk '{print $1}' )
        script_location="$raw_subrepo$selection"

        commit_path="$raw_subrepo"".gitrepo"
        _commit=$(curl -s "$commit_path" | awk -F' = ' '/commit/ { print $2 }')
        ;;

        "local")  # For branches not yet pushed to github
        branch_name=$(git symbolic-ref --short -q HEAD)

        subrepo_sha1sum=$( ${SHACOMMAND} "$_dir$selection" | awk '{print $1}' )
        script_location="$_dir$selection"

        commit_path="$_dir"".gitrepo"
        _commit=$(awk -F'= ' '/commit/ {print $2}' "$_subrepo_information")
        _remote=$(awk -F'= ' '/remote/ {print $2}' "$_subrepo_information")
        ;;

        *)
        branch_name="master"
        repo_location="remote"

        raw_subrepo="$REPOURL_RAW""$branch_name/$_subrepo_name"
        subrepo_sha1sum=$(curl -s "$raw_subrepo$selection" | ${SHACOMMAND}  | awk '{print $1}' )

        script_location="$raw_subrepo$selection"
        commit_path="$raw_subrepo"".gitrepo"
        _commit=$(curl -s "$commit_path" | awk -F' = ' '/commit/ { print $2 }')
        ;;
    esac

    _remote=$(awk -F'= ' '/remote/ {print $2}' "$_subrepo_information")

    # Find the sha1sum of the original script
    raw_remote=$(echo $_remote | sed 's/github.com/raw.githubusercontent.com/g'  | sed "s/\.git$/\/$_commit/g")
    remote_sha1sum=$(curl -s "$raw_remote/$selection" | ${SHACOMMAND}  | awk '{print $1}' )

    echo
    echo "------------------------------------------"
    echo -e "$PURPLE""Verifying recorded commit...$EFC"
    echo
    echo "Commit on file: $_commit"
    echo "$commit_path"
    echo
    echo -e "$UNDERLINE""Remote Repo Info (commit)$EFU"
    echo "$raw_remote/$selection"
    echo "sha1sum: ""$remote_sha1sum"
    echo
    echo -e "$UNDERLINE""SubRepo ($repo_location) Info ($branch_name)$EFU"
    echo "$script_location"
    echo "sha1sum: ""$subrepo_sha1sum"
    echo

    if [ "$remote_sha1sum" == "$subrepo_sha1sum" ]; then
        echo -e "Verifying commit: $GREEN""sha1sums match!""$EFC"
        echo "$branch_name ($repo_location branch) is inline with specified commit hash"
    else
        echo "------------------------------------------"
        echo
        echo -e "Verifying commit: $RED""sha1sums do NOT match!$EFC"
        if [[ $( curl -s $script_location | grep -e 404 ) ]]; then
            echo -e "$RED""ERROR:$EFC The following location does not exist:"
            echo "     $script_location"
            echo
            echo "Is this a local branch or a remote branch?"
            echo -e "'--check' only works on the master branch. You are on the following branch: $RED$(git symbolic-ref --short -q HEAD)"$EFC
            echo "Please use '--verify local' if the branch has not been merged into the master"
            echo
            echo "------------------------------------------"
        else
            echo "Please check why the $repo_location ($branch_name) repo does not match the commit hash we have on file"
        fi
        exit 1
    fi
    echo "------------------------------------------"
    echo
}

# Check to see if the remote branch is ahead of our subrepo
check_available_updates() {
    raw_remote_commit="$1"
    _commit=$( echo $raw_remote_commit | awk -F'/' '{ print $NF }')
    selection="$2"
    raw_remote_commit_sha1sum="$3"

    _remote=$( awk -F'= ' '/remote/ {print $2}' "$_subrepo_information" )

    raw_remote_master=$( echo $_remote | sed 's/github.com/raw.githubusercontent.com/g'  | sed "s/\.git$/\/master\/$selection/g" )
    raw_remote__master_sha1sum=$(curl -s "$raw_remote_master" | ${SHACOMMAND}  | awk '{print $1}' )

    echo "------------------------------------------"
    echo -e "$PURPLE""Checking if updates available... (script/commit vs script/master)$EFC"
    echo
    echo -e "$UNDERLINE""Remote 'Commit' URL$EFU"
    echo "$raw_remote_commit/$selection"
    echo "sha1sum: ""$raw_remote_commit_sha1sum"
    echo
    echo -e "$UNDERLINE""Remote 'Master' URL$EFU"
    echo "$raw_remote_master"
    echo "sha1sum: ""$raw_remote__master_sha1sum"

    echo
    if ! [ "$raw_remote_commit_sha1sum" == "$raw_remote__master_sha1sum" ]; then
        _compare=$( echo $_remote | sed 's#\.git$#/compare/'${_commit}'...master#g' )
        echo "Master and commit hash do NOT match"
        echo -e "Updates: ""$GREEN""Possible updates available$EFC"
        echo
        echo -e "$GREEN""Compare URL:$EFC"
        echo "$_compare"
    else
        echo -e "Updates: ""$RED""No updates are currently available$EFC"
        exit 1
    fi

    echo
    echo "------------------------------------------"
    echo
}

# Do you want to update the branch?
branchupdate() {
    repo="$1"
    if ! [[ $(git subrepo pull "$repo") ]]; then
        echo
        echo -e "$RED""You appear to have unstaged changed in your master repo.$EFC"
        echo "Please commit master branch changes first"
        git checkout master
        git status
        echo
        exit 1
    fi

    echo -e "$GREEN""Branch Updated.....""$EFC"
    echo -e "$GREEN""Verifying Update.....""$EFC"
    echo 'Cleaning up....'
    git branch -D subrepo/"$repo"

    repo_exist_check "$repo"
    validate_current_commit "$repo" "local"
}

# Check to see if git and git subrepo are installed
git_subrepo() {
    version=$(git subrepo --version 2>&1)

    # Check if git and git subrepo are installed
    if ! [ -x $(command -v git 2>/dev/null) ]; then
        error_message '
git is not installed, please install!
After git installation please install git subrepo:
                https://github.com/ingydotnet/git-subrepo'
    elif [ "$version" == "git: 'subrepo' is not a git command. See 'git --help'." ]; then
        error_message '
"git subrepo" does not appear to be installed.
Please install git subrepo:
                https://github.com/ingydotnet/git-subrepo'
    elif echo "$version" "0.4.0" | awk '{ exit !($1 > $2)}'; then
       error_message '
"git subrepo" version is too low
Please update:
                https://github.com/ingydotnet/git-subrepo'
    fi
}


git_subrepo

# If no arguments, provide the usage function
if [ -z "$*" ]; then
    usage
fi

# Goes through all of the script arguments
while :; do
    case $1 in
        "-h"|-\?|"--help")
            usage    # Display a usage synopsis.
            exit
        ;;
        "-a"|"--add" )
            # Add new subrepo
            # Check to see if a branch/tag is specified
            record=''
            tag=''
            for i in $@; do
                if [[ $i == '-b' ]] || [[ $i == '--branch' ]]; then
                    clone_branch='yes'
                    record='yes'
                elif [[ $record == 'yes' ]]; then
                    tag=$i
                    break
                elif [[ $record == '' ]]; then
                    clone_branch=''
                fi
            done
            # Check there isn't a directory/repo there already
            if [[ $# -ge 3 ]] && [[ $# -le 5 ]]; then
                repo_exist_check "empty" "$2"
                check_local_branch "$2"
                if [[ "$clone_branch" == "yes" ]]; then
                    clone_repo "$2" "$3" "$tag"
                else
                    clone_repo "$2" "$3"
                fi
                exit 0
            elif [[ $# -lt 3 ]]; then
                echo -e "$RED""Too few arguments provided.$EFC"
                echo
                echo "-a, --add     <reponame> <url>   Specify name of new repo"
                echo "-a, --add     <reponame> <url> -b <release>"
                echo
                exit 1
            elif [ ! $clone_branch ]; then
                echo -e "$RED""Too many arguments provided.$EFC"
                echo
                echo "-a, --add     <reponame> <url>   Specify name of new repo"
                echo "-a, --add     <reponame> <url> -b <release>"
                echo
                exit 1
            fi
            ;;
        "-v"|"--verify")
            if [[ $# -eq 2 ]]; then
                repo_exist_check "$2"
                validate_current_commit "$2" "verify"
            elif [[ $# -eq 3 ]] && [[ "$3" == "local" ]]; then
                repo_exist_check "$2"
                validate_current_commit "$2" "local"
            else
               echo
               echo "Only valid --verify options are:"
               echo "--verify <dir>"
               echo "--verify <dir> local"
               echo
            fi
            exit 0
        ;;
        "-u"|"--update" )
            # Upgrade subrepo
            repo_exist_check "$2"
            validate_current_commit "$2"
            check_available_updates "$raw_remote" "$selection" "$remote_sha1sum" "$2"
            check_local_branch "$2" "update"
            branchupdate "$2" "update" # update branch and then --verify
            exit 0
            ;;
        "-c"|"--check")
            # Check if update available
            repo_exist_check "$2"
            validate_current_commit "$2"
            check_available_updates "$raw_remote" "$selection" "$remote_sha1sum"
            exit 0
        ;;
        -?* )
            echo "Invalid option: $OPTARG" 1>&2
            usage
            exit 1
            ;;
        : )
            echo "Invalid option: -$OPTARG requires an argument" 1>&2
            usage
            exit 1
            ;;
        *)
            echo "Invalid option: -$OPTARG requires an argument" 1>&2
            usage
            exit 1
            ;;
    esac
    shift
done
