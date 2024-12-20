# vim: set fileencoding=utf-8
"""
org/acmsl/artifact/licdata/domain/licdata_artifact.py

This file declares the LicdataArtifact class.

Copyright (C) 2024-today acmsl/licdata-artifact-domain

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import docker
import io
import json
import os
from pythoneda.shared import (
    attribute,
    listen,
    sensitive,
    Event,
    EventEmitter,
    EventListener,
    Flow,
    Ports,
)
from pythoneda.shared.artifact.events import (
    DockerImageAvailable,
    DockerImageFailed,
    DockerImagePushed,
    DockerImageRequested,
)
from pythoneda.shared.runtime.secrets.events import (
    CredentialProvided,
    CredentialRequested,
)
import tarfile
import tempfile
from typing import Dict, List


class LicdataArtifact(Flow, EventListener):
    """
    The Licdata artifact.

    Class name: LicdataArtifact

    Responsibilities:
        - Reacts to requests regarding the Licdata artifact.

    Collaborators:
        - None
    """

    _singleton = None

    def __init__(self):
        """
        Creates a new LicdataArtifact instance.
        """
        super().__init__()
        self._dependencies = None

    @classmethod
    def instance(cls):
        """
        Retrieves the singleton instance.
        :return: Such instance.
        :rtype: org.acmsl.artifact.licdata.LicdataArtifact
        """
        if cls._singleton is None:
            cls._singleton = cls.initialize()

        return cls._singleton

    @classmethod
    def initialize(cls):
        """
        Initializes the singleton instance.
        :return: Such instance.
        :rtype: org.acmsl.artifact.licdata.LicdataArtifact
        """
        return cls()

    @classmethod
    @property
    def url(cls) -> str:
        """
        Retrieves the url.
        :return: Such url.
        :rtype: str
        """
        return "https://github.com/acmsl/licdata-artifact"

    def nix_path_of(self, derivation: str, build: bool = True) -> str:
        """
        Retrieves the Nix path of given derivation, building it if necessary.
        :param derivation: The derivation.
        :type derivation: str
        :param build: Whether to build the derivation if not found.
        :type build: bool
        :return: Such path.
        :rtype: str
        """
        import subprocess

        result = None

        try:
            cmd = ["nix", "eval", "--raw", derivation]
            output = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            result = output.stdout.strip()

            # if result does not exist:
            if not os.path.exists(result) and build:
                self.nix_build(derivation)
                result = self.nix_path_of(derivation, False)

        except subprocess.CalledProcessError as e:
            LicdataArtifact.logger().debug(f"Error: {e.stderr}")

        return result

    def nix_path_of_rydnr_nix_flakes(self, name: str, version: str) -> str:
        """
        Retrieves the Nix path of given dependency.
        :param name: The dependency name.
        :type name: str
        :param version: The dependency version.
        :type version: str
        :return: Such path.
        :rtype: str
        """
        return self.nix_path_of(f"github:rydnr/nix-flakes/{name}-{version}?dir={name}")

    def nix_path_of_nixpkgs(self, name: str, version: str) -> str:
        """
        Retrieves the Nix path of given dependency.
        :param name: The dependency name.
        :type name: str
        :param version: The dependency version.
        :type version: str
        :return: Such path.
        :rtype: str
        """
        return self.nix_path_of(f"nixpkgs#python3Packages.{name}")

    def nix_build(self, derivation: str):
        """
        Builds the derivation.
        :param derivation: The derivation.
        :type derivation: str
        """
        import subprocess

        try:
            cmd = ["nix", "build", derivation]
            output = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            LicdataArtifact.logger().debug(f"Output: {output.stdout}")

        except subprocess.CalledProcessError as e:
            LicdataArtifact.logger().debug(f"Error: {e.stderr}")

    @property
    def dependencies(self) -> List[Dict[str, str]]:
        """
        Retrieves the dependencies.
        :return: Such dependencies.
        :rtype: List[Dict[str,str]]
        """
        if self._dependencies is None:
            self._dependencies = self.retrieve_dependencies()
        return self._dependencies

    def retrieve_dependencies(self) -> List[Dict[str, str]]:
        """
        Retrieves the dependencies.
        :return: Such dependencies.
        :rtype: List[Dict[str,str]]
        """
        return [
            {
                "name": "azure-functions",
                "version": "1.21.3",
                "path": self.nix_path_of_rydnr_nix_flakes(
                    "azure-functions", "1.21.3.2"
                ),
            },
            {
                "name": "brotlicffi",
                "version": "1.1.0.0",
                "path": self.nix_path_of_nixpkgs("brotlicffi", "1.1.0.0"),
            },
            {
                "name": "certifi",
                "version": "2024.2.2",
                "path": self.nix_path_of_nixpkgs("certifi", "2024.2.2"),
            },
            {
                "name": "cffi",
                "version": "1.16.0",
                "path": self.nix_path_of_nixpkgs("cffi", "1.16.0"),
            },
            {
                "name": "charset-normalizer",
                "version": "3.3.2",
                "path": self.nix_path_of_nixpkgs("charset-normalizer", "3.3.2"),
            },
            {
                "name": "coverage",
                "version": "7.4.4",
                "path": self.nix_path_of_nixpkgs("coverage", "7.4.4"),
            },
            {
                "name": "cryptography",
                "version": "42.0.5",
                "path": self.nix_path_of_nixpkgs("cryptography", "42.0.5"),
            },
            {
                "name": "dbus_next",
                "version": "0.2.3",
                "path": self.nix_path_of_rydnr_nix_flakes("dbus-next", "0.2.3.3"),
            },
            {
                "name": "ddt",
                "version": "1.7.2",
                "path": self.nix_path_of_nixpkgs("ddt", "1.7.2"),
            },
            {
                "name": "Deprecated",
                "version": "1.2.14",
                "path": self.nix_path_of_nixpkgs("deprecated", "1.2.14"),
            },
            {
                "name": "dnspython",
                "version": "2.6.1",
                "path": self.nix_path_of_nixpkgs("dnspython", "2.6.1"),
            },
            {
                "name": "dulwich",
                "version": "0.21.7",
                "path": self.nix_path_of_nixpkgs("dulwich", "0.21.7"),
            },
            {
                "name": "esdbclient",
                "version": "1.1.3",
                "path": self.nix_path_of_rydnr_nix_flakes("esdbclient", "1.1.3.1"),
            },
            {
                "name": "gitdb",
                "version": "4.0.11",
                "path": self.nix_path_of_nixpkgs("gitdb", "4.0.11"),
            },
            {
                "name": "GitPython",
                "version": "3.1.43",
                "path": self.nix_path_of_nixpkgs("GitPython", "3.1.43"),
            },
            {
                "name": "grpcio",
                "version": "1.62.2",
                "path": self.nix_path_of_nixpkgs("grpcio", "1.62.2"),
            },
            {
                "name": "idna",
                "version": "3.7",
                "path": self.nix_path_of_nixpkgs("idna", "3.7"),
            },
            {
                "name": "installer",
                "version": "0.7.0",
                "path": self.nix_path_of_nixpkgs("installer", "0.7.0"),
            },
            {
                "name": "packaging",
                "version": "24.0",
                "path": self.nix_path_of_nixpkgs("packaging", "24.0"),
            },
            {
                "name": "paramiko",
                "version": "3.4.0",
                "path": self.nix_path_of_nixpkgs("paramiko", "3.4.0"),
            },
            {
                "name": "path",
                "version": "16.14.0",
                "path": self.nix_path_of_nixpkgs("path", "16.14.0"),
            },
            {
                "name": "poetry-core",
                "version": "1.9.0",
                "path": self.nix_path_of_nixpkgs("poetry-core", "1.9.0"),
            },
            {
                "name": "protobuf",
                "version": "4.24.4",
                "path": self.nix_path_of_nixpkgs("protobuf", "4.24.4"),
            },
            {
                "name": "pyasn1",
                "version": "0.6.0",
                "path": self.nix_path_of_nixpkgs("pyasn1", "0.6.0"),
            },
            {
                "name": "pycparser",
                "version": "2.22",
                "path": self.nix_path_of_nixpkgs("pycparser", "2.22"),
            },
            {
                "name": "PyGithub",
                "version": "2.3.0",
                "path": self.nix_path_of_nixpkgs("PyGithub", "2.3.0"),
            },
            {
                "name": "PyJWT",
                "version": "2.8.0",
                "path": self.nix_path_of_nixpkgs("pyjwt", "2.8.0"),
            },
            {
                "name": "PyNaCl",
                "version": "1.5.0",
                "path": self.nix_path_of_nixpkgs("pynacl", "1.5.0"),
            },
            {
                "name": "requests",
                "version": "2.31.0",
                "path": self.nix_path_of_nixpkgs("requests", "2.31.0"),
            },
            {
                "name": "semver",
                "version": "3.0.2",
                "path": self.nix_path_of_nixpkgs("semver", "3.0.2"),
            },
            {
                "name": "six",
                "version": "1.16.0",
                "path": self.nix_path_of_nixpkgs("six", "1.16.0"),
            },
            {
                "name": "typing_extensions",
                "version": "4.11.0",
                "path": self.nix_path_of_nixpkgs("typing-extensions", "4.11.0"),
            },
            {
                "name": "unidiff",
                "version": "0.7.5",
                "path": self.nix_path_of_nixpkgs("unidiff", "0.7.5"),
            },
            {
                "name": "urllib3",
                "version": "2.2.1",
                "path": self.nix_path_of_nixpkgs("urllib3", "2.2.1"),
            },
            {
                "name": "wheel",
                "version": "0.43.0",
                "path": self.nix_path_of_nixpkgs("wheel", "0.43.0"),
            },
            {
                "name": "wrapt",
                "version": "1.16.0",
                "path": self.nix_path_of_nixpkgs("wrapt", "1.16.0"),
            },
        ]

    @classmethod
    def copy_dependency_to(cls, dep: Dict[str, str], dest: str):
        """
        Copies a dependency to a destination.
        :param dep: The dependency.
        :type dep: Dict[str, str]
        :param dest: The destination.
        :type dest: str
        """
        import os
        import shutil

        os.makedirs(dest, exist_ok=True)

        # List all subdirectories in the folder
        subdirs = next(os.walk(os.path.join(dep["path"], "lib")))[1]

        # Find the first subfolder that starts with "python"
        python_subfolder = next(
            (subdir for subdir in subdirs if subdir.startswith("python")), None
        )

        source_folder = os.path.join(
            dep["path"], "lib", python_subfolder, "site-packages"
        )

        destination_path = os.path.join(
            dest, os.path.basename(f'{dep["name"]}-{dep["version"]}')
        )
        shutil.copytree(source_folder, destination_path)

    @classmethod
    def copy_dependencies_to(cls, deps: List[Dict[str, str]], dest: str):
        """
        Copies dependencies to a destination.
        :param deps: The dependencies.
        :type deps: List[Dict[str, str]]
        :param dest: The destination.
        :type dest: str
        """
        for dep in deps:
            LicdataArtifact.logger().info(f"Copying {dep['name']} to {dest}")
            cls.copy_dependency_to(dep, dest)

    def build_pythonpath(self) -> str:
        """
        Builds the PYTHONPATH.
        :return: Such path.
        :rtype: str
        """
        paths = [
            f'/home/site/wwwroot/python_deps/{dep["name"]}-{dep["version"]}'
            for dep in self.dependencies
        ]
        LicdataArtifact.logger().debug(f"PYTHONPATH: {':'.join(paths)}")
        return ":".join(paths)

    @classmethod
    @listen(DockerImageRequested)
    async def listen_DockerImageRequested(
        cls, event: DockerImageRequested
    ) -> DockerImageAvailable:
        """
        Gets notified of a DockerImageRequested event.
        Emits a DockerImageAvailable event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.DockerImageRequested
        :return: A request to build a Docker image.
        :rtype: pythoneda.shared.artifact.events.DockerImageAvailable
        """
        LicdataArtifact.logger().info(f"Received {event}")

        instance = cls.instance()

        instance.add_event(event)

        if instance.is_for_azure(event):
            return await instance.build_docker_image_for_azure(event)

        return DockerImageFailed(
            event.image_name,
            event.image_version,
            event.metadata,
            "Image not available",
            event.id + event.previous_event_ids,
        )

    def is_for_azure(self, event: DockerImageRequested) -> bool:
        """
        Determines if the event is for Azure.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.DockerImageRequested
        :return: True if the event is for Azure, False otherwise.
        :rtype: bool
        """
        return event.metadata.get("variant", None) == "azure"

    async def build_docker_image_for_azure(
        cls, event: DockerImageRequested
    ) -> DockerImageAvailable:
        """
        Fulfills the build of an Azure-tailored Docker image.
        Emits a DockerImageAvailable event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.DockerImageRequested
        :return: A request to build a Docker image.
        :rtype: pythoneda.shared.artifact.events.DockerImageAvailable
        """
        instance = cls.instance()

        azure_base_image_version = event.metadata.get("azure_base_image_version", "4")
        python_version = event.metadata.get("python_version", "3.11")

        # Create a temporary directory
        temp_dir = tempfile.TemporaryDirectory()

        cls.copy_dependencies_to(
            instance.dependencies, os.path.join(temp_dir.name, "python_deps")
        )

        # Write the Dockerfile content
        dockerfile_content = f"""
FROM mcr.microsoft.com/azure-functions/python:{azure_base_image_version}-python{python_version}

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/git

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    libssl-dev git libc-ares2 \
    && apt-get clean

# Set the working directory
WORKDIR /home/site/wwwroot

ADD python_deps/ .

RUN pip install --upgrade pip && pip install grpcio

ENV FUNCTIONS_WORKER_RUNTIME python

ENV PYTHONPATH="${{PYTHONPATH}}:{instance.build_pythonpath()}/root/.local/lib/python{python_version}/site-packages"

EXPOSE 80
        """

        # Connect to Docker
        client = docker.from_env()

        # Desired image tag
        image_name = f"{event.image_name}-azure-{azure_base_image_version}-python{python_version.replace('.', '')}"
        image_version = event.image_version
        image_tag = f"{image_name}:{image_version}"

        # Create an in-memory tar archive with the Dockerfile
        fileobj = io.BytesIO()
        with tarfile.TarFile(fileobj=fileobj, mode="w") as tar:
            dockerfile_bytes = dockerfile_content.encode("utf-8")
            dockerfile_info = tarfile.TarInfo("Dockerfile")
            dockerfile_info.size = len(dockerfile_bytes)
            tar.addfile(dockerfile_info, io.BytesIO(dockerfile_bytes))
            tar.add(temp_dir.name, arcname="python_deps")

        # Reset the file pointer to the beginning
        fileobj.seek(0)

        # Build the image using the Docker SDK
        image, build_logs = client.images.build(
            fileobj=fileobj, custom_context=True, rm=True, tag=image_tag
        )

        # Optional: Print build logs
        for chunk in build_logs:
            if "stream" in chunk:
                LicdataArtifact.logger().debug(chunk["stream"].strip())

        LicdataArtifact.logger().info(f"Image '{image_tag}' built successfully.")

        result = DockerImageAvailable(
            image_name,
            image_version,
            f"localhost:5000/{image_tag}",
            event.metadata,
            event.id,
            None,
        )

        instance.add_event(result)

        return result

    @classmethod
    @listen(CredentialProvided)
    async def listen_CredentialProvided(
        cls, event: CredentialProvided
    ) -> DockerImagePushed:
        """
        Gets notified of a CredentialProvided event.
        :param event: The event.
        :type event: pythoneda.shared.runtime.secrets.events.CredentialProvided
        """
        return await cls.instance().resume(event)

    async def continue_flow(
        self, event: CredentialProvided, previousEvent: CredentialRequested
    ):
        """
        Continues the flow with a new event.
        :param event: The event.
        :type event: pythoneda.shared.runtime.secrets.events.CredentialProvided
        :param previousEvent: The previous event.
        :type event: pythoneda.shared.runtime.secrets.events.CredentialRequested
        """
        self.__class__.logger().info(
            f"Credential available: {event.name} ({event.metadata})"
        )

        docker_image_available = self.find_latest_event(DockerImageAvailable)

        return await self.push_docker_image_for_azure(docker_image_available)

    async def push_docker_image_for_azure(
        cls, event: DockerImageAvailable
    ) -> DockerImagePushed:
        """
        Pushes the Docker image.
        Returns a DockerImagePushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.DockerImageAvailable
        :return: A request to build a Docker image.
        :rtype: pythoneda.shared.artifact.events.DockerImagePushed
        """
        instance = cls.instance()

        print(
            f"TODO: push the image {event.image_name} to the registry {event.metadata.get('registry_url', None)}"
        )


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
