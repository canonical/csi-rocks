#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

import logging

from k8s_test_harness import harness
from k8s_test_harness.util import env_util, k8s_util

LOG = logging.getLogger(__name__)

NFSPLUGIN_IMG = "ghcr.io/canonical/nfsplugin:4.7.0-ck2"


def _get_nfsplugin_csi_helm_cmd():
    image_tuples = [
        # (rock_name, version, helm_image_subitem)
        ("csi-provisioner", "4.0.0", "csiProvisioner"),
        ("livenessprobe", "2.12.0", "livenessProbe"),
        ("csi-node-driver-registrar", "2.10.0", "nodeDriverRegistrar"),
        ("snapshot-controller", "6.3.3", "externalSnapshotter"),
        ("csi-snapshotter", "6.3.3", "csiSnapshotter"),
    ]

    images = []
    for rock_name, version, helm_image_subitem in image_tuples:
        rock = env_util.get_build_meta_info_for_rock_version(
            rock_name, version, "amd64"
        )
        images.append(k8s_util.HelmImage(rock.image, subitem=helm_image_subitem))

    images.append(k8s_util.HelmImage(NFSPLUGIN_IMG, subitem="nfs"))

    set_configs = [
        "externalSnapshotter.enabled=true",
    ]

    return k8s_util.get_helm_install_command(
        "csi-driver-nfs",
        "csi-driver-nfs",
        repository="https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/charts",
        chart_version="v4.7.0",
        images=images,
        set_configs=set_configs,
    )


def test_nfsplugin_integration(function_instance: harness.Instance):
    function_instance.exec(_get_nfsplugin_csi_helm_cmd())

    k8s_util.wait_for_daemonset(function_instance, "csi-nfs-node", "kube-system")
    k8s_util.wait_for_deployment(function_instance, "csi-nfs-controller", "kube-system")
    k8s_util.wait_for_deployment(function_instance, "snapshot-controller", "kube-system")
