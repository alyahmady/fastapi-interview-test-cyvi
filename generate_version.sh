#!/bin/bash

cd "$(dirname "$0")" || exit

file_name="function.zip"
directory="versions"
counter=1

mkdir -p "$directory"

while [[ -e "./$directory/$file_name" ]]; do
  file_name="function$counter.zip"
  ((counter++))
done

echo "Generating new version ZIP package: $file_name"

cd ./linuxvenv/lib/python3.11/site-packages/ || exit
zip -r9 "../../../../$directory/$file_name" .
cd ../../../../
zip -g "./$directory/$file_name" -r app migrations alembic.ini

echo "Done"
