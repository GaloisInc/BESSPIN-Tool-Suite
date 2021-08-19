#!/bin/bash

FILE=`dirname $0`/$1/dist_electron/$1-0.1.0-armv7l.AppImage
DEST=/home/pi/deploy/$1-0.1.0-armv7l.AppImage

if [ -z ${1+x} ]; then
    echo "Usage: deploy.sh <app-name>"
    exit
fi

if test -f "$FILE"; then
    echo "Deploying $FILE" to pi@$1
    scp $FILE pi@$1:$DEST
else
    echo "File does not exist: $FILE"
    echo "Did you run: npm run build:arm?"
fi

