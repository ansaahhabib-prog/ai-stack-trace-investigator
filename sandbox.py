import docker
import os
import tempfile
import shutil

class DockerSandbox:
    def __init__(self, dockerfile_dir: str = "."):
        try:
            self.client = docker.from_env()
        except docker.errors.DockerException as e:
            print(f"Error connecting to Docker: {e}")
            self.client = None
            
        self.image_name = "ai-stack-trace-sandbox"
        self.dockerfile_dir = dockerfile_dir
        self.image_built = False

    def build_image(self):
        if not self.client:
            return False
            
        try:
            print("Building sandbox Docker image...")
            self.client.images.build(path=self.dockerfile_dir, tag=self.image_name, rm=True)
            self.image_built = True
            print("Image built successfully.")
            return True
        except Exception as e:
            print(f"Failed to build image: {e}")
            return False

    def run_reproduction(self, code_snippet: str) -> dict:
        if not self.client:
            return {"status": "error", "message": "Docker not available."}
            
        if not self.image_built:
            success = self.build_image()
            if not success:
                return {"status": "error", "message": "Failed to build sandbox image."}

        # Create a temporary directory to mount
        temp_dir = tempfile.mkdtemp()
        script_path = os.path.join(temp_dir, "reproduce.py")
        
        with open(script_path, "w") as f:
            f.write(code_snippet)

        try:
            container = self.client.containers.run(
                self.image_name,
                command=["python", "/app/reproduce.py"],
                volumes={temp_dir: {'bind': '/app', 'mode': 'ro'}},
                working_dir="/app",
                detach=True,
                network_disabled=True, # Sandboxing
                mem_limit="256m"
            )
            
            result = container.wait(timeout=30)
            logs = container.logs().decode("utf-8")
            
            container.remove()
            
            return {
                "status": "success",
                "exit_code": result["StatusCode"],
                "logs": logs
            }
            
        except docker.errors.ContainerError as e:
            # Re-raise or handle if container fails to run completely
            return {"status": "container_error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
