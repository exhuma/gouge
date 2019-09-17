FROM python:3

LABEL "com.github.actions.name"="Setup Python 3 Environment"
LABEL "com.github.actions.description"="Creates a new Python 3 environment for this project"
LABEL "com.github.actions.icon"="snake"
LABEL "com.github.actions.color"="yellow"

ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
