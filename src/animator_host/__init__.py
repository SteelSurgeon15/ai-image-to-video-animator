"""ai-image-to-video-animator — plugin host for AI image-to-video pipelines."""

__version__ = "0.9.2"
HOST_API_VERSION = (0, 9)

from animator_host.contracts.plugin import AnimatorPlugin, PluginManifest

__all__ = ["AnimatorPlugin", "PluginManifest", "__version__", "HOST_API_VERSION"]