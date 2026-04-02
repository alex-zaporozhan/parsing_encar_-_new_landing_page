.PHONY: fetch api dev-frontend install-backend install-frontend qa-api qa-e2e

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

fetch:
	cd backend && python -m app.jobs.fetch_encar

api:
	cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

dev-frontend:
	cd frontend && npm run dev

qa-api:
	cd backend && python -m pytest -q

# Требует API на :8000 (make api в другом терминале). POSIX: переменная перед командой.
qa-e2e:
	cd frontend && NEXT_PUBLIC_API_URL=http://127.0.0.1:8000 npm run test:e2e
