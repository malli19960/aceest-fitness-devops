pipeline {
    agent any

    triggers {
        githubPush()
    }

    stages {
        stage('Build and Lint') {
            steps {
                sh 'docker build --target test -t aceest-fitness:test .'
            }
        }

        stage('Test') {
            steps {
                sh 'docker run --rm aceest-fitness:test'
            }
        }

        stage('Build Runtime Image') {
            steps {
                sh 'docker build --target runtime -t aceest-fitness:latest .'
            }
        }
    }
}
