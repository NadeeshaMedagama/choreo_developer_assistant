# choreo-managed-auth-local-dev-proxy
Forward Proxy for Local Development with Choreo's Managed Authentication

## Introduction

This is reference proxy implementation for a proxy that can be used to access Choreo's Managed Authentication related endpoints when developing web applications locally.

## Run the proxy

```bash
npx @choreo/proxy -p <APP_PORT> -f <PROXY_PORT> -u <WEB_APP_URL>
```

| short option | long option    | description                                                                                                | required | default |
|--------------|----------------|------------------------------------------------------------------------------------------------------------|----------|---------|
| -p           | --localAppPort | Port on which the web app runs locally.                                                                    | true     | N/A     |
| -u           | --choreoAppUrl | The corresponding web app in choreo which the managed authentication related requests would be proxied to. | true     | N/A     |
| -f           | --proxyPort    | Port on which the proxy will listen.                                                                       | false    | 10000   |
| -l           | --logLevel     | Log level. One of ['info', 'debug']                                             | false    | info  |
