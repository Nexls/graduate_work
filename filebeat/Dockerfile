FROM alpine:3.12

ARG ELK_VERSION

RUN apk add --no-cache libc6-compat curl jq


#ENV DOCKERIZE_VERSION v0.6.1
#RUN apt-get update && apt-get install -y wget
#RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-#alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
#    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
#    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz
    
    
RUN \
  cd /tmp \
  && curl -O -J -L https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-oss-${ELK_VERSION}-linux-x86_64.tar.gz \
  && tar xzvf filebeat-oss-${ELK_VERSION}-linux-x86_64.tar.gz \
  && mv filebeat-${ELK_VERSION}-linux-x86_64 /usr/share/filebeat \
  && mkdir /usr/share/filebeat/logs /usr/share/filebeat/data \
  && rm /tmp/*

ENV PATH $PATH:/usr/share/filebeat

COPY config /usr/share/filebeat

COPY entrypoint.sh /usr/local/bin/entrypoint
RUN chmod +x /usr/local/bin/entrypoint

WORKDIR /usr/share/filebeat

#CMD dockerize -wait tcp://kibana:5601 -timeout 90s \
#    && dockerize -wait tcp://elasticsearch:9200 -timeout 90s

ENTRYPOINT ["entrypoint"]
CMD ["-h"]
