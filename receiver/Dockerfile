FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn[standard] aiofiles
COPY receiver.py ./receiver.py
EXPOSE 8001
CMD ["uvicorn", "receiver:app", "--host", "0.0.0.0", "--port", "8001"]
