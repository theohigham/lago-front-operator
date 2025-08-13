#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""A Juju charm for Lago Frontend."""

import logging

from ops import (
    ConfigChangedEvent,
    PebbleReadyEvent,
    StartEvent,
)
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, WaitingStatus
from ops.pebble import Layer

logger = logging.getLogger(__name__)

WORKLOAD_CONTAINER = "lago-frontend"
WORKLOAD_SERVICE = "lago-frontend"
WORKLOAD_PORT = 80


class LagoFrontendOperatorCharm(CharmBase):
    """Charm for deploying Lago Frontend."""

    def __init__(self, *args):
        super().__init__(*args)
        
        self._container = self.unit.get_container(WORKLOAD_CONTAINER)
        
        # Lifecycle event handlers.
        self.framework.observe(
            self.on.lago_frontend_pebble_ready, self._on_pebble_ready
        )
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.start, self._on_start)

    def _on_pebble_ready(self, event: PebbleReadyEvent) -> None:
        """Handle pebble ready event."""
        if not self._container.can_connect():
            self.unit.status = WaitingStatus("Waiting for container to be ready")
            event.defer()
            return

        self._configure_workload(event)

    def _on_config_changed(self, event: ConfigChangedEvent) -> None:
        """Handle configuration changes."""
        self._configure_workload(event)

    def _on_start(self, event: StartEvent) -> None:
        """Handle start event."""
        self._configure_workload(event)

    def _configure_workload(self, event) -> None:
        """Configure the lago frontend workload."""
        if not self._container.can_connect():
            self.unit.status = WaitingStatus("Waiting for container connection")
            event.defer()
            return

        # Validate required configuration.
        api_url = self.config["api-url"]
        if not api_url:
            self.unit.status = BlockedStatus("Missing required config: api-url")
            return

        # Build environment variables for the container.
        env_vars = self._build_environment_variables()
        
        # Create pebble layer.
        pebble_layer = self._create_pebble_layer(env_vars)
        
        # Add the layer to pebble.
        self._container.add_layer(WORKLOAD_SERVICE, pebble_layer, combine=True)
        
        # Restart the service to pick up changes.
        self._container.replan()
        
        # Open the port for nginx integration.
        self.unit.open_port("tcp", WORKLOAD_PORT)
        
        self.unit.status = ActiveStatus("Lago frontend is ready")

    def _build_environment_variables(self) -> dict:
        """Build environment variables from charm configuration."""
        config = self.config
        
        env_vars = {
            "API_URL": config["api-url"],
            "APP_ENV": config["app-env"],
        }
        
        # Add optional configurations if provided.
        if config["lago-domain"]:
            env_vars["LAGO_DOMAIN"] = config["lago-domain"]
            
        if config["lago-oauth-proxy-url"]:
            env_vars["LAGO_OAUTH_PROXY_URL"] = config["lago-oauth-proxy-url"]
            
        if config["lago-disable-signup"]:
            env_vars["LAGO_DISABLE_SIGNUP"] = "true"
        else:
            env_vars["LAGO_DISABLE_SIGNUP"] = "false"
            
        if config["lago-disable-pdf-generation"]:
            env_vars["LAGO_DISABLE_PDF_GENERATION"] = "true"
        else:
            env_vars["LAGO_DISABLE_PDF_GENERATION"] = "false"
            
        if config["nango-public-key"]:
            env_vars["NANGO_PUBLIC_KEY"] = config["nango-public-key"]
            
        if config["sentry-dsn"]:
            env_vars["SENTRY_DSN"] = config["sentry-dsn"]

        return env_vars

    def _create_pebble_layer(self, env_vars: dict) -> Layer:
        """Create the pebble layer for lago frontend."""
        pebble_layer = {
            "summary": "lago frontend layer",
            "description": "pebble layer for lago frontend",
            "services": {
                WORKLOAD_SERVICE: {
                    "override": "replace",
                    "summary": "lago frontend service",
                    "command": "nginx -g 'daemon off;'",
                    "startup": "enabled",
                    "environment": env_vars,
                }
            },
            "checks": {
                "http-check": {
                    "override": "replace",
                    "level": "alive",
                    "period": "30s",
                    "http": {"url": f"http://localhost:{WORKLOAD_PORT}/"},
                },
            },
        }
        
        return Layer(pebble_layer)


if __name__ == "__main__":
    main(LagoFrontendOperatorCharm)
