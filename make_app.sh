#!/bin/bash 
#rm ../upload/modsquare.app
tar -czf ../upload/modsquare.app all
./make_md5.sh ../upload/modsquare.app
echo "Done"
exit 0
