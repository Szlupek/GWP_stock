#!/bin/bash

rm -rfv raw_IF_data/*
rm -rfv IF_data/*
echo "Let's download some data"
scp -r micszl@student.fizyka.pw.edu.pl:~/Desktop/python/data/ .
echo "downloaded"
python3 handle_IF_data.py


