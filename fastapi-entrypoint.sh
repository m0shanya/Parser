#!/bin/sh

until cd /home/Parser/parser
do
    echo "Waiting for server volume..."
done

uvicorn main:app --host=0.0.0.0 --port=8000