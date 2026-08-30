#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
workspace_root="$(cd -- "${script_dir}/../.." && pwd)"
armbian_dir="${workspace_root}/third_party/armbian-build"
patch_file="${script_dir}/0001-enable-ov5647-sun60iw2.patch"

if [[ ! -d "${armbian_dir}/.git" && ! -f "${armbian_dir}/.git" ]]; then
    printf 'Armbian submodule is not initialized: %s\n' "${armbian_dir}" >&2
    printf 'Run: git submodule update --init third_party/armbian-build\n' >&2
    exit 1
fi

if [[ ! -f "${patch_file}" ]]; then
    printf 'Patch file is missing: %s\n' "${patch_file}" >&2
    exit 1
fi

case "${1:-apply}" in
    --check)
        git -C "${armbian_dir}" apply --check "${patch_file}"
        printf 'Patch applies cleanly: %s\n' "${patch_file}"
        ;;
    apply)
        git -C "${armbian_dir}" apply --check "${patch_file}"
        git -C "${armbian_dir}" apply "${patch_file}"
        printf 'Patch applied: %s\n' "${patch_file}"
        ;;
    *)
        printf 'Usage: %s [apply|--check]\n' "$0" >&2
        exit 2
        ;;
esac
