#!/bin/sh

cd /u01/notebooks/TFM/DetectionComponentsAPI && python DetectAPI.py &

jupyter notebook --allow-root --notebook-dir=/u01/notebooks --ip='0.0.0.0' --port=8888 --no-browser --NotebookApp.token='' --NotebookApp.password=''

