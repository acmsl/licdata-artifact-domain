# vim: set fileencoding=utf-8
"""
org/acmsl/artifact/licdata/domain/acmsl_licdata_infrastructure_nix_flake.py

This file defines the AcmslLicdataInfrastructureNixFlake class.

Copyright (C) 2025-today acmsl/licdata-artifact-domain

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
from .acmsl_licdata_events_nix_flake import AcmslLicdataEventsNixFlake
from .acmsl_licdata_domain_nix_flake import AcmslLicdataDomainNixFlake
from .acmsl_licdata_events_infrastructure_nix_flake import (
    AcmslLicdataEventsInfrastructureNixFlake,
)
from pythoneda.shared.nix.flake import (
    FlakeUtilsNixFlake,
    NixFlake,
    NixpkgsNixFlake,
    PythonedaSharedPythonlangBannerNixFlake,
    PythonedaSharedPythonlangDomainNixFlake,
    PythonedaSharedPythonlangInfrastructureNixFlake,
)


class AcmslLicdataInfrastructureNixFlake(NixFlake):
    """
    Nix flake for acmsl/licdata-domain

    Class name: AcmslLicdataInfrastructureNixFlake

    Responsibilities:
        - Provides a way to build acmsl/licdata-infrastructure

    Collaborators:
        - pythoneda.shared.nix.flake.NixFlake
    """

    def __init__(self, version: str):
        """
        Creates a new AcmslLicdataInfrastructureNixFlake instance.
        :param version: The version.
        :type version: str
        """
        super().__init__(
            "acmsl-licdata-infrastructure",
            version,
            "github:acmsl/licdata-infrastructure/{version}",
            [
                FlakeUtilsNixFlake.default(),
                NixpkgsNixFlake.default(),
                AcmslLicdataDomainNixFlake.default(),
                AcmslLicdataEventsNixFlake.default(),
                AcmslLicdataEventsInfrastructureNixFlake.default(),
                PythonedaSharedPythonlangBannerNixFlake.default(),
                PythonedaSharedPythonlangDomainNixFlake.default(),
                PythonedaSharedPythonlangInfrastructureNixFlake.default(),
            ],
            "pythoneda",
            "Licdata infrastructure",
            "https://github.com/acmsl/licdata-infrastructure",
            "gpl3",
            ["rydnr <github@acm-sl.org>"],
            2024,
            "rydnr",
        )

    @classmethod
    def default(cls) -> "AcmslLicdataInfrastructureNixFlake":
        """
        Retrieves the default version of the acmsl/licdata-infrastructure Nix flake .
        :return: Such instance.
        :rtype: org.acmsl.artifact.licdata.domain.AcmslLicdataInfrastructureNixFlake
        """
        return cls("0.0.24")


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
