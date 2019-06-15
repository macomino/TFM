FROM ubuntu:18.10
MAINTAINER macomino <macomino@crcit.es>

# Create user folder
RUN mkdir /u01
RUN mkdir /u01/notebooks

#Create folder to training model
RUN mkdir /u01/notebooks/trainingmodel

WORKDIR /u01/notebooks

# Updating Ubuntu packages
RUN apt-get update 
#&& apt-get upgrade -y

ENV TZ=Europe/Minsk
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Adding wget and bzip2
RUN apt-get install -y wget bzip2 net-tools libgl1-mesa-glx lsb-release protobuf-compiler python-pil python-lxml python-tk  git-core build-essential

# Anaconda installing
RUN wget https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh && bash Anaconda3-2019.03-Linux-x86_64.sh -b && rm Anaconda3-2019.03-Linux-x86_64.sh

# Set path to conda
ENV PATH /root/anaconda3/bin:$PATH

# Updating Anaconda packages
#RUN conda update conda
#RUN conda update anaconda
#RUN conda update --all
RUN conda install -y -c conda-forge opencv gcc_linux-64 gxx_linux-64
RUN conda-develop /u01/notebooks/models
RUN conda-develop /u01/notebooks/models/research/slim
RUN conda-develop /u01/notebooks/models/research/

# Install python dependencies
RUN pip install tensorflow Cython contextlib2 matplotlib pygame



# Clone object detection tensorflow 
RUN git clone  https://github.com/tensorflow/models.git && rm -rf models/.git

# Protobuf Compilation
RUN cd models/research && protoc object_detection/protos/*.proto --python_out=/u01/notebooks/models/research

# Install coco API metrics
RUN git clone  https://github.com/cocodataset/cocoapi.git && cd cocoapi/PythonAPI && make && cp -r pycocotools /u01/notebooks/models/research/ && rm -rf ../../cocoapi


# Clone source code of the project
RUN wget http://download.tensorflow.org/models/object_detection/faster_rcnn_inception_v2_coco_2018_01_28.tar.gz


#Install Google Cloud SDK
RUN echo "deb http://packages.cloud.google.com/apt cloud-sdk-$(lsb_release -c -s) main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && curl -sL https://deb.nodesource.com/setup_10.x | bash -

RUN apt-get update && apt-get install -y google-cloud-sdk nodejs && npm install -g @angular/cli



RUN git clone https://github.com/macomino/TFM.git 
RUN cd /u01/notebooks/TFM/Frontend && npm install
COPY ./DetectionComponentsAPI/frozen_inference_graph.pb ./TFM/DetectionComponentsAPI
RUN tar -xvzf faster_rcnn_inception_v2_coco_2018_01_28.tar.gz
RUN cp -r faster_rcnn_inception_v2_coco_2018_01_28/model* /u01/notebooks/TFM/Configs/


# Jupyter listens port
EXPOSE 8888

# Tensorboard listens port
EXPOSE 6006

# Frontend listen port
EXPOSE 4200

# Backend listent port
EXPOSE 5050

#Clean temporal files

RUN rm -rf faster_rcnn_inception_v2_coco_2018_01_28
RUN rm faster_rcnn_inception_v2_coco_2018_01_28.tar.gz



RUN chmod +x /u01/notebooks/TFM/start.sh

# Run start script as Docker main process
CMD ["/u01/notebooks/TFM/start.sh"]
