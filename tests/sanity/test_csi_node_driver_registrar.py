#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

import pytest
from k8s_test_harness.util import docker_util, env_util


@pytest.mark.parametrize("image_version", ("2.9.2", "2.10.0", "2.11.1"))
def test_csi_node_driver_registrar_rock(image_version):
    """Test csi-node-driver-registrar rock."""
    rock = env_util.get_build_meta_info_for_rock_version(
        "csi-node-driver-registrar", image_version, "amd64"
    )
    image = rock.image

    # check binary.
    process = docker_util.run_in_docker(image, ["/csi-node-driver-registrar", "--help"])
    assert "Usage of /csi-node-driver-registrar" in process.stderr
