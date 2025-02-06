import subprocess
import os 

def ensure_correct_base_path():
    import os
    is_composable: bool = os.getenv("IS_COMPOSABLE", "false").lower() == "true"
    if is_composable:
        subdirectory = "agent-studio"
        working_dir = os.path.join("/home/cdsw", subdirectory)
        print(f"Changing working directory to '{working_dir}'")
        os.chdir(working_dir)
ensure_correct_base_path()

CDSW_APP_PORT = os.environ.get("CDSW_APP_PORT")
out = subprocess.run([f"bash ./bin/start-app-script.sh {CDSW_APP_PORT}"], shell=True, check=True)
print(out)

print("App start script is complete.")
