"""Backend tool functions for the mcp-apps-lab server.

These are plain functions: the apps in ``mcp_apps_lab.apps`` register them
with ``app.add_tool(...)``, which tags each one with the owning app's hash
so the UIs can call it over the tool proxy under a hashed name (the proxy
never sees the plain names).
"""
