import logging
import subprocess
import time
from typing import Dict, Optional, List
from pydantic import BaseModel, Field
import docker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Pydantic Models for Type-Safe Configuration ---

class RDPConfig(BaseModel):
    """Configuration for RDP connections."""
    enabled: bool = True
    port: int = 3389
    tls_enabled: bool = True
    session_ttl: int = Field(3600, description="Session Time-to-Live in seconds.")
    allow_clipboard: bool = True
    allow_drive_redirection: bool = True

class ContainerResources(BaseModel):
    """Resource limits for Docker containers."""
    cpus: float = 1.5
    memory_limit: str = "2g"
    auto_remove: bool = True
    restart_policy: Dict = Field(default_factory=lambda: {"Name": "on-failure", "MaximumRetryCount": 3})

class VMConfig(BaseModel):
    """A comprehensive configuration for a single VM or container environment."""
    name: str
    provider: str = "docker"
    image: str = "ubuntu:latest"
    rdp: RDPConfig = Field(default_factory=RDPConfig)
    resources: ContainerResources = Field(default_factory=ContainerResources)
    environment: Dict[str, str] = Field(default_factory=dict)
    repo_clone_url: Optional[str] = None

# --- Main VM Manager Class ---

class EnhancedVMManager:
    """
    Manages the lifecycle of VMs and containers for sandboxed development and testing.
    Integrates with Docker as the primary provider and is designed for extensibility.
    """
    def __init__(self, config: VMConfig):
        """
        Initializes the VM Manager with a specific configuration.

        Args:
            config: A VMConfig object defining the environment to be managed.
        """
        self.config = config
        self.client = None
        if self.config.provider == "docker":
            try:
                self.client = docker.from_env()
                self.client.ping()
                logger.info("Successfully connected to Docker daemon.")
            except docker.errors.DockerException as e:
                logger.error(f"Failed to connect to Docker daemon: {e}")
                raise ConnectionError("Could not connect to Docker. Is the Docker daemon running?") from e
        else:
            raise NotImplementedError(f"Provider '{self.config.provider}' is not yet supported.")

    def _execute_command_in_container(self, container, command: str) -> (int, str):
        """Helper to execute a command inside a running container."""
        logger.info(f"Executing command in container {container.short_id}: '{command}'")
        exit_code, output = container.exec_run(command)
        return exit_code, output.decode('utf-8')

    def provision(self) -> Optional[docker.models.containers.Container]:
        """
        Provisions the VM or container based on the instance's configuration.

        This involves pulling the necessary image and creating the container with
        the specified resources, environment, and restart policies.
        """
        if not self.client:
            logger.error("Cannot provision: Docker client is not available.")
            return None

        logger.info(f"Provisioning container '{self.config.name}' from image '{self.config.image}'...")
        try:
            logger.info(f"Pulling image '{self.config.image}'. This may take a moment...")
            self.client.images.pull(self.config.image)
            logger.info("Image pulled successfully.")

            container = self.client.containers.create(
                image=self.config.image,
                name=self.config.name,
                detach=True,
                environment=self.config.environment,
                mem_limit=self.config.resources.memory_limit,
                cpu_shares=int(self.config.resources.cpus * 1024),
                auto_remove=self.config.resources.auto_remove,
                restart_policy=self.config.resources.restart_policy,
                command="/bin/sleep infinity"  # Keep container running
            )
            logger.info(f"Container '{self.config.name}' created with ID: {container.short_id}")
            return container
        except docker.errors.ImageNotFound:
            logger.error(f"Image '{self.config.image}' not found. Please check the image name.")
        except docker.errors.APIError as e:
            logger.error(f"Docker API error during provisioning: {e}")
        return None

    def start(self) -> Optional[docker.models.containers.Container]:
        """
        Starts a provisioned container and performs initial setup, like cloning a repository.
        """
        if not self.client:
            return None

        try:
            container = self.client.containers.get(self.config.name)
            if container.status == 'running':
                logger.info(f"Container '{self.config.name}' is already running.")
                return container

            logger.info(f"Starting container '{self.config.name}'...")
            container.start()
            container.reload() # Refresh container state
            logger.info(f"Container '{self.config.name}' started. Status: {container.status}")

            # Post-start setup
            if self.config.repo_clone_url:
                logger.info(f"Cloning repository '{self.config.repo_clone_url}' into the container...")
                exit_code, output = self._execute_command_in_container(
                    container,
                    f"git clone {self.config.repo_clone_url} /app"
                )
                if exit_code == 0:
                    logger.info("Repository cloned successfully.")
                else:
                    logger.error(f"Failed to clone repository. Output:\n{output}")

            return container
        except docker.errors.NotFound:
            logger.warning(f"Container '{self.config.name}' not found. Provisioning it first.")
            container = self.provision()
            if container:
                return self.start() # Retry starting
        except docker.errors.APIError as e:
            logger.error(f"Docker API error during start: {e}")
        return None

    def stop(self, timeout: int = 10):
        """Stops the running container."""
        if not self.client:
            return

        try:
            container = self.client.containers.get(self.config.name)
            if container.status != 'running':
                logger.info(f"Container '{self.config.name}' is not running.")
                return
            logger.info(f"Stopping container '{self.config.name}'...")
            container.stop(timeout=timeout)
            logger.info("Container stopped.")
        except docker.errors.NotFound:
            logger.warning(f"Container '{self.config.name}' not found. Cannot stop.")
        except docker.errors.APIError as e:
            logger.error(f"Docker API error during stop: {e}")

    def get_status(self) -> str:
        """Returns the status of the container."""
        if not self.client:
            return "unavailable"
        try:
            container = self.client.containers.get(self.config.name)
            return container.status
        except docker.errors.NotFound:
            return "not_found"

    def destroy(self):
        """Stops and removes the container, cleaning up resources."""
        if not self.client:
            return

        try:
            container = self.client.containers.get(self.config.name)
            logger.info(f"Destroying container '{self.config.name}'...")
            container.remove(force=True)
            logger.info("Container destroyed.")
        except docker.errors.NotFound:
            logger.warning(f"Container '{self.config.name}' not found. Nothing to destroy.")
        except docker.errors.APIError as e:
            logger.error(f"Docker API error during destroy: {e}")

# --- Example Usage ---
if __name__ == '__main__':
    logger.info("--- Running EnhancedVMManager Demo ---")

    # 1. Define the configuration for our development environment
    dev_vm_config = VMConfig(
        name="jules-dev-env",
        image="python:3.9-slim",
        repo_clone_url="https://github.com/someuser/someproject.git",
        environment={"API_KEY": "dummy_key_123"},
        resources=ContainerResources(cpus=1.0, memory_limit="1g")
    )

    # 2. Instantiate the manager
    manager = EnhancedVMManager(config=dev_vm_config)

    # 3. Full lifecycle demonstration
    try:
        # Start the VM (will provision if it doesn't exist)
        container = manager.start()

        if container:
            # Check status
            print(f"Current status: {manager.get_status()}")
            time.sleep(5)  # Give it time to run

            # Execute a command to verify setup
            print("Verifying repository clone...")
            code, out = manager._execute_command_in_container(container, "ls -l /app")
            print(f"Verification command output:\n{out}")

        # Stop the VM
        manager.stop()
        print(f"Status after stop: {manager.get_status()}")

    except ConnectionError as e:
        print(f"Exiting due to connection error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during the demo: {e}", exc_info=True)
    finally:
        # Clean up resources
        print("--- Tearing down environment ---")
        manager.destroy()
        print(f"Final status: {manager.get_status()}")
        logger.info("--- Demo Finished ---")