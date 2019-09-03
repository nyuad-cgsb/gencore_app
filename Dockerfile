FROM continuumio/miniconda3:4.6.14

#RUN conda config --add channels conda-forge
RUN conda install -c conda-forge -y jinja2 \
    conda \
    anaconda-client \
    apscheduler \
    ipython \
    pymongo \
    numpy

RUN echo "alias l='ls -lah'" >> ~/.bashrc

ENV PYTHONPATH "/pkgs:/pkgs/gencore_app"
