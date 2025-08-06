#!/bin/bash

if [ "$(uname)" != "Windows" ] && ! command pip show uvloop &> /dev/null; then
    pip3 install uvloop
fi

uvicorn src:app --reload --proxy-headers --host 0.0.0.0 --port 8000