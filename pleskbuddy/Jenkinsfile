pipeline {
    agent any
    triggers {
        pollSCM('')
    }
    stages {
        stage('Pleskbuddy') {
            parallel {
                stage('Pylint') {
                    agent {
                        docker {
                            image 'dsgnr/base-python2.7-alpine-docker'
                        }
                    }
                    stages {
                        stage('Setup') {
                            steps {
                                echo "Installing requirements..."
                                sh '''pip install -q -U pip
                                    pip install -r requirements.txt'''
                            }
                        }
                        stage('Pylint') {
                            steps {
                                echo "Running Pylint..."
                                sh 'pylint --rcfile=.pylintrc *.py > pylint.log'
                            }
                        }
                    }
                    post {
                        always {
                            recordIssues enabledForFailure: true, tool: pyLint(id: 'pleskbuddy-pylint', name: 'Pleskbuddy PyLint', pattern: 'pylint.log', reportEncoding: 'UTF-8')
                        }
                        failure {
                            sh 'cat pylint.log'
                        }
                    }
                }
                stage('Pycodestyle') {
                    agent {
                        docker {
                            image 'dsgnr/base-python2.7-alpine-docker'
                        }
                    }
                    stages {
                        stage('Setup') {
                            steps {
                                echo "Installing requirements..."
                                sh '''pip install -q -U pip
                                    pip install -r requirements.txt'''
                            }
                        }
                        stage('Pycodestyle') {
                            steps {
                                echo "Running Pycodestyle..."
                                sh 'pycodestyle --config=setup.cfg *.py > pycodestyle.log'
                            }
                        }
                    }
                    post {
                        always {
                            recordIssues enabledForFailure: true, tool: pep8(id: 'pleskbuddy-pycodestyle', name: 'Pleskbuddy Pycodestyle', pattern: 'pycodestyle.log', reportEncoding: 'UTF-8')
                        }
                        failure {
                            sh 'cat pycodestyle.log'
                        }
                    }
                }
            }
        }

    }
    post {
        always {
            deleteDir()
        }
    }
}
