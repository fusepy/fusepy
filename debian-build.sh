#!/bin/bash

# see https://github.com/randrus/fusepy 

PACKAGE_NAME="python-fusepy"

BUILD_DESTINATION="build"

# verify release
release=$(lsb_release -cs)

python setup.py --command-packages=stdeb.command bdist_deb

echo mkdir -p $BUILD_DESTINATION/$release/$PACKAGE_NAME
mkdir -p $BUILD_DESTINATION/$release/$PACKAGE_NAME

for file in deb_dist/* 
do
    test -f $file && {
        echo cp $file $BUILD_DESTINATION/$release/$PACKAGE_NAME
        cp $file $BUILD_DESTINATION/$release/$PACKAGE_NAME
    }
done

# cleanup
rm -rf deb_dist
rm -rf *.egg-info
