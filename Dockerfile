FROM jupyter/base-notebook:latest

RUN mamba install -c conda-forge plotly networkx pandas -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir ./pages
COPY /pages ./pages

COPY /data/bend_data.geojson ./data/bend_data.geojson
COPY /data/portalWebMaps_Test.csv ./data/portalWebMaps_Test.csv
COPY /data/solo_layers.csv ./data/solo_layers.csv

ENV PROJ_LIB='/opt/conda/share/proj'

USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

EXPOSE 8765

CMD ["solara", "run", "./pages", "--host=0.0.0.0"]
