#!bin/bash

PY_NAME=make_cocoa_jsai_data.py
DATA_DIR=data

mkdir -p ${DATA_DIR}

python3 $PY_NAME \
    --data_dir $DATA_DIR

rm ${DATA_DIR}/all_data.txt
rm ${DATA_DIR}/split_data.txt