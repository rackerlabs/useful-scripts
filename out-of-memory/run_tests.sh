#!/bin/bash

function display_help() {
    echo "Usage: $0 [COMMAND]"
    echo "Commands:"
    echo "  pytest   - Run pytest to execute tests."
    echo "  black    - Run black for code formatting."
    echo "  isort    - Run isort to sort imports."
    echo "  help     - Display this help message."
}

function build_images(){
    echo "Building images. If this is the first time they're building, it might take a while.."
    docker compose build 2>&1 > /dev/null
}

if [ "$#" -ne 1 ]; then
    echo "Error: You must provide exactly one command."
    display_help
    exit 1
fi

COMMAND="$1"
case "$COMMAND" in
    pytest)
        # Broken into two parts.
        # First part: Run nearly all tests on a collection of python versions
        # Second part: Run system tests on different distrubutions

        # Part 1
        # Run tests on multiple python versions
        build_images
        python_versions=("python27" "python36" "python310")
        for version in "${python_versions[@]}"
        do
            echo "Running $COMMAND in $version"
            docker compose run --rm $version $COMMAND -v --ignore=tests/test_system.py --ignore=tests/test_validate_options.py
        done

        # Part 2
        # Run system specific tests
        distributions=("amazonlinux" "centos7" "osx")
        for distro in "${distributions[@]}"
        do
            echo "Running test_system in $distro"
            # OSX doesn't have a specific pytest binary, so we use the python module
            if [ "$distro" == "osx" ]; then
                COMMAND="python -m pytest"
            fi
            docker compose run --rm $distro $COMMAND -v tests/test_system.py tests/test_validate_options.py -p no:cacheprovider
        done
        ;;
    black|isort)
        build_images
        # If black or isort, we only need to run in one version of python
        version="python310"
        echo "Running $COMMAND in $version"
        docker compose run --rm $version $COMMAND /app
        ;;
    help)
        display_help
        ;;
    *)
        echo "Error: Invalid command '$COMMAND'"
        display_help
        exit 1
        ;;
esac

# Clean up
docker compose down 2>&1 > /dev/null
