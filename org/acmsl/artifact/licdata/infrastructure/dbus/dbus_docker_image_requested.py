# vim: set fileencoding=utf-8
"""
org/acmsl/artifact/licdata/infrastructure/dbus/dbus_docker_image_requested.py

This file defines the DbusDockerImageRequested class.

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


class DbusDockerImageRequested(BaseObject, ServiceInterface):
    """
    D-Bus interface for DockerImageRequested

    Class name: DbusDockerImageRequested

    Responsibilities:
        - Define the d-bus interface for the DockerImageRequested event.

    Collaborators:
        - None
    """

    def __init__(self):
        """
        Creates a new DbusDockerImageRequested.
        """
        super().__init__("Licdata_Artifact_DockerImageRequested")

    @signal()
    def DockerImageRequested(self, version: "s"):
        """
        Defines the DockerImageRequested d-bus signal.
        :param version: The version.
        :type version: str
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
    def transform(cls, event: DockerImageRequested) -> List[str]:
        """
        Transforms given event to signal parameters.
        :param event: The event to transform.
        :type event: org.acmsl.artifact.licdata.domain.DockerImageRequested
        :return: The event information.
        :rtype: List[str]
        """
        return [event.version, event.id, json.dumps(event.previous_event_ids)]

    @classmethod
    def sign(cls, event: DockerImageRequested) -> str:
        """
        Retrieves the signature for the parameters of given event.
        :param event: The domain event.
        :type event: org.acmsl.artifact.licdata.domain.DockerImageRequested
        :return: The signature.
        :rtype: str
        """
        return "sss"

    @classmethod
    def parse(cls, message: Message) -> DockerImageRequested:
        """
        Parses given d-bus message containing a DockerImageRequested event.
        :param message: The message.
        :type message: dbus_next.Message
        :return: The DockerImageRequested event.
        :rtype: org.acmsl.artifact.licdata.domain.DockerImageRequested
        """
        version, event_id, prev_event_ids = message.body
        return DockerImageRequested(version, None, event_id, json.loads(prev_event_ids))


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
