## Overview
This document provides an analysis of CSI ROCK's cryptographic implementation with respect to FIPS 140 compliance requirements.

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

## Manual build and test

To manually build the FIPS-compliant ROCK images you need an Ubuntu Pro token. Once obtained, you can follow these intructions:

1. **Prerequisites**:
  - `rockcraft` version that contains the pro feature (see [this discourse post]).

2. **Build Command**:

  ```bash
  sudo rockcraft pack --pro=fips-updates
  ```

<!-- LINKS -->

[Go toolchain from Microsoft]: https://github.com/microsoft/go/blob/microsoft/release-branch.go1.23/eng/doc/fips/README.md
[this discourse post]: https://discourse.ubuntu.com/t/build-rocks-with-ubuntu-pro-services/57578
