import os
import json
from pathlib import Path
from dotenv import load_dotenv
from platformdirs import user_config_dir
from typing import Optional, Dict, Any

# Load .env: first from cwd (project local), then fall back to ~/.env
load_dotenv()
load_dotenv(Path.home() / ".env", override=False)

class Config:
    def __init__(self):
        self.oauth_consumer_key = os.getenv("ETRADE_OAUTH_CONSUMER_KEY")
        self.oauth_consumer_secret = os.getenv("ETRADE_OAUTH_CONSUMER_SECRET")
        self.sandbox = os.getenv("ETRADE_SANDBOX", "false").lower() in ("1", "true", "yes")
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from XDG config directories"""
        config_dirs = [
            Path(user_config_dir("mcp-etrade")),
            Path.home() / ".config" / "mcp-etrade",
            Path("/etc/mcp-etrade")
        ]
        
        for config_dir in config_dirs:
            config_file = config_dir / "config.json"
            if config_file.exists():
                try:
                    with open(config_file) as f:
                        return json.load(f)
                except (json.JSONDecodeError, IOError):
                    continue
        
        return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config_data.get(key, default)
    
    @property
    def is_configured(self) -> bool:
        """Check if OAuth credentials are available"""
        return bool(self.oauth_consumer_key and self.oauth_consumer_secret)
