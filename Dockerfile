FROM pytorch/torchserve:latest
WORKDIR /home/model-server
COPY . /home/model-server
RUN mkdir -p /home/model-server/model_store /home/model-server/config
COPY entrypoint.sh /home/model-server/entrypoint.sh

# Switch to root for chmod
USER root
RUN chmod +x /home/model-server/entrypoint.sh

# Switch back to model-server user for safety
USER model-server

EXPOSE 8080 8081 8082
CMD ["/home/model-server/entrypoint.sh"]
