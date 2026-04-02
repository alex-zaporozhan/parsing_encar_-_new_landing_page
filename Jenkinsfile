// ENCAR landing — тесты + публикация образов в GitHub Container Registry (ghcr.io), без Docker Hub.
// Агент: Linux, Docker CLI + доступ к daemon, Python 3.12+, Node 22+, curl.
// Секреты Jenkins: credentialsId "ghcr-pat" — Username with password (user = GitHub login, password = PAT с write:packages).

pipeline {
  agent any

  options {
    timeout(time: 60, unit: 'MINUTES')
    timestamps()
  }

  parameters {
    string(
      name: 'IMAGE_TAG',
      defaultValue: 'latest',
      trim: true,
      description: 'Тег образов на ghcr.io (например latest или v1.0.0)',
    )
    string(
      name: 'NEXT_PUBLIC_API_URL',
      defaultValue: 'http://127.0.0.1:8000',
      trim: true,
      description: 'Публичный URL API для сборки Next.js (на прод-релиз укажите https://api.ваш-домен)',
    )
    string(
      name: 'GHCR_OWNER',
      defaultValue: 'alex-zaporozhan',
      trim: true,
      description: 'Владелец пакетов на GitHub (организация или пользователь)',
    )
  }

  environment {
    E2E_API_URL         = 'http://127.0.0.1:8000'
    NEXT_PUBLIC_API_URL = "${params.NEXT_PUBLIC_API_URL}"
    DOCKER_REGISTRY     = 'ghcr.io'
    API_IMAGE           = "${DOCKER_REGISTRY}/${params.GHCR_OWNER}/encar-landing-api"
    WEB_IMAGE           = "${DOCKER_REGISTRY}/${params.GHCR_OWNER}/encar-landing-web"
    IMAGE_TAG_PARAM     = "${params.IMAGE_TAG}"
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
      environment {
        NEXT_PUBLIC_API_URL = 'http://127.0.0.1:8000'
      }
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

    stage('Docker build and push to GHCR') {
      when {
        anyOf {
          branch 'main'
          branch 'master'
        }
      }
      steps {
        withCredentials([
          usernamePassword(
            credentialsId: 'ghcr-pat',
            usernameVariable: 'GHCR_USER',
            passwordVariable: 'GHCR_TOKEN',
          ),
        ]) {
          sh '''
            set -e
            echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
            docker build -t "${API_IMAGE}:${IMAGE_TAG_PARAM}" ./backend
            docker build \
              --build-arg "NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}" \
              -t "${WEB_IMAGE}:${IMAGE_TAG_PARAM}" \
              ./frontend
            docker push "${API_IMAGE}:${IMAGE_TAG_PARAM}"
            docker push "${WEB_IMAGE}:${IMAGE_TAG_PARAM}"
          '''
        }
      }
    }
  }

  post {
    failure {
      archiveArtifacts allowEmptyArchive: true, artifacts: 'frontend/playwright-report/**/*', fingerprint: true
    }
  }
}
