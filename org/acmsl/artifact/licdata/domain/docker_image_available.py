# vim: set fileencoding=utf-8
"""
org/acmsl/licdata/artifact/domain/docker_image_available.py

This file declares the DockerImageAvailable event.

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
from pythoneda.shared import Event, primary_key_attribute
from typing import List


class DockerImageAvailable(Event):
    """
    Represents the moment a Docker image is requested.

    Class name: DockerImageRequested

    Responsibilities:
        - Wraps all contextual information of the event.

    Collaborators:
        - None
    """

    def __init__(
        self,
        name: str,
        version: str,
        url: str,
        previousEventIds: List[str] = None,
        reconstructedId: str = None,
        reconstructedPreviousEventIds: List[str] = None,
    ):
        """
        Creates a new DockerImageRequested instance.
        :param name: The image name.
        :type name: str
        :param version: The image version.
        :type version: str
        :param url: The image URL.
        :type url: str
        :param previousEventIds: The id of previous events, if any.
        :type previousEventIds: List[str]
        :param reconstructedId: The id of the event, if it's generated externally.
        :type reconstructedId: str
        :param reconstructedPreviousEventIds: The id of the previous events, if an external event
        is being reconstructed.
        :type reconstructedPreviousEventIds: List[str]
        """
        super().__init__(
            previousEventIds, reconstructedId, reconstructedPreviousEventIds
        )
        self._name = name
        self._version = version
        self._url = url

    @property
    @primary_key_attribute
    def name(self) -> str:
        """
        The image name.
        """
        return self._name

    @property
    @primary_key_attribute
    def version(self) -> str:
        """
        The image version.
        """
        return self._version

    @property
    def url(self) -> str:
        """
        The image URL.
        """
        return self._url


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
