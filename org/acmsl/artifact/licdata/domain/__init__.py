# vim: set fileencoding=utf-8
"""
org/acmsl/artifact/licdata/domain/__init__.py

This file ensures org.acmsl.artifact.licdata.domain is a package.

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
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from .acmsl_licdata_events_nix_flake import AcmslLicdataEventsNixFlake
from .acmsl_licdata_events_infrastructure_nix_flake import (
    AcmslLicdataEventsInfrastructureNixFlake,
)
from .acmsl_licdata_domain_nix_flake import AcmslLicdataDomainNixFlake
from .acmsl_licdata_infrastructure_nix_flake import AcmslLicdataInfrastructureNixFlake
from .licdata_artifact import LicdataArtifact

# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
