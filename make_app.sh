#!/bin/bash
usage="first arg is the directory containing make_md5.sh and the upload directory" 
tar -czvf "$1"upload/autofitDist.app "$1"all/
"$1"make_md5.sh "$1"upload/autofitDist.app ./autofitDist.app.md5
echo "Done"
exit 0
