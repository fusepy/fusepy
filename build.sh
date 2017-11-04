#!/bin/bash

# see https://github.com/randrus/fusepy 

PACKAGE_NAME="python-fusepy"

test -z "$CHECKED_OUT_PACKAGES_REPO" && {
    echo "env var CHECKED_OUT_PACKAGES_REPO not defined - must reference packages repo" >&2
    exit 1
}

# verify release
release=$(lsb_release -cs)

test "precise" = "$release" -o "lucid" = "$release" || {
    echo "$(lsb_release -ds) not supported" >&2
    exit 1
}

test "lucid" = $release && {
    POOLNAME=pool
}

test "precise" = $release && {
    POOLNAME=pool-precise
}

python setup.py --command-packages=stdeb.command bdist_deb

echo mkdir -p $CHECKED_OUT_PACKAGES_REPO/$POOLNAME/$PACKAGE_NAME
mkdir -p $CHECKED_OUT_PACKAGES_REPO/$POOLNAME/$PACKAGE_NAME

for file in deb_dist/* 
do
    test -f $file && {
        echo cp $file $CHECKED_OUT_PACKAGES_REPO/$POOLNAME/$PACKAGE_NAME
        cp $file $CHECKED_OUT_PACKAGES_REPO/$POOLNAME/$PACKAGE_NAME
    }
done

# cleanup
rm -rf deb_dist
rm -rf *.egg-info
