pipeline {
    agent any

    triggers {
        githubPush()
    }

    options {
        disableConcurrentBuilds()
        timestamps()
    }

    parameters {
        choice(
            name: 'DEPLOYMENT_STRATEGY',
            choices: ['rolling', 'blue-green', 'canary'],
            description: 'Kubernetes deployment strategy for main-branch builds.'
        )
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    def revision = env.GIT_COMMIT ?: sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()
                    env.IMAGE_TAG = "${env.BUILD_NUMBER}-${revision.take(12)}"
                }
            }
        }

        stage('Build and Test') {
            steps {
                sh 'docker build --target test -t aceest-fitness:test .'
                sh 'docker run --rm aceest-fitness:test'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh "\"${scannerHome}/bin/sonar-scanner\""
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build and Push Image') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set -eu
                        export IMAGE_REPOSITORY="${DOCKERHUB_USERNAME}/aceest-fitness"
                        printf '%s' "$DOCKERHUB_TOKEN" | docker login \
                          --username "$DOCKERHUB_USERNAME" --password-stdin
                        docker build --target runtime \
                          -t "${IMAGE_REPOSITORY}:${IMAGE_TAG}" .
                        docker push "${IMAGE_REPOSITORY}:${IMAGE_TAG}"
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    ),
                    file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')
                ]) {
                    script {
                        env.IMAGE_FULL = "${env.DOCKERHUB_USERNAME}/aceest-fitness:${env.IMAGE_TAG}"
                        if (params.DEPLOYMENT_STRATEGY == 'rolling') {
                            sh '''
                                set -eu
                                sed "s|__IMAGE__|${IMAGE_FULL}|g" \
                                  k8s/rolling/deployment.yaml | kubectl apply -f -
                                kubectl apply -f k8s/rolling/service.yaml
                                if ! kubectl rollout status deployment/aceest-fitness \
                                  --timeout=180s; then
                                  echo "Rolling update failed; reverting the Deployment." >&2
                                  kubectl rollout undo deployment/aceest-fitness
                                  exit 1
                                fi
                                kubectl port-forward service/aceest-fitness-rolling 18080:80 \
                                  >/tmp/aceest-rolling.log 2>&1 &
                                PF_PID=$!
                                trap 'kill "$PF_PID" >/dev/null 2>&1 || true' EXIT
                                for attempt in $(seq 1 30); do
                                  if curl --fail --silent --show-error \
                                    http://127.0.0.1:18080/health >/dev/null; then
                                    curl --fail --silent --show-error \
                                      http://127.0.0.1:18080/health
                                    trap - EXIT
                                    kill "$PF_PID" >/dev/null 2>&1 || true
                                    exit 0
                                  fi
                                  sleep 2
                                done
                                echo "Rolling update smoke test failed; reverting the Deployment." >&2
                                trap - EXIT
                                kill "$PF_PID" >/dev/null 2>&1 || true
                                kubectl rollout undo deployment/aceest-fitness
                                kubectl rollout status deployment/aceest-fitness --timeout=180s
                                exit 1
                            '''
                        } else if (params.DEPLOYMENT_STRATEGY == 'blue-green') {
                            sh '''
                                set -eu
                                if ! kubectl get service aceest-fitness-blue-green >/dev/null 2>&1; then
                                  sed "s|__IMAGE__|${IMAGE_FULL}|g" \
                                    k8s/blue-green/deployment-blue.yaml | kubectl apply -f -
                                  kubectl apply -f k8s/blue-green/service.yaml
                                  kubectl rollout status deployment/aceest-blue --timeout=180s
                                fi

                                ACTIVE=$(kubectl get service aceest-fitness-blue-green \
                                  -o jsonpath='{.spec.selector.slot}')
                                if [ "$ACTIVE" = "blue" ]; then
                                  TARGET=green
                                elif [ "$ACTIVE" = "green" ]; then
                                  TARGET=blue
                                else
                                  echo "Unexpected active blue/green slot: $ACTIVE" >&2
                                  exit 1
                                fi

                                sed "s|__IMAGE__|${IMAGE_FULL}|g" \
                                  "k8s/blue-green/deployment-${TARGET}.yaml" \
                                  | kubectl apply -f -
                                kubectl rollout status "deployment/aceest-${TARGET}" \
                                  --timeout=180s
                                kubectl port-forward \
                                  "deployment/aceest-${TARGET}" 18081:5000 \
                                  >/tmp/aceest-blue-green.log 2>&1 &
                                PF_PID=$!
                                trap 'kill "$PF_PID" >/dev/null 2>&1 || true' EXIT
                                READY=false
                                for attempt in $(seq 1 30); do
                                  if curl --fail --silent --show-error \
                                    http://127.0.0.1:18081/health >/dev/null; then
                                    READY=true
                                    break
                                  fi
                                  sleep 2
                                done
                                if [ "$READY" != "true" ]; then
                                  echo "Blue/green target smoke test failed; keeping $ACTIVE active." >&2
                                  trap - EXIT
                                  kill "$PF_PID" >/dev/null 2>&1 || true
                                  kubectl scale "deployment/aceest-${TARGET}" --replicas=0
                                  exit 1
                                fi
                                trap - EXIT
                                kill "$PF_PID" >/dev/null 2>&1 || true
                                curl --fail --silent --show-error \
                                  http://127.0.0.1:18081/health
                                kubectl patch service aceest-fitness-blue-green --type=merge \
                                  -p "{\"spec\":{\"selector\":{\"app\":\"aceest-fitness-blue-green\",\"slot\":\"${TARGET}\"}}}"
                                kubectl get endpoints aceest-fitness-blue-green
                            '''
                        } else {
                            sh '''
                                set -eu
                                if ! kubectl get deployment aceest-stable >/dev/null 2>&1; then
                                  sed "s|__IMAGE__|${IMAGE_FULL}|g" \
                                    k8s/canary/deployment-stable.yaml | kubectl apply -f -
                                  kubectl apply -f k8s/canary/service.yaml
                                  kubectl rollout status deployment/aceest-stable \
                                    --timeout=180s
                                fi

                                sed "s|__IMAGE__|${IMAGE_FULL}|g" \
                                  k8s/canary/deployment-canary.yaml | kubectl apply -f -
                                if ! kubectl rollout status deployment/aceest-canary \
                                  --timeout=180s; then
                                  echo "Canary failed; removing canary traffic." >&2
                                  kubectl scale deployment/aceest-canary --replicas=0
                                  exit 1
                                fi
                                kubectl port-forward deployment/aceest-canary 18082:5000 \
                                  >/tmp/aceest-canary.log 2>&1 &
                                PF_PID=$!
                                trap 'kill "$PF_PID" >/dev/null 2>&1 || true' EXIT
                                for attempt in $(seq 1 30); do
                                  if curl --fail --silent --show-error \
                                    http://127.0.0.1:18082/health >/dev/null; then
                                    curl --fail --silent --show-error \
                                      http://127.0.0.1:18082/health
                                    break
                                  fi
                                  if [ "$attempt" = "30" ]; then
                                    echo "Canary smoke test failed; removing canary traffic." >&2
                                    trap - EXIT
                                    kill "$PF_PID" >/dev/null 2>&1 || true
                                    kubectl scale deployment/aceest-canary --replicas=0
                                    exit 1
                                  fi
                                  sleep 2
                                done
                                trap - EXIT
                                kill "$PF_PID" >/dev/null 2>&1 || true

                                kubectl set image deployment/aceest-stable \
                                  app="${IMAGE_FULL}"
                                if ! kubectl rollout status deployment/aceest-stable \
                                  --timeout=180s; then
                                  echo "Stable promotion failed; reverting the Deployment." >&2
                                  kubectl rollout undo deployment/aceest-stable
                                  kubectl scale deployment/aceest-canary --replicas=0
                                  exit 1
                                fi
                                kubectl port-forward deployment/aceest-stable 18083:5000 \
                                  >/tmp/aceest-stable.log 2>&1 &
                                PF_PID=$!
                                trap 'kill "$PF_PID" >/dev/null 2>&1 || true' EXIT
                                for attempt in $(seq 1 30); do
                                  if curl --fail --silent --show-error \
                                    http://127.0.0.1:18083/health >/dev/null; then
                                    curl --fail --silent --show-error \
                                      http://127.0.0.1:18083/health
                                    break
                                  fi
                                  if [ "$attempt" = "30" ]; then
                                    echo "Promoted stable smoke test failed; rolling back." >&2
                                    trap - EXIT
                                    kill "$PF_PID" >/dev/null 2>&1 || true
                                    kubectl rollout undo deployment/aceest-stable
                                    kubectl rollout status deployment/aceest-stable --timeout=180s
                                    kubectl scale deployment/aceest-canary --replicas=0
                                    exit 1
                                  fi
                                  sleep 2
                                done
                                trap - EXIT
                                kill "$PF_PID" >/dev/null 2>&1 || true
                                kubectl get endpoints aceest-fitness-canary
                                kubectl scale deployment/aceest-canary --replicas=0
                            '''
                        }
                    }
                }
            }
        }
    }
}
