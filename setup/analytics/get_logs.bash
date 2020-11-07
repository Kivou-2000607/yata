#!/bin/bash

rsync -azv --progress --delete-after login@host:~/admin/logs/http/2020/ logs/2020
