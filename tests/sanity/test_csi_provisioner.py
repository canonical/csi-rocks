#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

import pytest
from k8s_test_harness.util import docker_util, env_util


@pytest.mark.parametrize("image_version", ("3.6.4", "4.0.0", "4.0.1"))
def test_csi_provisioner_rock(image_version):
    """Test csi-provisioner rock."""
    rock = env_util.get_build_meta_info_for_rock_version(
        "csi-provisioner", image_version, "amd64"
    )
    image = rock.image

    # check binary.
    process = docker_util.run_in_docker(image, ["/csi-provisioner", "--help"], False)
    assert "Usage of /csi-provisioner" in process.stderr
