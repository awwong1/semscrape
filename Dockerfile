# Prepare django app to be multi-staged for Server/Web-Client separation
FROM python:3.7 as semscrape
ENV PYTHONUNBUFFERED=1

# create a non-root user for running the app
ARG UNAME=semscrape
ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID -o $UNAME
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $UNAME
RUN mkdir /code
RUN chown -R $UID:$GID /code
USER $UNAME
ENV PATH="/home/${UNAME}/.local/bin:${PATH}"

WORKDIR /code
COPY requirements.txt /code/
RUN pip install -U pip
RUN pip install -r requirements.txt

# Initialize the NLTK punkt sentence tokenizer
RUN python3 -c "import nltk; nltk.download('punkt')"

# Initialize the transformer model pre-trained model
RUN python3 -W ignore -c "from transformers import pipeline;\
nlp = pipeline(\
    'sentiment-analysis',\
    model='distilbert-base-uncased-finetuned-sst-2-english'\
);\
np_str=['Hi!', 'I\'m Alex.', 'Please hire me!'];\
print(*list(zip(np_str, nlp(*np_str))), sep='\n')"

COPY . /code/
