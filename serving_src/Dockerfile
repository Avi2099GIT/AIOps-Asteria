FROM pytorch/torchserve:latest
WORKDIR /home/model-server
COPY . /home/model-server
RUN mkdir -p /home/model-server/model_store /home/model-server/config
COPY entrypoint.sh /home/model-server/entrypoint.sh
RUN chmod +x /home/model-server/entrypoint.sh
EXPOSE 8080 8081 8082
CMD ["/home/model-server/entrypoint.sh"]
