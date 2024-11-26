# vim: set fileencoding=utf-8
"""
org/acmsl/artifact/licdata/infrastructure/dbus/licdata_artifact_dbus_signal_emitter.py

This file defines the LicdataArtifactDbusSignalEmitter class.

Copyright (C) 2024-today acmsl's Licdata Artifact

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
from dbus_next import BusType
from org.acmsl.artifact.events.infrastructure.licdata.dbus import (
    DbusDockerImageAvailable,
)
from org.acmsl.artifact.events.licdata import DockerImageAvailable
from pythoneda.shared.infrastructure.dbus import DbusSignalEmitter
from typing import Dict


class LicdataArtifactDbusSignalEmitter(DbusSignalEmitter):
    """
    A Port that emits licdata-artifact events as d-bus signals.

    Class name: LicdataArtifactDbusSignalEmitter

    Responsibilities:
        - Connect to d-bus.
        - Emit licdata-artifact events as d-bus signals.

    Collaborators:
        - pythoneda.shared.application.PythonEDA: Requests emitting events.
        - org.acmsl.artifact.events.infrastructure.infrastructure.dbus.DbusDockerImageAvailable
    """

    def __init__(self):
        """
        Creates a new LicdataArtifactDbusSignalEmitter instance.
        """
        super().__init__()

    def signal_emitters(self) -> Dict:
        """
        Retrieves the configured event emitters.
        :return: For each event, a list with the event interface and the bus type.
        :rtype: Dict
        """
        result = {}
        key = self.__class__.full_class_name(DockerImageAvailable)
        result[key] = [DbusDockerImagesAvailable, BusType.SYSTEM]

        return result


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
