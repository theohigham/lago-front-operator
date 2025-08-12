# Lago Frontend Operator

A Juju charm for deploying and managing the Lago Frontend application on Kubernetes.

## Description

This operator deploys the Lago Frontend, a modern React application for billing and subscription management. The operator manages an OCI container image and provides configuration options for connecting to the Lago API backend.

## Usage

### Deploy the operator

```bash
juju deploy ./lago-front-k8s_*.charm \
  --resource oci-image=ghcr.io/theohigham/lago-front:latest \
  --config api-url=https://your-lago-api.example.com
```

### Required Configuration

- `api-url`: The URL of your Lago API backend

### Optional Configuration

- `app-env`: Application environment (development/staging/production)
- `lago-domain`: Custom domain for the application
- `lago-oauth-proxy-url`: OAuth proxy URL for authentication
- `lago-disable-signup`: Disable user registration
- `lago-disable-pdf-generation`: Disable PDF generation features
- `nango-public-key`: Nango integration public key
- `sentry-dsn`: Sentry DSN for error tracking

### Integrations

The operator requires an nginx-route integration for web traffic:

```bash
juju deploy nginx-ingress-integrator
juju integrate lago-front-k8s nginx-ingress-integrator
```

## Building

To build the charm:

```bash
charmcraft pack
```

## License

This operator is distributed under the Apache Software License, version 2.0.
