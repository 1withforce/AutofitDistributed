#!/bin/bash 
tar -czf ../upload/autofitDist.app all
./make_md5.sh ../upload/autofitDist.app
echo "Done"
exit 0
