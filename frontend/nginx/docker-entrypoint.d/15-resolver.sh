#!/bin/sh
# Gera /tmp/nginx/resolver.conf com o primeiro DNS de /etc/resolv.conf.
# Funciona no Docker (127.0.0.11) e no Azure Container Apps sem configuração manual.
set -eu
mkdir -p /tmp/nginx
ns=$(awk '/^nameserver/ { print $2; exit }' /etc/resolv.conf)
if [ -z "${ns}" ]; then
    echo "15-resolver.sh: nenhum nameserver em /etc/resolv.conf" >&2
    exit 1
fi
case "${ns}" in
    *:*) ns="[${ns}]" ;;  # IPv6
esac
echo "resolver ${ns} valid=10s ipv6=off;" > /tmp/nginx/resolver.conf
