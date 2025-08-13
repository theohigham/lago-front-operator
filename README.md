# Lago Frontend Operator

A Juju charm for deploying and managing the Lago Frontend application on Kubernetes.

## Description

This operator deploys the Lago Frontend, a modern React application for billing and subscription management. The operator follows the operator pattern by managing an OCI container image and provides comprehensive configuration options for connecting to the Lago API backend.

## Prerequisites

- **Juju 3.0+** with a Kubernetes model
- **Kubernetes cluster** with RBAC enabled
- **Lago API backend** deployed and accessible
- **OCI image** available in a container registry

## Quick Start

### Basic Deployment

```bash
# Deploy with minimal configuration.
juju deploy ./lago-front-k8s_*.charm \
  --resource oci-image=ghcr.io/theohigham/lago-front:latest \
  --config api-url=https://your-lago-api.example.com
```

### Local Development Setup

```bash
# For local development with Lago running locally.
juju deploy ./lago-front-k8s_*.charm \
  --resource oci-image=ghcr.io/theohigham/lago-front:latest \
  --config api-url=http://192.168.1.100:3000 \
  --config app-env=development
```

## Configuration Reference

### Required Configuration

| Option | Type | Description |
|--------|------|-------------|
| `api-url` | string | **Required.** The URL of your Lago API backend. Must be accessible from the Kubernetes cluster. |

**Example:**
```bash
juju config lago-front-k8s api-url=https://api.lago.example.com
```

### Application Environment

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `app-env` | string | `production` | Application environment setting. Controls various frontend behaviors and UI elements. |

**Valid values:** `development`, `staging`, `production`

**Examples:**
```bash
# Development mode (shows debug info, different favicon).
juju config lago-front-k8s app-env=development

# Production mode (optimized, minimal logging).
juju config lago-front-k8s app-env=production
```

### Domain and URL Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `lago-domain` | string | `""` | Custom domain for the application. If set, API URL will be automatically constructed as `https://{lago-domain}/api`. |
| `lago-oauth-proxy-url` | string | `""` | OAuth proxy URL for authentication integration. Used for enterprise SSO setups. |

**Examples:**
```bash
# Using custom domain (will set API URL to https://billing.company.com/api).
juju config lago-front-k8s lago-domain=billing.company.com

# Using OAuth proxy for SSO.
juju config lago-front-k8s lago-oauth-proxy-url=https://auth.company.com/oauth
```

### Feature Flags

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `lago-disable-signup` | boolean | `false` | Disable user registration functionality in the frontend. Useful for enterprise deployments. |
| `lago-disable-pdf-generation` | boolean | `false` | Disable PDF generation features in the frontend. |

**Examples:**
```bash
# Disable self-registration for enterprise use.
juju config lago-front-k8s lago-disable-signup=true

# Disable PDF features if not needed.
juju config lago-front-k8s lago-disable-pdf-generation=true
```

### Integrations

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `nango-public-key` | string | `""` | Public key for Nango integration service. Used for third-party API integrations. |
| `sentry-dsn` | string | `""` | Sentry DSN for error tracking and monitoring. Recommended for production deployments. |

**Examples:**
```bash
# Enable error tracking.
juju config lago-front-k8s sentry-dsn=https://your-sentry-dsn@sentry.io/project

# Enable Nango integrations.
juju config lago-front-k8s nango-public-key=nango_pk_your-public-key
```

## Deployment Scenarios

### Scenario 1: Production Deployment with Load Balancer

```bash
# Deploy the charm.
juju deploy ./lago-front-k8s_*.charm \
  --resource oci-image=ghcr.io/theohigham/lago-front:latest \
  --config api-url=https://api.lago.company.com \
  --config app-env=production \
  --config lago-disable-signup=true \
  --config sentry-dsn=https://your-sentry-dsn@sentry.io/project

# Integrate with nginx ingress for external access.
juju deploy nginx-ingress-integrator
juju integrate lago-front-k8s nginx-ingress-integrator

# Configure TLS and custom domain.
juju config nginx-ingress-integrator \
  service-hostname=billing.company.com \
  tls-secret-name=lago-tls
```

### Scenario 2: Development Environment

```bash
# Deploy for development.
juju deploy ./lago-front-k8s_*.charm \
  --resource oci-image=ghcr.io/theohigham/lago-front:latest \
  --config api-url=http://localhost:3000 \
  --config app-env=development \
  --config lago-disable-signup=false

# Port forward for local access.
kubectl port-forward -n your-model svc/lago-front-k8s 8080:80
```

### Scenario 3: Enterprise SSO Integration

```bash
# Deploy with OAuth proxy integration.
juju deploy ./lago-front-k8s_*.charm \
  --resource oci-image=ghcr.io/theohigham/lago-front:latest \
  --config api-url=https://api.lago.company.com \
  --config lago-domain=billing.company.com \
  --config lago-oauth-proxy-url=https://auth.company.com/oauth \
  --config lago-disable-signup=true
```

## Networking and Access

### Internal Access

The charm creates a Kubernetes service that exposes the frontend on port 80. The service can be accessed internally using:

```bash
# Get service information.
juju status lago-front-k8s

# Access via port forwarding.
kubectl port-forward -n your-model svc/lago-front-k8s 8080:80
```

### External Access

For external access, integrate with nginx-ingress-integrator:

```bash
juju deploy nginx-ingress-integrator
juju integrate lago-front-k8s nginx-ingress-integrator
juju config nginx-ingress-integrator service-hostname=your-domain.com
```

## Monitoring and Observability

### Health Checks

The charm includes built-in health checks:
- **HTTP health check** on port 80 every 30 seconds
- **Pebble service monitoring** for the frontend process

### Logging

View application logs:

```bash
# Charm logs.
juju debug-log --include=lago-front-k8s

# Application logs.
kubectl logs -n your-model -l app.kubernetes.io/name=lago-front-k8s -c lago-frontend
```

### Error Tracking

Configure Sentry for production error tracking:

```bash
juju config lago-front-k8s sentry-dsn=https://your-sentry-dsn@sentry.io/project
```

## Security Considerations

### OCI Image Security

- Use specific image tags rather than `latest` in production
- Ensure your OCI registry has proper access controls
- Regularly update the base image for security patches

### Network Security

- Configure proper CORS settings on your Lago API backend
- Use HTTPS for all production deployments
- Consider network policies to restrict inter-pod communication

### Authentication

- Disable signup (`lago-disable-signup=true`) for enterprise deployments
- Configure OAuth proxy for SSO integration
- Ensure API backend has proper authentication mechanisms

## Troubleshooting

### Common Issues

#### 1. Frontend not loading

**Symptoms:** White screen or loading errors
**Solutions:**
```bash
# Check charm status.
juju status lago-front-k8s

# Check pod logs.
kubectl logs -n your-model -l app.kubernetes.io/name=lago-front-k8s -c lago-frontend

# Verify configuration.
juju config lago-front-k8s
```

#### 2. API connection failures

**Symptoms:** Login fails, network errors in browser console
**Solutions:**
```bash
# Verify API URL is accessible from cluster.
kubectl run test-pod --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl -I http://your-api-url/health

# Check CORS configuration on API backend.
# Ensure LAGO_FRONT_URL environment variable is set correctly on API.
```

#### 3. Image pull failures

**Symptoms:** `ImagePullBackOff` errors
**Solutions:**
```bash
# Check image exists and is accessible.
docker pull ghcr.io/theohigham/lago-front:latest

# For private registries, create image pull secret.
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=your-username \
  --docker-password=your-token \
  -n your-model

# Patch service account.
kubectl patch serviceaccount lago-front-k8s \
  -p '{"imagePullSecrets": [{"name": "ghcr-secret"}]}' \
  -n your-model
```

### Debug Mode

Enable debug logging:

```bash
juju config lago-front-k8s app-env=development
juju debug-log --include=lago-front-k8s --replay
```

## Architecture

### Operator Pattern

This charm follows the operator pattern:
- **Separation of concerns:** Application code (OCI image) separate from operational logic (charm)
- **Declarative configuration:** Desired state managed through Juju configuration
- **Lifecycle management:** Handles installation, upgrades, and configuration changes
- **Integration ready:** Designed to work with other Juju charms and operators

### Runtime Configuration

The charm generates a dynamic `env-config.js` file that configures the frontend at runtime:
- Environment variables are injected as `window.API_URL`, `window.APP_ENV`, etc.
- Configuration changes trigger immediate updates without pod restarts
- Supports all Lago frontend configuration options

## Development

### Building from Source

```bash
# Clone and build.
git clone <your-repo>
cd lago-front-operator
charmcraft pack
```

### Testing

```bash
# Deploy to test model.
juju add-model test-lago
juju deploy ./lago-front-k8s_*.charm --resource oci-image=nginx:alpine

# Run integration tests.
juju status
juju config lago-front-k8s api-url=http://test-api.example.com
```

### Contributing

1. Follow Juju charm development best practices
2. Update documentation for any configuration changes
3. Test thoroughly with different deployment scenarios
4. Ensure backward compatibility for configuration options

## License

This operator is distributed under the Apache Software License, version 2.0.

## Support

For issues related to:
- **Charm functionality:** Open an issue in this repository
- **Lago application:** See [Lago documentation](https://docs.getlago.com/)
- **Juju platform:** See [Juju documentation](https://juju.is/docs)