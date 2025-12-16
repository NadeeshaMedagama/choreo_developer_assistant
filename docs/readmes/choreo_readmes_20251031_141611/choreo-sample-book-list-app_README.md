# Choreo Sample - Book List Application

Welcome to the Choreo Book List Application sample! This application is designed to help you get familiar with the [Choreo](https://console.choreo.dev/) platform and its features.

## Overview

This application is a multi-user book list manager. It allows multiple users to maintain their own book lists independently. Each user can add, remove, and view books in their personal book list. It's built using the Choreo platform, showcasing its capabilities in building and deploying multi-user web applications.

## Directory Overview

| Directory               | Description                                                                                                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
|reading-list-front-end|React web frontend with auth handled through Choreo itself.|
|reading-list-front-end-with-managed-auth|React web frontend with auth handled through Asgardeo (Similar to using any third party IDP).
|reading-list-service|Backend microservice that handles the application logic|

> NOTE: Frontend and Frontend with managed auth showcase implementing the same frontend using a third party IDP for auth or using the Choreo built in auth implementation.

## Getting Started

To engage with these examples:

1. **Fork the Repository**: Begin by forking this repository to your GitHub account.
2. Log into [Choreo](https://console.choreo.dev/).
3. Create a mono repo project with React build preset for frontend components and NodeJS for backend component.

Please refer to the Choreo documentation [Deploy a Web Application that Consumes a Backend Service](https://wso2.com/choreo/docs/quick-start-guides/deploy-a-web-application-that-consumes-a-backend-service/) to learn more.

## Contribution & Feedback

We greatly value community insights:

- **Contribute**: Got a new example or an enhancement? We'd love to incorporate it.
- **Feedback**: Encounter issues or have suggestions? Please raise them under this repository's [issues section](https://github.com/wso2/choreo-sample-book-list-app/issues).
