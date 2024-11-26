# vim: set fileencoding=utf-8
"""
org/acmsl/artifact/licdata/infrastructure/dbus/licdata_artifact_dbus_signal_listener.py

This file defines the LicdataArtifactDbusSignalListener class.

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
from org.acmsl.artifact.events.infrastructure.licdata.dbus import (
    DbusDockerImageRequested,
)
from org.acmsl.artifact.events.licdata import DockerImageRequested
from pythoneda.shared.infrastructure.dbus import DbusSignalListener
from typing import Dict


class LicdataArtifactDbusSignalListener(DbusSignalListener):
    """
    A PrimaryPort that listens to d-bus signals relevant to licdata-artifact.

    Class name: LicdataArtifactDbusSignalListener

    Responsibilities:
        - Connect to d-bus.
        - Listen to signals relevant to licdata-artifact.

    Collaborators:
        - pythoneda.shared.application.pythoneda.PythonEDA: Receives relevant domain events.
        - org.acmsl.artifact.events.infrastructure.licdata.dbus.DbusDockerImageRequested
    """

    def __init__(self):
        """
        Creates a new LicdataArtifactDbusSignalListener instance.
        """
        super().__init__("org.acmsl.artifact.events.infrastructure.licdata.dbus")

    def signal_receivers(self, app) -> Dict:
        """
        Retrieves the configured signal receivers.
        :param app: The PythonEDA instance.
        :type app: pythoneda.shared.application.PythonEDA
        :return: A dictionary with the signal name as key, and the tuple interface and bus type as the value.
        :rtype: Dict
        """
        result = {}
        key = self.__class__.full_class_name(DockerImageRequested)
        result[key] = DbusDockerImageRequested
        return result


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
