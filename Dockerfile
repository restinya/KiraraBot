FROM python:3.6
#Create VENV
ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN sudo apt install ffmpeg
#ship it
ADD main.py /
CMD [ "python", "./main.py"]
