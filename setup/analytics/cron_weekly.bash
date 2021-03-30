#!/bin/bash

source source.bash

t=$(date "+%Y" -d "8 day ago")
t2=$(date "+%Y")

echo $t
./get.bash
./create_year.bash $t
if [ "$t2" != "$t" ]; then
    echo $t2
   ./create_year.bash $t2
fi
./push.bash
