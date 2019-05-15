FROM ubuntu:18.10
MAINTAINER macomino <macomino@crcit.es>

# Updating Ubuntu packages
RUN apt-get update && apt-get upgrade -y

# Adding wget and bzip2
RUN apt-get install -y wget bzip2 net-tools libgl1-mesa-glx lsb-release

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

# Install pygame
RUN pip install pygame

# Create user folder
RUN mkdir /u01
RUN mkdir /u01/notebooks

WORKDIR /u01/notebooks

# Clone object detection tensorflow 
RUN git clone  https://github.com/tensorflow/models.git

# Protobuf Compilation
RUN cd models/research && protoc object_detection/protos/*.proto --python_out=/u01/notebooks/models/research

# Install coco API metrics
RUN git clone https://github.com/cocodataset/cocoapi.git
RUN cd cocoapi/PythonAPI && make
RUN cp -r cocoapi/PythonAPI/pycocotools /u01/notebooks/models/research/

# Clone source code of the project
RUN wget http://download.tensorflow.org/models/object_detection/faster_rcnn_inception_v2_coco_2018_01_28.tar.gz

RUN git  clone  https://github.com/macomino/TFM.git 
COPY ./DetectionComponentsAPI/frozen_inference_graph.pb ./TFM/DetectionComponentsAPI
RUN tar -xvzf faster_rcnn_inception_v2_coco_2018_01_28.tar.gz
RUN cp -r faster_rcnn_inception_v2_coco_2018_01_28/model* /u01/notebooks/TFM/Configs/

#Install Google Cloud SDK

RUN echo "deb http://packages.cloud.google.com/apt cloud-sdk-$(lsb_release -c -s) main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update && apt-get install -y google-cloud-sdk

# Jupyter listens port: 8888
EXPOSE 8888

# Tensorboard listens port: 6006
EXPOSE 6006

#Clean temporal files
RUN rm -rf cocoapi
RUN rm -rf faster_rcnn_inception_v2_coco_2018_01_28
RUN rm faster_rcnn_inception_v2_coco_2018_01_28.tar.gz

#Create folder to training model
RUN mkdir trainingmodel

RUN chmod +x /u01/notebooks/TFM/start.sh

# Run Jupytewr notebook as Docker main process
CMD ["/u01/notebooks/TFM/start.sh"]
