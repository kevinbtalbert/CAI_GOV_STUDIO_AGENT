import subprocess
import cmlapi
import os
from typing import Dict 
import json
from studio.consts import DEFAULT_AS_PHOENIX_OPS_PLATFORM_PORT
import http.server
import http.client
import urllib.parse



def start_phoenix_server():
    """
    Start up the actual phoenix observability platform server process.
    """
    
    print("Starting up the Phoenix ops platform server...")
    out = subprocess.run([f"bash ./bin/start-agent-ops-phoenix.sh"], shell=True, check=True)


def set_ops_server_discovery():
    """
    Write this application pod's IP and port to the project
    environment variables. This will allow other pods and workflows
    to access the UI through http://<ip>:<port>/, and the graphql
    endpoint through http://<ip>:<port>/graphql
    """

    # Set some new environment variables
    os.environ["AGENT_STUDIO_OPS_IP"] = os.getenv("CDSW_IP_ADDRESS")
    os.environ["AGENT_STUDIO_OPS_PORT"] = DEFAULT_AS_PHOENIX_OPS_PLATFORM_PORT
    cml = cmlapi.default_client()
    project_id = os.getenv("CDSW_PROJECT_ID")
    proj: cmlapi.Project = cml.get_project(project_id)
    proj_env: Dict = json.loads(proj.environment)
    proj_env.update({
        "AGENT_STUDIO_OPS_IP": os.environ["AGENT_STUDIO_OPS_IP"],
        "AGENT_STUDIO_OPS_PORT": os.environ["AGENT_STUDIO_OPS_PORT"]
    })
    updated_project: cmlapi.Project = cmlapi.Project(
        environment= json.dumps(proj_env)
    )
    out: cmlapi.Project = cml.update_project(updated_project, project_id=project_id)
    print(out.environment)
    print("LLM Ops Server discoverable through project env variables!")


# Define the target server to forward requests to
TARGET_SERVER = "0.0.0.0"

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    """
    We do not inherently serve the ops platform on $CDSW_APP_PORT because this
    port is gated with authentication, which affects both our /v1/trace calls
    and the /graphql calls to this endpoint. Instead, we serve on a dedicated
    port in the container, and forward all traffic from CDSW_APP_PORT to 
    our phoenix server with this python middleware.
    """
    
    def do_GET(self):
        self.forward_request()

    def do_POST(self):
        self.forward_request()

    def forward_request(self):

        # The target URL is where the phoenix server resides
        target_url = f"http://{TARGET_SERVER}:{DEFAULT_AS_PHOENIX_OPS_PLATFORM_PORT}{self.path}"

        # Forward the request to the target server
        url = urllib.parse.urlparse(target_url)
        conn = http.client.HTTPConnection(url.hostname, url.port)

        # Forward the headers
        headers = {key: value for key, value in self.headers.items()}

        # Read the body (for POST requests)
        body = None
        if self.command == "POST":
            content_length = self.headers.get("Content-Length")
            if content_length:
                body = self.rfile.read(int(content_length))

        # Send the request to the target server
        conn.request(self.command, url.path + ("?" + url.query if url.query else ""), body, headers)
        response = conn.getresponse()

        # Send the response back to the client
        self.send_response(response.status)
        for key, value in response.getheaders():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(response.read())
        

def run_proxy_server():
    """
    Start up the proxy server. This makes the phoenix observability platform visible right from the 
    CDSW application by forwarding all CDSW_APP_PORT traffic to the dedicated phoenix server running
    on a separate host port.
    """
    server_address = ("127.0.0.1", int(os.getenv("CDSW_APP_PORT")))
    print(f"Starting proxy server on {server_address[0]}:{server_address[1]}, forwarding to {TARGET_SERVER}")
    httpd = http.server.HTTPServer(server_address, ProxyHandler)
    httpd.serve_forever()


set_ops_server_discovery()
start_phoenix_server()
run_proxy_server()