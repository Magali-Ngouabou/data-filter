#!/bin/bash
FOLDER= C:/Users/mags1/OneDrive/Documents/CMU_REU/cache_dir/*
for file in $FOLDER
do 
    echo deleting  $file
    rm  $file
    echo deleted
done

