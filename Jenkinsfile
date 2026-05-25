pipeline {
    agent none
    environment {
        SERVICE = 'exchange'
        NAME = "youcancallmegus/${env.SERVICE}"
    }
    stages {
        stage('Install Dependencies') {
            agent {
                docker { image 'python:3.11-slim' }
            }
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Test') {
            agent {
                docker { image 'python:3.11-slim' }
            }
            steps {
                sh 'pytest tests/ -v'
            }
        }
        stage('Build & Push Image') {
            agent any  // usa o Jenkins direto, que tem Docker
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credential',
                    usernameVariable: 'USERNAME',
                    passwordVariable: 'TOKEN')])
                {
                    sh "docker login -u $USERNAME -p $TOKEN"
                    sh "docker buildx create --use --platform=linux/arm64,linux/amd64 --node multi-platform-builder-${env.SERVICE} --name multi-platform-builder-${env.SERVICE}"
                    sh "docker buildx build --platform=linux/arm64,linux/amd64 --push --tag ${env.NAME}:latest --tag ${env.NAME}:${env.BUILD_ID} -f Dockerfile ."
                    sh "docker buildx rm --force multi-platform-builder-${env.SERVICE}"
                }
            }
        }
    }
}