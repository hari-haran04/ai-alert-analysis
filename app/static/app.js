const samples = {
  trueAlert: {
    alertId: "ALT-1001",
    screeningType: "SANCTIONS",
    thirdParty: {
      entityId: "TP001",
      name: "Gold Mayning 000",
      country: "Russia",
      city: "Yakutsk",
      registrationNumber: "1201400007291",
      taxId: "1435353596",
    },
    hits: [
      {
        hitId: "HIT001",
        name: "Gold Mayning 000",
        country: "Russia",
        city: "Yakutsk",
        registrationNumber: "1201400007291",
        taxId: "1435353596",
        score: 100,
        level: "HIGH",
        listType: "US_50PLUS",
        source: "KHARON",
      },
      {
        hitId: "HIT002",
        name: "Sakha Gold Mayning AO",
        country: "Russia",
        city: "Aldan",
        score: 94,
        level: "MEDIUM",
        listType: "US_50PLUS",
        source: "KHARON",
      },
    ],
  },
  falsePositive: {
    alertId: "ALT-1002",
    screeningType: "SANCTIONS",
    thirdParty: {
      entityId: "TP002",
      name: "Michael Jordan",
      country: "USA",
      city: "Chicago",
      dateOfBirth: "1985-06-20",
      passportNumber: "P12345678",
    },
    hits: [
      {
        hitId: "HIT010",
        name: "Michael B Jordan",
        country: "USA",
        city: "New York",
        dateOfBirth: "1960-01-01",
        passportNumber: "P99999999",
        score: 85,
        level: "LOW",
        listType: "WATCHLIST",
        source: "FIRCO",
      },
    ],
  },
  missingData: {
    alertId: "ALT-1003",
    screeningType: "SANCTIONS",
    thirdParty: {
      entityId: "TP003",
      name: "ABC Trading Ltd",
      country: "UAE",
      city: "Dubai",
    },
    hits: [
      {
        hitId: "HIT020",
        name: "ABC Trading Limited",
        country: "UAE",
        city: "Dubai",
        score: 88,
        level: "MEDIUM",
        listType: "WATCHLIST",
        source: "FIRCO",
      },
    ],
  },
};

const $ = (id) => document.getElementById(id);

function setPayload(sample) {
  $("payload").value = JSON.stringify(sample, null, 2);
}

function badge(value) {
  return `<span class="badge ${String(value)}">${value}</span>`;
}

function percent(value) {
  return `${Math.round((value || 0) * 100)}%`;
}

function fieldLabel(value) {
  return String(value)
    .replace(/([A-Z])/g, " $1")
    .replace(/^./, (letter) => letter.toUpperCase());
}

function renderAnalysis(data) {
  $("emptyState").classList.add("hidden");
  $("results").classList.remove("hidden");
  $("resultSubhead").textContent = `${data.alertId} analyzed`;
  $("classification").innerHTML = badge(data.classification);
  $("confidence").textContent = `${data.confidence}%`;
  $("riskLevel").innerHTML = badge(data.riskLevel);
  $("bestHit").textContent = data.bestHit?.hitId || "-";
  $("summary").textContent = data.summary || data.complianceNotice || "";

  $("rankedHits").innerHTML = (data.rankedHits || [])
    .map(
      (hit) => `
        <div class="rank-row">
          <div>
            <strong>#${hit.rank} ${hit.hitId}</strong>
            <span>Candidate hit</span>
          </div>
          <div class="score-wrap" aria-label="Match score ${percent(hit.matchScore)}">
            <strong>${percent(hit.matchScore)}</strong>
            <div class="score-bar"><span style="width: ${percent(hit.matchScore)}"></span></div>
          </div>
        </div>
      `,
    )
    .join("");

  const bestHitId = data.bestHit?.hitId || "best hit";
  $("attributes").innerHTML = Object.entries(data.attributeAnalysis || {})
    .map(
      ([name, value]) => `
        <div class="attribute-row">
          <strong><span>${fieldLabel(name)}</span>${badge(value.result)}</strong>
          <p class="hit-context">Compared against ${bestHitId}</p>
          <p>${value.evidence}</p>
        </div>
      `,
    )
    .join("");

  const cases = data.historicalEvidence?.cases || [];
  $("historicalCases").innerHTML =
    cases.length === 0
      ? `<p class="muted">No meaningful historical cases found above the similarity threshold.</p>`
      : cases
          .map(
            (item) => `
              <article class="case-card">
                <div class="case-head">
                  <div>
                    <h4>${item.caseId}</h4>
                    <p>${item.summary || ""}</p>
                  </div>
                  <div class="case-score">
                    <strong>${percent(item.similarity)}</strong>
                    <span>Third-party similarity</span>
                  </div>
                </div>
                <div class="field-chip-row">
                  ${(item.fieldMatches || [])
                    .filter((match) => match.result !== "MISMATCH")
                    .slice(0, 5)
                    .map(
                      (match) =>
                        `<span class="field-chip">${fieldLabel(match.field)} ${percent(match.similarity)}</span>`,
                    )
                    .join("")}
                </div>
                <details>
                  <summary>View case details</summary>
                  <div class="case-detail-grid">
                    ${(item.fieldMatches || [])
                      .map(
                        (match) => `
                          <div>
                            <span>${fieldLabel(match.field)}</span>
                            ${badge(match.result)}
                            <strong>${percent(match.similarity)}</strong>
                          </div>
                        `,
                      )
                      .join("")}
                  </div>
                  <p class="muted">${(item.matchReasons || []).join(" · ")}</p>
                </details>
              </article>
            `,
          )
          .join("");

  $("actionsList").innerHTML = (data.recommendedActions || [])
    .map((action) => `<li>${action}</li>`)
    .join("");
}

async function analyze() {
  let payload;
  try {
    payload = JSON.parse($("payload").value);
  } catch (error) {
    alert(`Invalid JSON: ${error.message}`);
    return;
  }

  $("analyze").disabled = true;
  $("analyze").textContent = "Analyzing";
  try {
    const response = await fetch("/api/v1/alerts/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data?.error?.message || data?.detail || "Analysis failed");
    }
    renderAnalysis(data);
  } catch (error) {
    alert(error.message);
  } finally {
    $("analyze").disabled = false;
    $("analyze").textContent = "Analyze Alert";
  }
}

async function checkApi() {
  try {
    const response = await fetch("/health");
    $("apiStatus").textContent = response.ok ? "API online" : "API issue";
  } catch {
    $("apiStatus").textContent = "API offline";
  }
}

$("loadTrue").addEventListener("click", () => setPayload(samples.trueAlert));
$("loadFalse").addEventListener("click", () => setPayload(samples.falsePositive));
$("loadMissing").addEventListener("click", () => setPayload(samples.missingData));
$("formatJson").addEventListener("click", () => {
  try {
    $("payload").value = JSON.stringify(JSON.parse($("payload").value), null, 2);
  } catch (error) {
    alert(`Invalid JSON: ${error.message}`);
  }
});
$("analyze").addEventListener("click", analyze);

setPayload(samples.falsePositive);
checkApi();
