FROM python:3.10-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and use app directory matching project name
WORKDIR /app/Calculadora

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install streamlit

# Copy entire project into Calculadora subdirectory
COPY . .

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "Home.py"]