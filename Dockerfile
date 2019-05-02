FROM ubuntu:18.10
MAINTAINER macomino <macomino@crcit.es>

# Updating Ubuntu packages
RUN apt-get update && apt-get upgrade -y

# Adding wget and bzip2
RUN apt-get install -y wget bzip2 net-tools libgl1-mesa-glx

# Anaconda installing
RUN wget https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh
RUN bash Anaconda3-2019.03-Linux-x86_64.sh -b
RUN rm Anaconda3-2019.03-Linux-x86_64.sh

# Set path to conda
ENV PATH /root/anaconda3/bin:$PATH

# Updating Anaconda packages
RUN conda update conda
RUN conda update anaconda
RUN conda update --all
RUN conda install -y -c conda-forge opencv
RUN conda-develop /u01/notebooks/models
RUN conda-develop /u01/notebooks/models/research/slim
RUN conda-develop /u01/notebooks/models/research/

# Install tensorflow
RUN pip install tensorflow

# Install object detection dependencies
ENV TZ=Europe/Minsk
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install -y protobuf-compiler python-pil python-lxml python-tk  git-core build-essential
RUN pip install --user Cython
RUN pip install --user contextlib2
RUN pip install --user matplotlib

# Create user folder
RUN mkdir /u01
RUN mkdir /u01/notebooks

WORKDIR /u01/notebooks

# Clone object detection tensorflow 
RUN git clone https://github.com/tensorflow/models.git

# Protobuf Compilation
RUN cd models/research && protoc object_detection/protos/*.proto --python_out=/u01/notebooks/models/research

# Install coco API metrics
RUN git clone https://github.com/cocodataset/cocoapi.git
RUN cd cocoapi/PythonAPI && make
RUN cp -r cocoapi/PythonAPI/pycocotools /u01/notebooks/models/research/

# Clone source code of the project
RUN git  clone  https://github.com/macomino/TFM.git
RUN wget http://download.tensorflow.org/models/object_detection/faster_rcnn_inception_v2_coco_2018_01_28.tar.gz
RUN tar -xvzf faster_rcnn_inception_v2_coco_2018_01_28.tar.gz
RUN cp -r faster_rcnn_inception_v2_coco_2018_01_28/model* /u01/notebooks/TFM/Configs/

# Jupyter listens port: 8888
EXPOSE 8888

# Run Jupytewr notebook as Docker main process
CMD ["jupyter", "notebook", "--allow-root", "--notebook-dir=/u01/notebooks/TFM", "--ip='0.0.0.0'", "--port=8888", "--no-browser", "--NotebookApp.token=''", "--NotebookApp.password=''"]
