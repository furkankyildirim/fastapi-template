#!/bin/bash

uvicorn src:app --reload --proxy-headers --host 0.0.0.0 --port 8000