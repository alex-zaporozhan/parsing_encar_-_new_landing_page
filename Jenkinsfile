// ENCAR landing — CI без Docker Hub: pytest + E2E (uvicorn + Playwright).
// Агент: Linux с bash, Python 3.12+, Node 20+ (npm), curl, системные зависимости для Chromium (playwright install --with-deps).

pipeline {
  agent any

  options {
    timeout(time: 20, unit: 'MINUTES')
    timestamps()
  }

  environment {
    NEXT_PUBLIC_API_URL = 'http://127.0.0.1:8000'
    E2E_API_URL         = 'http://127.0.0.1:8000'
  }

  stages {
    stage('Backend') {
      steps {
        dir('backend') {
          sh 'python3 -m pip install -r requirements.txt'
          sh 'python3 -m pytest -q'
        }
      }
    }

    stage('E2E') {
      steps {
        sh '''
          set -e
          cd backend
          python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
          UVICORN_PID=$!
          cd ../frontend
          for i in $(seq 1 60); do
            if curl -sf http://127.0.0.1:8000/api/v1/health >/dev/null; then
              break
            fi
            sleep 1
          done
          curl -sf http://127.0.0.1:8000/api/v1/health
          npm ci
          npx playwright install --with-deps chromium
          npm run test:e2e
          kill $UVICORN_PID || true
        '''
      }
    }
  }

  post {
    failure {
      archiveArtifacts allowEmptyArchive: true, artifacts: 'frontend/playwright-report/**/*', fingerprint: true
    }
  }
}
