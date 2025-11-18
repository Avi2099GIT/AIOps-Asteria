FROM pytorch/torchserve:0.12.0-cpu

USER root

RUN mkdir -p /home/model-server/model_store
RUN mkdir -p /home/model-server/config

COPY ../../serving/model-store/*.mar /home/model-server/model_store/

COPY entrypoint.sh /home/model-server/entrypoint.sh
RUN chmod +x /home/model-server/entrypoint.sh

EXPOSE 8080 8081 8082

ENTRYPOINT ["/home/model-server/entrypoint.sh"]
