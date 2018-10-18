#!/bin/bash

heroku logs --app torn-yata --tail | grep -e VIEW -e FUNCTION
