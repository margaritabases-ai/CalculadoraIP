document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
  });
});

document.getElementById("cidr-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errBox = document.getElementById("cidr-error");
  const resBox = document.getElementById("cidr-result");
  errBox.classList.add("hidden");

  const payload = {
    ip: document.getElementById("cidr-ip").value,
    mask: document.getElementById("cidr-mask").value,
  };

  const resp = await fetch("/api/cidr", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const json = await resp.json();

  if (!json.ok) {
    resBox.classList.add("hidden");
    errBox.textContent = json.error;
    errBox.classList.remove("hidden");
    return;
  }

  const d = json.data;
  const rows = [
    ["Dirección de Red", `${d.network}/${d.prefix}`],
    ["Máscara Decimal", `${d.mask_dotted} (/${d.prefix})`],
    ["Rango de Hosts Válidos", `${d.first_host} - ${d.last_host}`],
    ["Dirección de Broadcast", d.broadcast],
    ["Hosts Disponibles", `${d.usable_hosts} (Total bloque: ${d.total_addresses})`],
    ["Red (Binario)", d.binary_network],
    ["Máscara (Binario)", d.binary_mask],
    ["Broadcast (Binario)", d.binary_broadcast],
  ];

  document.getElementById("cidr-tbody").innerHTML = rows
    .map(([k, v]) => `<tr><th>${k}</th><td class="mono">${v}</td></tr>`)
    .join("");
  resBox.classList.remove("hidden");
});

const subnetsList = document.getElementById("subnets-list");

function addSubnetRow(name = "", hosts = "") {
  const row = document.createElement("div");
  row.className = "subnet-row";
  row.innerHTML = `
    <input type="text" class="sub-name" placeholder="Nombre (ej. Subred A)" value="${name}" required />
    <input type="number" class="sub-hosts" placeholder="Hosts requeridos" min="1" value="${hosts}" required />
    <button type="button" class="btn-danger">Quitar</button>
  `;
  row.querySelector("button").addEventListener("click", () => row.remove());
  subnetsList.appendChild(row);
}

[
  ["Subred A", 100],
  ["Subred B", 50],
  ["Subred C", 25],
  ["Subred D", 10],
].forEach(([n, h]) => addSubnetRow(n, h));

document.getElementById("add-subnet-btn").addEventListener("click", () => addSubnetRow());

document.getElementById("vlsm-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errBox = document.getElementById("vlsm-error");
  const resBox = document.getElementById("vlsm-result");
  errBox.classList.add("hidden");

  const subnets = Array.from(document.querySelectorAll(".subnet-row")).map((row) => ({
    name: row.querySelector(".sub-name").value,
    hosts: row.querySelector(".sub-hosts").value,
  }));

  const resp = await fetch("/api/vlsm", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      base_cidr: document.getElementById("vlsm-base").value,
      subnets,
    }),
  });
  const json = await resp.json();

  if (!json.ok) {
    resBox.classList.add("hidden");
    errBox.textContent = json.error;
    errBox.classList.remove("hidden");
    return;
  }

  const d = json.data;
  document.getElementById("vlsm-summary").textContent =
    `Red Base: ${d.base_network} | Usadas: ${d.used_addresses}/${d.total_addresses} direcciones | ` +
    `Libres: ${d.remaining_addresses} (Siguiente IP libre: ${d.next_free_ip})`;

  document.getElementById("vlsm-tbody").innerHTML = d.allocations
    .map(
      (a) => `
      <tr>
        <td><strong>${a.name}</strong></td>
        <td>${a.required_hosts}</td>
        <td class="mono">${a.network}/${a.prefix}</td>
        <td class="mono">${a.mask_dotted} (/${a.prefix})</td>
        <td class="mono">${a.first_host} - ${a.last_host}</td>
        <td class="mono">${a.broadcast}</td>
        <td>${a.usable_hosts}</td>
        <td>${a.wasted_hosts}</td>
      </tr>`
    )
    .join("");

  resBox.classList.remove("hidden");
});