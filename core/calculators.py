import math
from dataclasses import dataclass
from typing import List, Tuple


def ip_to_int(ip_str: str) -> int:
    parts = ip_str.strip().split(".")
    if len(parts) != 4:
        raise ValueError(f"Formato IPv4 inválido: '{ip_str}'. Debe tener 4 octetos.")
    result = 0
    for part in parts:
        if not part.isdigit():
            raise ValueError(f"Octeto no numérico en '{ip_str}': '{part}'.")
        val = int(part)
        if val < 0 or val > 255:
            raise ValueError(f"Octeto fuera de rango (0-255) en '{ip_str}': {val}.")
        result = (result << 8) | val
    return result


def int_to_ip(ip_int: int) -> str:
    return ".".join(str((ip_int >> (8 * i)) & 0xFF) for i in reversed(range(4)))


def int_to_bin(ip_int: int) -> str:
    return ".".join(f"{(ip_int >> (8 * i)) & 0xFF:08b}" for i in reversed(range(4)))


def prefix_to_mask_int(prefix: int) -> int:
    if not (0 <= prefix <= 32):
        raise ValueError(f"Prefijo fuera de rango (0-32): /{prefix}")
    return (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF if prefix > 0 else 0


def mask_str_to_prefix(mask_str: str) -> int:
    mask_int = ip_to_int(mask_str)
    inv = (~mask_int) & 0xFFFFFFFF
    if (inv & (inv + 1)) != 0:
        raise ValueError(f"La máscara '{mask_str}' no tiene bits contiguos válidos.")
    return bin(mask_int).count("1")


def calculate_cidr(ip_input: str, mask_or_prefix: str = "") -> dict:
    ip_input = ip_input.strip()
    mask_or_prefix = mask_or_prefix.strip()

    if "/" in ip_input and not mask_or_prefix:
        ip_part, pref_part = ip_input.split("/", 1)
        if not pref_part.isdigit():
            raise ValueError(f"Prefijo inválido: '/{pref_part}'")
        prefix = int(pref_part)
    elif mask_or_prefix:
        ip_part = ip_input
        if mask_or_prefix.startswith("/"):
            mask_or_prefix = mask_or_prefix[1:]
        if mask_or_prefix.isdigit():
            prefix = int(mask_or_prefix)
        else:
            prefix = mask_str_to_prefix(mask_or_prefix)
    else:
        raise ValueError("Ingresa la IP con prefijo (ej. 192.168.10.0/24) o especifica una máscara.")

    ip_int = ip_to_int(ip_part)
    mask_int = prefix_to_mask_int(prefix)
    network_int = ip_int & mask_int
    block_size = 1 << (32 - prefix)
    broadcast_int = network_int + block_size - 1

    if prefix <= 30:
        first_host = int_to_ip(network_int + 1)
        last_host = int_to_ip(broadcast_int - 1)
        usable_hosts = block_size - 2
    elif prefix == 31:
        first_host = int_to_ip(network_int)
        last_host = int_to_ip(broadcast_int)
        usable_hosts = 2
    else:
        first_host = int_to_ip(network_int)
        last_host = int_to_ip(network_int)
        usable_hosts = 1

    return {
        "input_ip": int_to_ip(ip_int),
        "network": int_to_ip(network_int),
        "first_host": first_host,
        "last_host": last_host,
        "broadcast": int_to_ip(broadcast_int),
        "mask_dotted": int_to_ip(mask_int),
        "prefix": prefix,
        "usable_hosts": usable_hosts,
        "total_addresses": block_size,
        "binary_network": int_to_bin(network_int),
        "binary_mask": int_to_bin(mask_int),
        "binary_broadcast": int_to_bin(broadcast_int),
    }


@dataclass
class SubnetAllocation:
    name: str
    required_hosts: int
    network: str
    prefix: int
    mask_dotted: str
    first_host: str
    last_host: str
    broadcast: str
    usable_hosts: int
    wasted_hosts: int
    block_size: int


def calculate_vlsm(base_cidr: str, requirements: List[Tuple[str, int]]) -> dict:
    if "/" not in base_cidr:
        raise ValueError("La red base debe incluir prefijo CIDR (ej. 192.168.0.0/24).")
    if not requirements:
        raise ValueError("Debes agregar al menos una subred con hosts requeridos.")

    base_ip_str, base_pref_str = base_cidr.strip().split("/", 1)
    if not base_pref_str.isdigit():
        raise ValueError(f"Prefijo base inválido: '/{base_pref_str}'")

    prefix_base = int(base_pref_str)
    if not (0 <= prefix_base <= 30):
        raise ValueError("El prefijo de la red base debe estar entre /0 y /30.")

    base_ip_int = ip_to_int(base_ip_str)
    base_mask_int = prefix_to_mask_int(prefix_base)
    network_base = base_ip_int & base_mask_int
    total_base_space = 1 << (32 - prefix_base)
    base_limit = network_base + total_base_space

    cleaned_reqs = []
    for name, req_hosts in requirements:
        clean_name = name.strip() or "Subred"
        if not isinstance(req_hosts, int) or req_hosts <= 0:
            raise ValueError(f"La subred '{clean_name}' debe solicitar un entero positivo de hosts.")
        cleaned_reqs.append((clean_name, req_hosts))

    sorted_subnets = sorted(cleaned_reqs, key=lambda item: item[1], reverse=True)

    current_network = network_base
    allocations: List[SubnetAllocation] = []

    for name, req_hosts in sorted_subnets:
        needed_hosts = req_hosts + 2
        host_bits = max(2, math.ceil(math.log2(needed_hosts)))
        mask_bits = 32 - host_bits
        block_size = 1 << host_bits

        if current_network + block_size > base_limit:
            raise ValueError(
                f"Espacio insuficiente en {int_to_ip(network_base)}/{prefix_base}: "
                f"no cabe la subred '{name}' ({req_hosts} hosts, bloque de {block_size} direcciones)."
            )

        net_addr = current_network
        first_host = net_addr + 1
        broadcast = net_addr + block_size - 1
        last_host = broadcast - 1
        usable_hosts = block_size - 2
        wasted_hosts = usable_hosts - req_hosts

        allocations.append(
            SubnetAllocation(
                name=name,
                required_hosts=req_hosts,
                network=int_to_ip(net_addr),
                prefix=mask_bits,
                mask_dotted=int_to_ip(prefix_to_mask_int(mask_bits)),
                first_host=int_to_ip(first_host),
                last_host=int_to_ip(last_host),
                broadcast=int_to_ip(broadcast),
                usable_hosts=usable_hosts,
                wasted_hosts=wasted_hosts,
                block_size=block_size,
            )
        )
        current_network += block_size

    used_addresses = current_network - network_base
    remaining_addresses = total_base_space - used_addresses

    return {
        "base_network": f"{int_to_ip(network_base)}/{prefix_base}",
        "total_addresses": total_base_space,
        "used_addresses": used_addresses,
        "remaining_addresses": remaining_addresses,
        "next_free_ip": int_to_ip(current_network) if remaining_addresses > 0 else "Ninguna",
        "allocations": allocations,
    }