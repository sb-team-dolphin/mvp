import os
import re
import yaml
from pathlib import Path
from typing import Optional


class Settings:
    """Application configuration settings - reads from YAML like Spring Boot"""

    def __init__(self):
        # Get profile from environment (default: local)
        self.profile = os.getenv('SPRING_PROFILES_ACTIVE', 'local')

        # Application settings
        self.app_name = "MyApp Backend"
        self.environment = self.profile
        self.server_port = 8080

        # Load configuration from YAML
        self._load_from_yaml()

    def _substitute_env_vars(self, value: str) -> str:
        """
        Substitute ${ENV_VAR} or ${ENV_VAR:default} patterns with environment variables
        Similar to Spring Boot property placeholder resolution
        """
        if not isinstance(value, str):
            return value

        # Pattern: ${VAR_NAME} or ${VAR_NAME:default_value}
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'

        def replacer(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ''
            return os.getenv(var_name, default_value)

        return re.sub(pattern, replacer, value)

    def _load_from_yaml(self):
        """Load configuration from YAML file based on active profile"""

        # Try to load config-{profile}.yml first
        config_file = Path(__file__).parent.parent / f'config-{self.profile}.yml'

        if not config_file.exists():
            # Fallback to default values for local development
            if self.profile == 'local':
                self.db_host = "localhost"
                self.db_port = 3306
                self.db_name = "myappdb"
                self.db_username = "root"
                self.db_password = ""
                return
            else:
                raise FileNotFoundError(f"Configuration file not found: {config_file}")

        # Load YAML file
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if not config:
            raise ValueError(f"Empty or invalid YAML file: {config_file}")

        # Parse Spring Boot style configuration
        spring_config = config.get('spring', {})
        datasource = spring_config.get('datasource', {})

        # Extract database URL (jdbc:mysql://host:port/dbname?params)
        jdbc_url = datasource.get('url', '')
        jdbc_url = self._substitute_env_vars(jdbc_url)

        # Parse JDBC URL
        if jdbc_url.startswith('jdbc:mysql://'):
            # Remove jdbc:mysql:// prefix
            url_part = jdbc_url.replace('jdbc:mysql://', '')

            # Split host:port/dbname?params
            if '/' in url_part:
                host_port, db_part = url_part.split('/', 1)

                # Extract host and port
                if ':' in host_port:
                    self.db_host, port_str = host_port.split(':', 1)
                    self.db_port = int(port_str)
                else:
                    self.db_host = host_port
                    self.db_port = 3306

                # Extract database name (remove query params)
                self.db_name = db_part.split('?')[0]

        # Get username and password
        self.db_username = self._substitute_env_vars(datasource.get('username', ''))
        self.db_password = self._substitute_env_vars(datasource.get('password', ''))

    @property
    def database_url(self) -> str:
        """Construct database URL for SQLAlchemy"""
        return f"mysql+pymysql://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


# Global settings instance
settings = Settings()
