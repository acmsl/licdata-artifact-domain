# vim: set fileencoding=utf-8
"""
org/acmsl/artifact/licdata/infrastructure/dbus/dbus_docker_image_available.py

This file defines the DbusDockerImageAvailable class.

Copyright (C) 2024-today acmsl's licdata-artifact

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
from dbus_next import Message
from dbus_next.service import ServiceInterface, signal
import json
from pythoneda.shared import BaseObject
from org.acmsl.artifact.licdata.infrastructure.dbus import DBUS_PATH
from typing import List


class DbusDockerImageAvailable(BaseObject, ServiceInterface):
    """
    D-Bus interface for DockerImageAvailable

    Class name: DbusDockerImageAvailable

    Responsibilities:
        - Define the d-bus interface for the DockerImageAvailable event.

    Collaborators:
        - None
    """

    def __init__(self):
        """
        Creates a new DbusDockerImageAvailable.
        """
        super().__init__("Licdata_Artifact_DockerImageAvailable")

    @signal()
    def DockerImageAvailable(self, name: "s", version: "s", "url": s):
        """
        Defines the DockerImageAvailable d-bus signal.
        :param name: The image name.
        :type name: str
        :param version: The version.
        :type version: str
        :param url: The url the image is available.
        :type url: str
        """
        pass

    @classmethod
    def path(cls) -> str:
        """
        Retrieves the d-bus path.
        :return: Such value.
        :rtype: str
        """
        return DBUS_PATH

    @classmethod
    def transform(cls, event: DockerImageAvailable) -> List[str]:
        """
        Transforms given event to signal parameters.
        :param event: The event to transform.
        :type event: org.acmsl.artifact.licdata.domain.DockerImageAvailable
        :return: The event information.
        :rtype: List[str]
        """
        return [event.name, event.version, event.url, event.id, json.dumps(event.previous_event_ids)]

    @classmethod
    def sign(cls, event: DockerImageAvailable) -> str:
        """
        Retrieves the signature for the parameters of given event.
        :param event: The domain event.
        :type event: org.acmsl.artifact.licdata.domain.DockerImageAvailable
        :return: The signature.
        :rtype: str
        """
        return "sssss"

    @classmethod
    def parse(cls, message: Message) -> DockerImageAvailable:
        """
        Parses given d-bus message containing a DockerImageAvailable event.
        :param message: The message.
        :type message: dbus_next.Message
        :return: The DockerImageAvailable event.
        :rtype: org.acmsl.artifact.licdata.domain.DockerImageAvailable
        """
        name, version, url, event_id, prev_event_ids = message.body
        return DockerImageAvailable(name, version, url, None, event_id, json.loads(prev_event_ids))


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
