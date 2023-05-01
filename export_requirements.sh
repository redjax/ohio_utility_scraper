#!/bin/bash

prod_requirements="requirements.txt"
dev_requirements="requirements.dev.txt"
ci_requirements="requirements.ci.txt"

echo "Exporting production requirements"
pdm export -o requirements.txt --without-hashes

echo "Exporting dev requirements"
pdm export -d -o requirements.dev.txt --without-hashes

echo "Exporting ci requirements"
pdm export -dG ci -o requirements.ci.txt --without-hashes
