FROM continuumio/miniconda3:4.6.14

#RUN conda config --add channels conda-forge
RUN conda install -c conda-forge -y conda anaconda-client apscheduler ipython numpy

RUN echo "alias l='ls -lah'" >> ~/.bashrc

ENV PYTHON_PATH "/pkgs:/pkgs/gencore_app"
