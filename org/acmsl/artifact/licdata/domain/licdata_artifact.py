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
    Ports,
)
from pythoneda.shared.artifact.events import (
    DockerImageAvailable,
    DockerImagePushed,
    DockerImageRequested,
)
import tarfile
import tempfile


class LicdataArtifact(EventListener):
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
    @property
    def url(cls) -> str:
        """
        Retrieves the url.
        :return: Such url.
        :rtype: str
        """
        return "https://github.com/acmsl/licdata-artifact"

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

        # Create a temporary directory
        temp_dir = tempfile.TemporaryDirectory()

        # Define the path for the requirements.txt
        requirements_txt_path = os.path.join(temp_dir.name, "requirements.txt")

        # Write the Dockerfile content
        requirements_txt_content = """
azure-functions==1.21.3
bcrypt==4.1.2
brotlicffi==1.1.0.0
certifi==2024.2.2
cffi==1.16.0
charset-normalizer==3.3.2
coverage==7.4.4
cryptography==42.0.5
dbus_next==0.2.3
ddt==1.7.2
Deprecated==1.2.14
dnspython==2.6.1
dulwich==0.21.7
esdbclient==1.1.3
gitdb==4.0.11
GitPython==3.1.43
grpcio==1.62.2
idna==3.7
installer==0.7.0
packaging==24.0
paramiko==3.4.0
path==16.14.0
poetry-core==1.9.0
protobuf==4.24.4
pyasn1==0.6.0
pycparser==2.22
PyGithub==2.3.0
PyJWT==2.8.0
PyNaCl==1.5.0
requests==2.31.0
semver==3.0.2
six==1.16.0
typing_extensions==4.11.0
unidiff==0.7.5
urllib3==2.2.1
wheel==0.43.0
wrapt==1.16.0
        """

        # Write the Dockerfile content
        dockerfile_content = """
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/git


# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    libssl-dev git libc-ares2 \
    && apt-get clean

# Set the working directory
WORKDIR /home/site/wwwroot

ADD .deps/ .

COPY requirements.txt .

RUN pip install --upgrade pip && pip install grpcio && pip install --no-cache-dir -r requirements.txt --user

ENV FUNCTIONS_WORKER_RUNTIME python

ENV PYTHONPATH="${PYTHONPATH}:/root/.local/lib/python3.11/site-packages"

EXPOSE 80
        """

        # Connect to Docker
        client = docker.from_env()

        # Desired image tag
        image_tag = f"{event.image_name}:{event.image_version}"

        # Create an in-memory tar archive with the Dockerfile
        fileobj = io.BytesIO()
        with tarfile.TarFile(fileobj=fileobj, mode="w") as tar:
            dockerfile_bytes = dockerfile_content.encode("utf-8")
            dockerfile_info = tarfile.TarInfo("Dockerfile")
            dockerfile_info.size = len(dockerfile_bytes)
            tar.addfile(dockerfile_info, io.BytesIO(dockerfile_bytes))
            requirements_txt_bytes = requirements_txt_content.encode("utf-8")
            requirements_txt_info = tarfile.TarInfo("requirements.txt")
            requirements_txt_info.size = len(requirements_txt_bytes)
            tar.addfile(requirements_txt_info, io.BytesIO(requirements_txt_bytes))
            # TODO: Copy the dependencies somehow
            tar.add("/tmp/deps", arcname=".deps")

        # Reset the file pointer to the beginning
        fileobj.seek(0)

        print(f"type of client.images: {type(client.images)}")
        # Build the image using the Docker SDK
        image, build_logs = client.images.build(
            fileobj=fileobj, custom_context=True, rm=True, tag=image_tag
        )

        # Optional: Print build logs
        for chunk in build_logs:
            if "stream" in chunk:
                LicdataArtifact.logger().debug(chunk["stream"].strip())

        LicdataArtifact.logger().info(f"Image '{image_tag}' built successfully.")

        return DockerImageAvailable(
            event.image_name,
            event.image_version,
            None,
            event.id,
            event.previous_event_ids,
        )


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
