#!/bin/bash

source source.bash

t=$(date "+%Y %m" -d "4 day ago")
t2=$(date "+%Y %m")

echo $t
./get.bash
./create_month.bash $t
if [ "$t2" != "$t" ]; then
    echo $t2
   ./create_month.bash $t2
fi
./push.bash
