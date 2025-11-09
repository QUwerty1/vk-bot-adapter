FROM python:3.11-alpine

WORKDIR /app

RUN apk --no-cache add git

RUN git clone https://github.com/QUwerty1/vk-bot-adapter.git .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3000

ENV URL=""
ENV TOKEN=""
ENV BACKEND_URL=""

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]