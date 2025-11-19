## Overview
This document provides an analysis of CSI ROCK's cryptographic implementation with respect to [FIPS 140-3] compliance requirements.

> **Note:** As of now, pebble is not built in a FIPS-compliant way. This document will be updated once it is.

## FIPS Compliance Status

To address the FIPS compliance for the CSI ROCKs, the following steps are required:

1. **Go Toolchain**: Must use the modified [Go toolchain from Microsoft] that links against FIPS-validated cryptographic modules.
2. **OpenSSL**: Must link against a FIPS-validated OpenSSL implementation.

**NOTE**: This ROCK is bundled with a FIPS-validated OpenSSL library which is described in the ROCK manifest (see [this discourse post]).
```yaml
...
parts:
  openssl:
    plugin: nil
    stage-packages:
      - openssl-fips-module-3
      - openssl
...
```

## Manual build

**Prerequisites**:

- a `rockcraft` version that allows building with Ubuntu Pro services (refer to [this discourse post]).

**Building the Image**:

Use the following command to build the image:

```bash
sudo rockcraft pack --pro=fips-updates
```

<!-- LINKS -->

[FIPS 140-3]: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.140-3.pdf
[Go toolchain from Microsoft]: https://github.com/microsoft/go/blob/microsoft/release-branch.go1.23/eng/doc/fips/README.md
[this discourse post]: https://discourse.ubuntu.com/t/build-rocks-with-ubuntu-pro-services/57578
