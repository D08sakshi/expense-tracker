# Expense Tracker DevSecOps Project

## Project Overview
This project demonstrates a complete DevSecOps pipeline using a Flask-based Expense Tracker application.

## Features
- Expense Management
- Docker Containerization
- CI/CD using GitHub Actions
- Vulnerability Scanning using Trivy
- AWS Deployment Ready

## Technologies Used
- Flask
- Docker
- GitHub Actions
- Trivy
- AWS EC2
- SQLite

## Workflow
1. Developer pushes code to GitHub
2. GitHub Actions triggers automatically
3. Docker image gets built
4. Trivy scans image vulnerabilities
5. Application becomes deployment-ready

## Security
Trivy is integrated to detect vulnerabilities in container images during the CI/CD pipeline.

## Deployment
The application can be deployed on AWS EC2 using Docker containers.