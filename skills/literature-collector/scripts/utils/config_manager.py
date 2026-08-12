import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigurationError(Exception):
    pass


class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else self._find_config_file()
        self.config = self._load_config()

    def _find_config_file(self) -> Path:
        possible_paths = [
            Path(__file__).parent.parent.parent / 'assets' / 'config.json',
            Path.cwd() / 'config.json',
            Path.home() / '.literature-collector' / 'config.json',
        ]

        for path in possible_paths:
            if path.exists():
                return path

        raise ConfigurationError(
            "配置文件未找到。请确保以下任一路径下存在config.json文件：\n"
            f"  - {Path(__file__).parent.parent.parent / 'assets' / 'config.json'}\n"
            f"  - {Path.cwd() / 'config.json'}\n"
            f"  - {Path.home() / '.literature-collector' / 'config.json'}"
        )

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self._validate_config(config)
            return config
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"配置文件JSON格式错误: {e}")
        except FileNotFoundError:
            raise ConfigurationError(f"配置文件未找到: {self.config_path}")

    def _validate_config(self, config: Dict[str, Any]) -> None:
        if 'api_keys' not in config:
            raise ConfigurationError("配置文件缺少api_keys部分")

        if 'search_settings' not in config:
            raise ConfigurationError("配置文件缺少search_settings部分")

        if 'output_settings' not in config:
            raise ConfigurationError("配置文件缺少output_settings部分")

    def get_api_key(self, source: str) -> str:
        try:
            return self.config['api_keys'][source]['api_key']
        except KeyError:
            raise ConfigurationError(f"找不到 {source} 的API密钥配置")

    def get_endpoint(self, source: str) -> str:
        try:
            return self.config['api_keys'][source]['endpoint']
        except KeyError:
            raise ConfigurationError(f"找不到 {source} 的endpoint配置")

    def get_rate_limit(self, source: str) -> int:
        try:
            return self.config['api_keys'][source].get('rate_limit', 10)
        except KeyError:
            return 10

    def get_default_years(self) -> int:
        return self.config['search_settings'].get('default_years', 3)

    def get_max_results(self) -> int:
        return self.config['search_settings'].get('max_results_per_source', 100)

    def get_request_timeout(self) -> int:
        return self.config['search_settings'].get('request_timeout', 30)

    def get_retry_attempts(self) -> int:
        return self.config['search_settings'].get('retry_attempts', 3)

    def get_retry_delay(self) -> int:
        return self.config['search_settings'].get('retry_delay', 2)

    def include_abstract(self) -> bool:
        return self.config['output_settings'].get('include_abstract', True)

    def get_max_abstract_length(self) -> int:
        return self.config['output_settings'].get('max_abstract_length', 500)

    def get_sort_by(self) -> str:
        return self.config['output_settings'].get('sort_by', 'citations')

    def is_web_search_enabled(self) -> bool:
        return self.config.get('web_search', {}).get('enabled', True)

    def get_web_search_max_results(self) -> int:
        return self.config.get('web_search', {}).get('max_results', 20)

    def update_api_key(self, source: str, new_key: str) -> None:
        if source not in self.config['api_keys']:
            raise ConfigurationError(f"不支持的API来源: {source}")

        self.config['api_keys'][source]['api_key'] = new_key
        self._save_config()

    def _save_config(self) -> None:
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigurationError(f"保存配置文件失败: {e}")

    def get_config(self) -> Dict[str, Any]:
        return self.config.copy()

    def reload(self) -> None:
        self.config = self._load_config()
