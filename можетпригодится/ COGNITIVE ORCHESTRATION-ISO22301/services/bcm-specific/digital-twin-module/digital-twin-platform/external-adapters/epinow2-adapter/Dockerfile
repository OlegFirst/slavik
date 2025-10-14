FROM rocker/r-ver:4.3.1
RUN R -e "install.packages(c('plumber','jsonlite','data.table'), repos='https://cloud.r-project.org')"
RUN R -e "install.packages('EpiNow2', repos='https://cloud.r-project.org')"
WORKDIR /app
COPY plumber.R /app/plumber.R
EXPOSE 7003
ENTRYPOINT ["R", "-e", "pr <- plumber::plumb('/app/plumber.R'); pr$run(host='0.0.0.0', port=7003)"]
