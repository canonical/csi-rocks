#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

import logging
import pathlib

from k8s_test_harness import harness
from k8s_test_harness.util import constants, env_util, exec_util, k8s_util

LOG = logging.getLogger(__name__)

DIR = pathlib.Path(__file__).absolute().parent
MANIFESTS_DIR = DIR / ".." / "templates"


def _clone_helm_chart_repo(
    instance: harness.Instance, dest_path: pathlib.Path, version: str
):
    clone_command = [
        "git",
        "clone",
        "https://github.com/kubernetes-csi/csi-driver-nfs",
        "--depth",
        "1",
        str(dest_path.absolute()),
    ]
    instance.exec(clone_command)

    # The Helm chart deploys the CSI components with readOnlyRootFilesystem: true, not allowing
    # Pebble to run properly.
    templates_path = dest_path / "charts" / version / "csi-driver-nfs" / "templates"
    abs_path = str(templates_path.absolute())
    sed_str = "'s/readOnlyRootFilesystem: true/readOnlyRootFilesystem: false/g'"
    cmd = f"find {abs_path}/ -name '*.yaml' -exec sed -i -e {sed_str} {{}} \\;"  # noqa
    replace_command = ["bash", "-c", cmd]

    instance.exec(replace_command)


def _get_nfsplugin_csi_helm_cmd(chart_path: pathlib.Path):
    image_tuples = [
        # (rock_name, version, helm_image_subitem)
        ("csi-provisioner", "5.0.2", "csiProvisioner"),
        ("livenessprobe", "2.13.1", "livenessProbe"),
        ("csi-node-driver-registrar", "2.11.1", "nodeDriverRegistrar"),
        ("snapshot-controller", "6.3.3", "externalSnapshotter"),
        ("csi-snapshotter", "8.0.2", "csiSnapshotter"),
    ]

    images = []
    for rock_name, version, helm_image_subitem in image_tuples:
        rock = env_util.get_build_meta_info_for_rock_version(
            rock_name, version, "amd64"
        )
        images.append(k8s_util.HelmImage(rock.image, subitem=helm_image_subitem))

    set_configs = [
        "externalSnapshotter.enabled=true",
    ]

    return k8s_util.get_helm_install_command(
        "csi-driver-nfs",
        chart_name=str(chart_path.absolute()),
        chart_version="v4.7.0",
        images=images,
        set_configs=set_configs,
    )


def test_nfsplugin_integration(
    tmp_path: pathlib.Path, function_instance: harness.Instance
):
    version = "v4.7.0"
    clone_path = tmp_path / "csi-driver-nfs"
    chart_path = clone_path / "charts" / version / "csi-driver-nfs"

    _clone_helm_chart_repo(function_instance, clone_path, version)
    helm_command = _get_nfsplugin_csi_helm_cmd(chart_path)
    function_instance.exec(helm_command)

    # wait for all the components to become active.
    k8s_util.wait_for_daemonset(function_instance, "csi-nfs-node", "kube-system")
    k8s_util.wait_for_deployment(function_instance, "csi-nfs-controller", "kube-system")
    k8s_util.wait_for_deployment(
        function_instance, "snapshot-controller", "kube-system"
    )

    # call the nfsplugin's liveness probes to check that they're running as intended.
    for port in [29652, 29653]:
        # It has hostNetwork=true, which means that curling localhost should work.
        exec_util.stubbornly(retries=5, delay_s=5).on(function_instance).exec(
            ["curl", f"http://localhost:{port}/healthz"]
        )

    # Deploy a NFS server and an nginx Pod with a NFS volume attached.
    for item in ["nfs-server.yaml", "nginx-pod.yaml"]:
        manifest = MANIFESTS_DIR / item
        function_instance.exec(
            ["k8s", "kubectl", "apply", "-f", "-"],
            input=pathlib.Path(manifest).read_bytes(),
        )

    # Expect the Pod to become ready, and that it has the volume attached.
    k8s_util.wait_for_deployment(function_instance, "nfs-server")
    k8s_util.wait_for_resource(
        function_instance,
        "pod",
        "nginx-nfs-example",
        condition=constants.K8S_CONDITION_READY,
    )

    process = function_instance.exec(
        [
            "k8s",
            "kubectl",
            "exec",
            "nginx-nfs-example",
            "--",
            "bash",
            "-c",
            "findmnt /var/www -o TARGET,SOURCE,FSTYPE",
        ],
        capture_output=True,
        text=True,
    )

    assert "/var/www nfs-server.default.svc.cluster.local:/ nfs4" in process.stdout
