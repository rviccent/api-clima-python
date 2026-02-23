# 🌤 API de Clima com Python + PostgreSQL

Projeto backend completo que:

- Consome API pública de clima
- Salva dados automaticamente no PostgreSQL
- Expõe API REST com Flask
- Possui dashboard web
- Possui job agendado para coleta automática

---

## 🚀 Tecnologias

- Python 3.13
- Flask
- PostgreSQL
- psycopg2
- requests
- matplotlib
- Task Scheduler (Windows)

---

## 📊 Endpoints

### Health check
GET /health

### Últimos registros
GET /clima/ultimos?n=5

### Resumo estatístico
GET /clima/resumo

### Dashboard
GET /

---

## 🛠 Como rodar

1. Clonar o repositório
2. Criar ambiente virtual
3. Instalar dependências: pip install -r requirements.txt
4. Configurar banco PostgreSQL
5. Rodar: python api.py
---

## 📌 Autor

Ryan Vicente

