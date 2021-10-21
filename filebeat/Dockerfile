FROM alpine:3.12

ARG ELK_VERSION

RUN apk add --no-cache libc6-compat curl jq

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

ENTRYPOINT ["entrypoint"]
CMD ["-h"]