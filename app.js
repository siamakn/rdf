// Path: webapp/app.js

const RDF_FOLDER = "RDF";
const FILTER_KEYS = [
  { key: "subject", prop: ["http://purl.org/dc/terms/subject", "dct:subject", "subject"] },
  { key: "keywords", prop: ["http://schema.org/keywords", "schema:keywords", "keywords"] },
  { key: "level", prop: ["http://schema.org/educationalLevel", "schema:educationalLevel", "educationalLevel"] },
  { key: "method", prop: ["http://purl.org/dc/terms/instructionalMethod", "dct:instructionalMethod", "instructionalMethod"] },
  { key: "type", prop: ["http://schema.org/learningResourceType", "schema:learningResourceType", "learningResourceType"] },
];

let allResources = [];

async function loadResources() {
  const files = await fetchFileList();

  for (const file of files) {
    try {
      const res = await fetch(`${RDF_FOLDER}/${file}`);
      const data = await res.json();
      const resource = Array.isArray(data["@graph"]) ? data["@graph"][0] : data;
      allResources.push(resource);
    } catch (e) {
      console.error("Error loading", file, e);
    }
  }

  buildDropdowns();
  renderResults(allResources);
}

/*
async function fetchFileList() {
  const res = await fetch(`${RDF_FOLDER}/`);
  const html = await res.text();
  const matches = html.match(/href="([^?][^\"]+\.jsonld)"/g) || [];
  return matches.map(m => m.replace(/href="/, "").replace(/"/, ""));
}
*/

async function fetchFileList() {
  const res = await fetch(`${RDF_FOLDER}/filelist.json`);
  const json = await res.json();
  return json;
}


function getValue(obj, keys) {
  for (const key of keys) {
    if (obj[key]) return obj[key];
  }
  return undefined;
}

function buildDropdowns(filteredResources = allResources) {
  FILTER_KEYS.forEach(({ key, prop }) => {
    const values = new Set();
    filteredResources.forEach(res => {
      const val = getValue(res, prop);
      if (Array.isArray(val)) val.forEach(v => values.add(v));
      else if (val) values.add(val);
    });

    const select = document.getElementById(key);
    const currentValue = select.value;
    select.innerHTML = '<option value="">-- Any --</option>';
    Array.from(values).sort().forEach(v => {
      const opt = document.createElement("option");
      opt.value = v;
      opt.textContent = v;
      select.appendChild(opt);
      if (v === currentValue) {
        opt.selected = true;
      }
    });
  });
}

function applyFilters() {
  const filters = {};
  FILTER_KEYS.forEach(({ key }) => {
    const val = document.getElementById(key).value;
    if (val) filters[key] = val;
  });

  const filtered = allResources.filter(res => {
    return FILTER_KEYS.every(({ key, prop }) => {
      if (!filters[key]) return true;
      const val = getValue(res, prop);
      if (Array.isArray(val)) return val.includes(filters[key]);
      return val === filters[key];
    });
  });

  renderResults(filtered);
  buildDropdowns(filtered);
}

function renderResults(results) {
  const container = document.getElementById("results");
  document.getElementById("results-count").textContent = `Showing ${results.length} resource(s)`;
  container.innerHTML = "";

  if (results.length === 0) {
    container.textContent = "No results match your filters.";
    return;
  }

  results.forEach((res, index) => {
    const title = getValue(res, ["http://schema.org/name", "schema:name", "dct:title"]) || "No Title";
    const desc = getValue(res, ["http://schema.org/description", "schema:description", "dct:description"]) || "No description.";
    const link = getValue(res, ["http://schema.org/url", "schema:url", "identifier", "http://schema.org/identifier"]) || "#";
    const subject = getValue(res, ["http://purl.org/dc/terms/subject", "dct:subject", "subject"]) || "No subject";
    const keywords = getValue(res, ["http://schema.org/keywords", "schema:keywords", "keywords"]) || [];
    const level = getValue(res, ["http://schema.org/educationalLevel", "schema:educationalLevel", "educationalLevel"]) || "Unspecified";
    const modified = getValue(res, ["http://schema.org/dateModified", "schema:dateModified", "dateModified"]) || "Unknown";

    const keywordStr = Array.isArray(keywords) ? keywords.join(", ") : keywords;

    const div = document.createElement("div");
    div.className = "result-card";
    div.innerHTML = `
      <h3><strong>${title}</strong></h3>
      <p><a href="${link}" target="_blank">${link}</a></p>
      <p><em>Subject:</em> ${subject}</p>
      <p><em>Keywords:</em> ${keywordStr}</p>
      <span class="badge">Level: ${level}</span>
      <span class="badge">Last Modified: ${modified}</span>
      <br><br>
      <button class="desc-toggle" onclick="openModal(${index})">Description</button>
    `;
    container.appendChild(div);

    // Hidden modal element
    const modal = document.createElement("div");
    modal.className = "modal";
    modal.id = `modal-${index}`;
    modal.innerHTML = `
      <div class="modal-content">
        <span class="close" onclick="closeModal(${index})">&times;</span>
        <p>${desc}</p>
      </div>
    `;
    document.body.appendChild(modal);
  });
}

function openModal(index) {
  document.getElementById(`modal-${index}`).style.display = "block";
}

function closeModal(index) {
  document.getElementById(`modal-${index}`).style.display = "none";
}

loadResources();

FILTER_KEYS.forEach(({ key }) => {
  const select = document.getElementById(key);
  select.addEventListener("change", applyFilters);
});
