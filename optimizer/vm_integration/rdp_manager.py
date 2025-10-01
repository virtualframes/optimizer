"""
VM RDP System Integration Manager
Handles Remote Desktop Protocol connections, VM management, and cross-platform compatibility.
This module uses optional dependencies. To use all features, install with `pip install 'optimizer[vm]'`.
"""
import asyncio
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import json
import socket
import ssl
from contextlib import asynccontextmanager

# --- Guarded Imports for Optional Dependencies ---
# These dependencies are part of the '[vm]' extra.
# They are imported conditionally to allow the module to be imported
# even if the optional dependencies are not installed.

_psutil_available = False
try:
    import psutil
    _psutil_available = True
except ImportError:
    psutil = None

_paramiko_available = False
try:
    import paramiko
    _paramiko_available = True
except ImportError:
    paramiko = None

_cryptography_available = False
try:
    from cryptography.fernet import Fernet
    _cryptography_available = True
except ImportError:
    Fernet = None

_winrm_available = False
try:
    import winrm
    _winrm_available = True
except ImportError:
    winrm = None

_fabric_available = False
try:
    from fabric import Connection
    _fabric_available = True
except ImportError:
    Connection = None

_docker_available = False
try:
    import docker
    _docker_available = True
except ImportError:
    docker = None

_win32_available = False
try:
    import win32api
    import win32security
    import win32net
    _win32_available = True
except ImportError:
    win32api = win32security = win32net = None


logger = logging.getLogger(__name__)

class VMProvider(Enum):
    """Supported VM providers"""
    HYPERV = "hyperv"
    VMWARE = "vmware"
    VIRTUALBOX = "virtualbox"
    DOCKER = "docker"
    QEMU = "qemu"

class RDPAuthMethod(Enum):
    """RDP authentication methods"""
    NTLM = "ntlm"
    KERBEROS = "kerberos"
    CERTIFICATE = "certificate"
    SMARTCARD = "smartcard"

class OSType(Enum):
    """Operating system types"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    FREEBSD = "freebsd"

@dataclass
class RDPConnection:
    """RDP connection configuration"""
    host: str
    port: int = 3389
    username: str = ""
    password: str = ""
    domain: str = ""
    auth_method: RDPAuthMethod = RDPAuthMethod.NTLM
    use_tls: bool = True
    verify_cert: bool = True
    screen_width: int = 1920
    screen_height: int = 1080
    color_depth: int = 32
    keyboard_layout: str = "en-US"
    audio_enabled: bool = False
    clipboard_enabled: bool = True
    drive_redirection: bool = True
    printer_redirection: bool = False
    session_timeout: int = 3600
    connection_timeout: int = 30

@dataclass
class VMConfiguration:
    """Virtual machine configuration"""
    vm_id: str
    name: str
    provider: VMProvider
    os_type: OSType
    cpu_cores: int = 2
    memory_mb: int = 4096
    disk_size_gb: int = 100
    network_adapter: str = "internal"
    template: str = ""
    resource_pool: str = ""
    storage_path: str = ""
    auto_start: bool = False
    auto_stop: bool = True
    snapshot_enabled: bool = True

class RDPManager:
    """
    Comprehensive RDP and VM management system.
    Requires optional dependencies for full functionality. Install with `pip install 'optimizer[vm]'`.
    """

    def __init__(self):
        self.config = self._load_config()
        self.active_connections: Dict[str, Dict] = {}
        self.vm_configurations: Dict[str, VMConfiguration] = {}
        self.encryption_key = self._get_encryption_key()

        # Initialize platform-specific handlers
        self.platform = self._detect_platform()
        self._init_platform_handlers()

    def _load_config(self) -> Dict:
        """Load configuration from environment variables"""
        return {
            'rdp_enabled': os.getenv('RDP_ENABLED', 'true').lower() == 'true',
            'rdp_default_host': os.getenv('RDP_DEFAULT_HOST', 'localhost'),
            'rdp_default_port': int(os.getenv('RDP_DEFAULT_PORT', '3389')),
            'rdp_default_username': os.getenv('RDP_DEFAULT_USERNAME', ''),
            'rdp_default_password': os.getenv('RDP_DEFAULT_PASSWORD', ''),
            'rdp_default_domain': os.getenv('RDP_DEFAULT_DOMAIN', ''),
            'rdp_connection_timeout': int(os.getenv('RDP_CONNECTION_TIMEOUT', '30')),
            'rdp_session_timeout': int(os.getenv('RDP_SESSION_TIMEOUT', '3600')),
            'rdp_max_connections': int(os.getenv('RDP_MAX_CONNECTIONS', '10')),
            'rdp_use_tls': os.getenv('RDP_USE_TLS', 'true').lower() == 'true',
            'rdp_verify_certificates': os.getenv('RDP_VERIFY_CERTIFICATES', 'true').lower() == 'true',
            'rdp_certificate_path': os.getenv('RDP_CERTIFICATE_PATH', ''),
            'rdp_private_key_path': os.getenv('RDP_PRIVATE_KEY_PATH', ''),
            'rdp_screen_width': int(os.getenv('RDP_SCREEN_WIDTH', '1920')),
            'rdp_screen_height': int(os.getenv('RDP_SCREEN_HEIGHT', '1080')),
            'rdp_color_depth': int(os.getenv('RDP_COLOR_DEPTH', '32')),
            'vm_provider': VMProvider(os.getenv('VM_PROVIDER', 'hyperv')),
            'vm_management_url': os.getenv('VM_MANAGEMENT_URL', ''),
            'vm_management_token': os.getenv('VM_MANAGEMENT_TOKEN', ''),
            'vm_default_template': os.getenv('VM_DEFAULT_TEMPLATE', 'windows-server-2022'),
            'vm_resource_pool': os.getenv('VM_RESOURCE_POOL', 'development'),
            'vm_network_adapter': os.getenv('VM_NETWORK_ADAPTER', 'internal'),
            'vm_storage_path': os.getenv('VM_STORAGE_PATH', '/var/lib/vms'),
            'vm_backup_path': os.getenv('VM_BACKUP_PATH', '/var/backups/vms'),
            'vm_snapshot_enabled': os.getenv('VM_SNAPSHOT_ENABLED', 'true').lower() == 'true',
            'vm_auto_start': os.getenv('VM_AUTO_START', 'false').lower() == 'true',
            'vm_auto_stop': os.getenv('VM_AUTO_STOP', 'true').lower() == 'true',
        }

    def _get_encryption_key(self):
        """Get or generate encryption key for sensitive data"""
        if not _cryptography_available:
            logger.warning("Cryptography not available. Skipping encryption key generation.")
            return None
        key_env = os.getenv('ENCRYPTION_KEY')
        if key_env:
            return Fernet(key_env.encode())

        # Generate new key if not provided
        key = Fernet.generate_key()
        logger.warning("No ENCRYPTION_KEY provided, generated temporary key")
        return Fernet(key)

    def _detect_platform(self) -> str:
        """Detect the current operating system platform"""
        import platform
        system = platform.system().lower()

        if system == 'windows':
            return 'windows'
        elif system == 'darwin':
            return 'macos'
        elif system == 'linux':
            return 'linux'
        else:
            return 'unknown'

    def _init_platform_handlers(self):
        """Initialize platform-specific handlers"""
        if self.platform == 'windows':
            self._init_windows_handlers()
        elif self.platform == 'linux':
            self._init_linux_handlers()
        elif self.platform == 'macos':
            self._init_macos_handlers()

    def _init_windows_handlers(self):
        """Initialize Windows-specific RDP handlers"""
        if _win32_available:
            self.windows_available = True
            logger.info("Windows RDP handlers initialized")
        else:
            self.windows_available = False
            logger.info("Windows-specific modules (pywin32) not available. Windows RDP functionality disabled.")

    def _init_linux_handlers(self):
        """Initialize Linux-specific RDP handlers"""
        # Check for xfreerdp, rdesktop, or other RDP clients
        self.rdp_clients = []
        for client in ['xfreerdp', 'rdesktop', 'remmina']:
            if self._command_exists(client):
                self.rdp_clients.append(client)
        logger.info(f"Linux RDP clients available: {self.rdp_clients}")

    def _init_macos_handlers(self):
        """Initialize macOS-specific RDP handlers"""
        # Check for Microsoft Remote Desktop or other RDP clients
        self.macos_rdp_available = self._command_exists('open')
        logger.info(f"macOS RDP support: {self.macos_rdp_available}")

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH"""
        try:
            subprocess.run([command, '--version'], capture_output=True, text=True, timeout=5, check=True)
            return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False

    async def create_vm(self, vm_config: VMConfiguration) -> str:
        """Create a new virtual machine"""
        provider = vm_config.provider

        if provider == VMProvider.DOCKER:
            if not _docker_available:
                raise ImportError("Docker support requires the 'docker' package. Please install with 'pip install optimizer[vm]'")
            return await self._create_docker_container(vm_config)
        else:
            # Placeholder for other providers
            raise NotImplementedError(f"VM creation for provider '{provider.value}' is not yet implemented.")

    async def _create_docker_container(self, config: VMConfiguration) -> str:
        """Create Docker container as VM substitute"""
        client = docker.from_env()

        image_map = {
            OSType.WINDOWS: 'mcr.microsoft.com/windows/servercore:ltsc2022',
            OSType.LINUX: 'ubuntu:22.04',
            OSType.MACOS: 'sickcodes/docker-osx:latest'
        }
        image = image_map.get(config.os_type, 'ubuntu:22.04')

        container_config = {
            'image': image,
            'name': config.name,
            'detach': True,
            'mem_limit': f'{config.memory_mb}m',
            'cpu_count': config.cpu_cores,
            'restart_policy': {'Name': 'unless-stopped'},
            'labels': {
                'jules.vm_id': config.vm_id,
                'jules.vm_type': 'docker',
                'jules.os_type': config.os_type.value
            }
        }
        container = client.containers.run(**container_config)
        self.vm_configurations[config.vm_id] = config
        logger.info(f"Docker container created: {config.name} ({container.id})")
        return config.vm_id

    async def health_check(self) -> Dict:
        """Perform health check of RDP and VM systems"""
        if not _psutil_available:
            raise ImportError("psutil is required for health checks. Please install with 'pip install optimizer[vm]'")

        health = {
            'rdp_enabled': self.config['rdp_enabled'],
            'platform': self.platform,
            'active_connections': len(self.active_connections),
            'max_connections': self.config['rdp_max_connections'],
            'configured_vms': len(self.vm_configurations),
            'vm_provider': self.config['vm_provider'].value,
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage': dict(psutil.disk_usage('/')._asdict())
            },
            'dependencies': {
                'psutil': _psutil_available,
                'paramiko': _paramiko_available,
                'cryptography': _cryptography_available,
                'winrm': _winrm_available,
                'fabric': _fabric_available,
                'docker': _docker_available,
                'pywin32': _win32_available,
            }
        }
        return health