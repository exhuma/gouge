FROM python:3

LABEL "com.github.actions.name"="Run pytest"
LABEL "com.github.actions.description"="Runs pytest against the repo"
LABEL "com.github.actions.icon"="snake"
LABEL "com.github.actions.color"="yellow"

ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
