from okwrtdsh/anaconda3:10.0-cudnn7

RUN apt-get update -qq \
 && apt-get install --no-install-recommends -y \
	graphviz \
 && apt-get clean \
 && apt-get install -y vim \
 && apt-get install ffmpeg libsm6 libxext6  -y \
 && rm -rf /var/lib/apt/lists/*

RUN conda upgrade -n base -c defaults --override-channels conda

RUN echo "completed!"
CMD ["python3"]