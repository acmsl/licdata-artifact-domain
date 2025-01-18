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
    DockerImagePushFailed,
    DockerImagePushRequested,
    DockerImageRequested,
)
from pythoneda.shared.git import GitClone, GitRepo
from pythoneda.shared.runtime.secrets.events import (
    CredentialProvided,
    CredentialRequested,
)
from pythoneda.shared.shell import AsyncShell
import shutil
import subprocess
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
    def urls(cls) -> List[str]:
        """
        Retrieves the urls.
        :return: Such urls.
        :rtype: List[str]
        """
        return [
            "https://github.com/acmsl-def/licdata-application",
            "https://github.com/acmsl-def/licdata-infrastructure",
            "https://github.com/acmsl-def/licdata-domain",
        ]

    def extract_repo_from_url(self, url: str) -> str:
        """
        Extracts the repository name from the url.
        :param url: The url.
        :type url: str
        :return: The repository name.
        :rtype: str
        """
        _, result = GitRepo.extract_repo_owner_and_repo_name(url)

        return result

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

    def copy_dependencies_to(self, dest: str):
        """
        Copies dependencies to a destination.
        :param dest: The destination.
        :type dest: str
        """
        for dep in self.dependencies:
            LicdataArtifact.logger().info(f"Copying {dep['name']} to {dest}")
            self.__class__.copy_dependency_to(dep, dest)

    async def clone_and_copy_repos_to(self, dest: str):
        """
        Clones and copies the repositories to a destination.
        :param dest: The destination.
        :type dest: str
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            repos_folder = await self.clone_artifacts(tmp_dir)
            shutil.copytree(repos_folder, dest)

    def build_pythonpath(self) -> str:
        """
        Builds the PYTHONPATH.
        :return: Such path.
        :rtype: str
        """
        paths = [
            f'/home/site/wwwroot/python_deps/{dep["name"]}-{dep["version"]}'
            for dep in self.dependencies
        ] + [
            f"/home/site/wwwroot/{self.extract_repo_from_url(url)}"
            for url in self.__class__.urls
        ]
        return ":".join(paths)

    async def clone_artifacts(self, rootFolder: str) -> str:
        """
        Clones the artifacts into given folder.
        :param rootFolder: The root folder.
        :type rootFolder: str
        :return: The folder of the cloned repository.
        :rtype: str
        """
        git_clone = GitClone(rootFolder)
        for url in self.__class__.urls:
            repo = self.extract_repo_from_url(url)
            (code, stdout, stderr) = await git_clone.clone(url, repo)

        return rootFolder

    @classmethod
    @listen(DockerImageRequested)
    async def listen_DockerImageRequested(
        cls, event: DockerImageRequested
    ) -> List[Event]:
        """
        Gets notified of a DockerImageRequested event.
        Emits a DockerImageAvailable event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.DockerImageRequested
        :return: A request to build a Docker image.
        :rtype: pythoneda.shared.artifact.events.DockerImageAvailable
        """
        result = []

        instance = cls.instance()

        instance.add_event(event)

        if instance.is_for_azure(event):
            docker_image_available = await instance.build_docker_image_for_azure(event)
            result.append(docker_image_available)
            instance.add_event(docker_image_available)
        else:
            result.append(
                DockerImageFailed(
                    event.image_name,
                    event.image_version,
                    event.metadata,
                    "Image not available",
                    [event.id] + event.previous_event_ids,
                )
            )

        for evt in result:
            instance.add_event(evt)

        return result

    @classmethod
    @listen(DockerImagePushRequested)
    async def listen_DockerImagePushRequested(
        cls, event: DockerImagePushRequested
    ) -> List[Event]:
        """
        Gets notified of a DockerImagePushRequested event.
        Emits a DockerImagePushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.DockerImagePushRequested
        :return: A request to build and push a Docker image.
        :rtype: pythoneda.shared.artifact.events.DockerImagePushed
        """
        result = []

        instance = cls.instance()

        instance.add_event(event)

        if instance.is_for_azure(event):
            docker_image_available = await instance.build_docker_image_for_azure(event)
            result.append(docker_image_available)
            instance.add_event(docker_image_available)
            if event.metadata.get("credential_name", None) is None:
                credential_requested = CredentialRequested(
                    event.metadata.get("credential_name", None),
                    event.metadata,
                    [docker_image_available.id]
                    + docker_image_available.previous_event_ids,
                )
                result.append(credential_requested)
            else:
                credential_provided = CredentialProvided(
                    event.metadata.get("credential_name", None),
                    event.metadata.get("credential_value", None),
                    event.metadata,
                    [docker_image_available.id]
                    + docker_image_available.previous_event_ids,
                )
                result.append(credential_provided)
        else:
            result.append(
                DockerImageFailed(
                    event.image_name,
                    event.image_version,
                    event.metadata,
                    "Image not available",
                    [event.id] + event.previous_event_ids,
                )
            )

        for evt in result:
            instance.add_event(evt)

        return result

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
        self, event: DockerImageRequested
    ) -> DockerImageAvailable:
        """
        Fulfills the build of an Azure-tailored Docker image.
        Emits a DockerImageAvailable event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.DockerImageRequested
        :return: A request to build a Docker image.
        :rtype: pythoneda.shared.artifact.events.DockerImageAvailable
        """
        azure_base_image_version = event.metadata.get("azure_base_image_version", "4")
        python_version = event.metadata.get("python_version", "3.12")

        # Create a temporary directory
        temp_dir = tempfile.TemporaryDirectory()

        # self.copy=dependencies_to(os.path.join(temp_dir.name, "python_deps"))

        licdata_folder = os.path.join(temp_dir.name, "licdata")
        await self.clone_and_copy_repos_to(licdata_folder)
        # await self.run_nix_build_in_artifacts_in(licdata_folder)
        # await self.copy_external_wheel_files(licdata_folder)

        add_content = "\n".join(
            [
                f"ADD licdata/{self.extract_repo_from_url(url)} /home/site/wwwroot/"
                for url in self.__class__.urls
            ]
        )

        # Write the Dockerfile content
        dockerfile_content = f"""
FROM ghcr.io/nixos/nix:latest as nix-store-base

FROM mcr.microsoft.com/azure-functions/python:{azure_base_image_version}-python{python_version}

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    AzureWebJobsFeatureFlags=EnableWorkerIndexing \
    FUNCTIONS_WORKER_RUNTIME=python \
    GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/git \
    NIX_INSTALLER_NO_PROMPT=1 \
    NIX_FIRST_BUILD_UID=30001 \
    NIX_BUILD_USERS=32 \
    PATH="/nix/var/nix/profiles/default/bin:$PATH" \
    NIX_PATH="nixpkgs=/nix/var/nix/profiles/per-user/root/channels/nixpkgs" \
    NIX_CONF_DIR="/etc/nix"

# Keeps Python from generating .pyc files in the container.
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update \\
 && apt-get install -y libssl-dev git libc-ares2 curl sudo xz-utils \\
 && apt-get clean \\
 && apt-get -qq remove --purge -y \\
 && apt-get -qq autoremove \\
 && rm -rf /tmp/* \\
 && for f in /var/log/*; do \\
        echo '' > $f; \\
    done \\
 && pip install --upgrade pip \\
 && pip install grpcio \\
 && mkdir -p /home/app/.config/nix \\
 && mkdir -p /home/site/wwwroot \\
 && chown -R app /home/ \\
 && echo 'app ALL=(ALL:ALL) NOPASSWD:SETENV: ALL' >> /etc/sudoers \\
 && chown -R app:app /home/app/.config \\
 && chsh -s /bin/bash app

USER app

RUN cd /tmp \\
 && curl -L https://nixos.org/nix/install -o install-nix.sh \\
 && sh install-nix.sh --daemon --yes \\
 && rm install-nix.sh \\
 && sudo sh -c "echo 'trusted-users = root app' >> /etc/nix/nix.conf" \\
 && sudo sh -c "echo 'allowed-users = *' >> /etc/nix/nix.conf" \\
 && sudo sh -c "echo 'sandbox = true' >> /etc/nix/nix.conf"

USER root

# Copy Nix setup from the previous stage
COPY --from=nix-store-base /nix/store /nix/store

USER app

ENV NIX_CONF_DIR=/home/app/.config/nix

RUN echo 'sandbox = true' >> /home/app/.config/nix/nix.conf \\
 && echo 'experimental-features = flakes nix-command' >> /home/app/.config/nix/nix.conf \\
 && (sudo /nix/var/nix/profiles/default/bin/nix-daemon &) \\
 && for url in {' '.join(map(lambda url: f'"{url}"', self.__class__.urls))}; do \\
      command cd /home/site/wwwroot \\
 &&   command git clone "$url" \\
 &&   command cd "${{url##*/}}" \\
 &&   command nix build \\
 &&   command cp result/dist/*.whl /home/site/wwwroot \\
 &&   find result/deps -name '*.whl' -exec pip install {{}} \\; \\
 &&   PYTHONEDA_NO_BANNER=1 command nix develop --impure -c bash -c "command pip freeze" | command grep -v PYTHONEDA | command grep -v WARNING >> /home/site/wwwroot/requirements_raw.txt; \\
    done \\
 && command sort /home/site/wwwroot/requirements_raw.txt > /home/site/wwwroot/requirements.txt \\
 && rm -f /home/site/wwwroot/requirements_raw.txt \\
 && (command pip install -r /home/site/wwwroot/requirements.txt || command echo -n '');

COPY function_app.py host.json Dockerfile /home/site/wwwroot/

EXPOSE 80
"""
        LicdataArtifact.logger().debug(dockerfile_content)

        host_json = {
            "version": "2.0",
            "logging": {
                "applicationInsights": {
                    "samplingSettings": {"isEnabled": True, "excludedTypes": "Request"}
                }
            },
            "extensionBundle": {
                "id": "Microsoft.Azure.Functions.ExtensionBundle",
                "version": "[4.*, 5.0.0)",
            },
        }
        local_settings_json = {
            "IsEncrypted": False,
            "Values": {
                "AzureWebJobsStorage": "",
                "FUNCTIONS_WORKER_RUNTIME": "python",
                "AzureWebJobsScriptRoot": "/home/site/wwwroot",
                "AzureFunctionsJobHost__Logging__Console__IsEnabled": "true",
                "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
            },
        }
        # requirements_txt = await self.build_aggregate_requirements_txt(licdata_folder)

        function_app_py = """
import azure.functions as func
from http_blueprint import bp

app = func.FunctionApp()

app.register_functions(bp)

"""

        client = docker.from_env()

        # Desired image tag
        image_name = f"{event.image_name}-azure-{azure_base_image_version}-python{python_version.replace('.', '')}"
        image_version = event.image_version
        image_tag = f"{image_name}:{image_version}"

        # Create an in-memory tar archive with the context used by docker build
        fileobj = io.BytesIO()
        with tarfile.TarFile(fileobj=fileobj, mode="w") as tar:
            dockerfile_bytes = dockerfile_content.encode("utf-8")
            dockerfile_info = tarfile.TarInfo("Dockerfile")
            dockerfile_info.size = len(dockerfile_bytes)
            tar.addfile(dockerfile_info, io.BytesIO(dockerfile_bytes))
            # tar.add(temp_dir.name, arcname="python_deps")
            # tar.add(licdata_folder, arcname="licdata")
            host_json_bytes = json.dumps(
                host_json, indent=4, ensure_ascii=False
            ).encode("utf-8")
            host_json_info = tarfile.TarInfo("host.json")
            host_json_info.size = len(host_json_bytes)
            tar.addfile(host_json_info, io.BytesIO(host_json_bytes))
            # local_settings_json_bytes = json.dumps(local_settings_json).encode("utf-8")
            # local_settings_json_info = tarfile.TarInfo("local.settings.json")
            # local_settings_json_info.size = len(local_settings_json_bytes)
            # tar.addfile(local_settings_json_info, io.BytesIO(local_settings_json_bytes))
            # requirements_txt_bytes = requirements_txt.encode("utf-8")
            # requirements_txt_info = tarfile.TarInfo("requirements.txt")
            # requirements_txt_info.size = len(requirements_txt_bytes)
            # tar.addfile(requirements_txt_info, io.BytesIO(requirements_txt_bytes))
            function_app_py_bytes = function_app_py.encode("utf-8")
            function_app_py_info = tarfile.TarInfo("function_app.py")
            function_app_py_info.size = len(function_app_py_bytes)
            tar.addfile(function_app_py_info, io.BytesIO(function_app_py_bytes))
            print(tar.list())

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

        docker_registry_url = event.metadata.get(
            "docker_registry_url", "localhost:5000"
        )
        local_image = f"{image_name}:{image_version}"

        result = DockerImageAvailable(
            image_name,
            image_version,
            f"{docker_registry_url}/{local_image}",
            event.metadata,
            [event.id] + event.previous_event_ids,
        )

        self.add_event(result)

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
        cls.instance().add_event(event)
        resumed = await cls.instance().resume(event)

        return resumed

    async def continue_flow(self, event: CredentialProvided) -> List[Event]:
        """
        Continues the flow with a new event.
        :param event: The event.
        :type event: pythoneda.shared.runtime.secrets.events.CredentialProvided
        :return: The resulting events.
        :rtype: List[pythoneda.shared.Event]
        """
        self.__class__.logger().info(
            f"Credential available: {event.name}/{event.value} ({event.metadata})"
        )

        docker_image_available = self.find_latest_event(DockerImageAvailable)

        return await self.push_docker_image_for_azure(docker_image_available, event)

    async def push_docker_image_for_azure(
        self,
        dockerImageAvailable: DockerImageAvailable,
        credentialProvided: CredentialProvided,
    ) -> DockerImagePushed:
        """
        Pushes the Docker image.
        Returns a DockerImagePushed event.
        :param dockerImageAvailable: The DockerImageAvailable event.
        :type dockerImageAvailable: pythoneda.shared.artifact.events.DockerImageAvailable
        :param credentialProvided: The CredentialProvided event.
        :type credentialProvided: pythoneda.shared.runtime.secrets.events.CredentialProvided
        :return: A request to build a Docker image.
        :rtype: pythoneda.shared.artifact.events.DockerImagePushed
        """
        result = None

        username = credentialProvided.name
        password = credentialProvided.value
        docker_registry_url = credentialProvided.metadata.get(
            "docker_registry_url", None
        )
        local_image = (
            f"{dockerImageAvailable.image_name}:{dockerImageAvailable.image_version}"
        )
        remote_image = f"{docker_registry_url}/{local_image}"
        LicdataArtifact.logger().info(f"Pushing {local_image} to {docker_registry_url}")

        # 1. Instantiate the Docker client from environment
        client = docker.from_env()

        try:
            # 3. Tag the local image with the registry's name
            image = client.images.get(local_image)
            image.tag(remote_image)

            auth_dict = {
                "username": username,
                "password": password,
                "registry": docker_registry_url,
            }
            # 4. Push the image
            push_logs = client.images.push(
                remote_image,
                stream=True,
                decode=True,
                auth_config=auth_dict,
            )

            for log_line in push_logs:
                # Each 'log_line' is a dict. Examples:
                # {'status': 'Pushing', 'progressDetail': {...}, ...}
                # {'errorDetail': {'message': 'unauthorized...'}, 'error': 'unauthorized...'}
                LicdataArtifact.logger().debug(f"Push log chunk: {log_line}")

                if "error" in log_line:
                    # Handle the error
                    error_msg = log_line["error"]
                    LicdataArtifact.logger().error(f"Push failed: {error_msg}")
                    result = DockerImagePushFailed(
                        dockerImageAvailable.image_name,
                        dockerImageAvailable.image_version,
                        remote_image,
                        docker_registry_url,
                        dockerImageAvailable.metadata,
                        [dockerImageAvailable.id, credentialProvided.id]
                        + dockerImageAvailable.previous_event_ids,
                    )
                    break
                else:
                    # Optional: handle or display status updates
                    status_msg = log_line.get("status")
                    if status_msg:
                        LicdataArtifact.logger().debug(status_msg)

            if result is None:
                result = DockerImagePushed(
                    dockerImageAvailable.image_name,
                    dockerImageAvailable.image_version,
                    remote_image,
                    docker_registry_url,
                    dockerImageAvailable.metadata,
                    [dockerImageAvailable.id, credentialProvided.id]
                    + dockerImageAvailable.previous_event_ids,
                )
                LicdataArtifact.logger().info(
                    f"Pushed {remote_image} to {docker_registry_url}"
                )
        except docker.errors.APIError as e:
            result = DockerImagePushFailed(
                dockerImageAvailable.image_name,
                dockerImageAvailable.image_version,
                remote_image,
                docker_registry_url,
                e,
                dockerImageAvailable.metadata,
                [dockerImageAvailable.id, credentialProvided.id]
                + dockerImageAvailable.previous_event_ids,
            )

        self.add_event(result)

        return result

    async def build_aggregate_requirements_txt(self, artifactsFolder: str) -> str:
        """
        Builds the requirements.txt content.
        :param artifactsFolder: The artifacts folder.
        :type artifactsFolder: str
        :return: Such content.
        :rtype: str
        """
        result = []

        for url in self.__class__.urls:
            repo = self.extract_repo_from_url(url)
            artifact_folder = os.path.join(artifactsFolder, repo)
            result.append(await self.build_requirements_txt(artifact_folder))

        return "\n".join(result)

    async def build_requirements_txt(
        self, artifactFolder: str, impure: bool = False
    ) -> str:
        """
        Builds the requirements.txt content.
        :param artifactFolder: The artifact folder.
        :type artifactFolder: str
        :param impure: Whether to run "nix develop" with the "--impure" flag.
        :type impure: bool
        :return: Such content.
        :rtype: str
        """
        result = None

        cmd = "pip freeze"
        LicdataArtifact.logger().debug(
            f'Launching "nix develop -c {cmd}" on {artifactFolder}'
        )
        args = ["command", "nix", "develop", "--impure", "-c", "bash", "-c", cmd]
        env = os.environ.copy()
        env["PYTHONEDA_NO_BANNER"] = "1"
        _, result, stderr = await AsyncShell(args, artifactFolder).run(env=env)

        LicdataArtifact.logger().debug(
            f'"nix develop -c {cmd}" finished ({result}) / {stderr}'
        )

        return result

    async def run_nix_build_in_artifacts_in(self, baseFolder: str) -> List[str]:
        """
        Runs "nix build" for all artifacts in given folder.
        :param baseFolder: The base folder.
        :type baseFolder: str
        :return: The results.
        :rtype: List[str]
        """
        result = []
        for url in self.__class__.urls:
            repo = self.extract_repo_from_url(url)
            artifact_folder = os.path.join(baseFolder, repo)
            result.append(await self.run_nix_build_in(artifact_folder))

        return result

    async def run_nix_build_in(self, artifactFolder: str) -> str:
        """
        Runs "nix build" in given folder.
        :param artifactFolder: The artifact folder.
        :type artifactFolder: str
        :return: The stdout.
        :rtype: str
        """
        LicdataArtifact.logger().debug(f'Launching "nix build" in {artifactFolder}')
        args = ["command", "nix", "build"]
        env = os.environ.copy()
        env["PYTHONEDA_NO_BANNER"] = "1"
        process, result, stderr = await AsyncShell(args, artifactFolder).run(env=env)

        LicdataArtifact.logger().debug(f'"nix build finished ({result}) / {stderr}')

    async def copy_external_wheel_files(self, baseFolder: str):
        """
        Copies external wheel files so that they don't reside outside the root folder.
        :param baseFolder: The base folder.
        :type baseFolder: str
        """
        for url in self.__class__.urls:
            repo = self.extract_repo_from_url(url)
            artifact_folder = os.path.join(baseFolder, repo)
            pattern = os.path.join(artifact_folder, "result", "*.whl")
            for file_path in glob.glob(pattern):
                shutil.copy2(file_path, artifact_folder)


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
