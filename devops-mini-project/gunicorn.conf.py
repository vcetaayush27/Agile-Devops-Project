import os
bind = "0.0.0.0:" + os.getenv("PORT", "10000")
workers = 2
threads = 2
timeout = 30
accesslog = "-"
errorlog = "-"
capture_output = True
# Runtime control commands are unnecessary for this small container.
# Disable the optional Unix control socket to avoid home-directory permission issues.
control_socket_disable = True
