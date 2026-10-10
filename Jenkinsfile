pipeline {
    agent any

    triggers {
        githubPush()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Lint') {
            steps {
                sh 'python3 -m pip install -r requirements-dev.txt'
                sh 'python3 -m compileall -q app.py tests'
            }
        }

        stage('Test') {
            steps {
                sh 'python3 -m pytest -q'
            }
        }

        stage('Build Docker Images') {
            steps {
                sh 'docker build --target test -t aceest-fitness:test .'
                sh 'docker run --rm aceest-fitness:test'
                sh 'docker build --target runtime -t aceest-fitness:latest .'
            }
        }
    }
}
