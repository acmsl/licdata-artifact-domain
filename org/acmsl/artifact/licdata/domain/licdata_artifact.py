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
import json
from pythoneda.shared import (
    attribute,
    listen,
    sensitive,
    Event,
    EventEmitter,
    EventListener,
    Ports,
)
from org.acmsl.artifact.events.licdata import DockerImageAvailable, DockerImageRequested


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
        :type event: org.acmsl.artifact.events.licdata.DockerImageRequested
        :return: A request to build a Docker image.
        :rtype: org.acmsl.artifact.events.licdata.DockerImageAvailable
        """
        LicdataArtifact.logger().info(f"Received {event}")


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
