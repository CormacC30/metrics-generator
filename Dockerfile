FROM python:3.11-slim
WORKDIR /app
RUN pip install Flask
RUN pip install prometheus_client
COPY metrics-generator.py /app/metrics-generator.py
EXPOSE 8080
CMD ["python3", "metrics-generator.py"]
