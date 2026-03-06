<script setup>
import * as dc from "dc";
import * as d3 from "d3";
import cloud from "d3-cloud";
import crossfilter from "crossfilter2";
import "dc/dist/style/dc.css";
import "dc/src/compat/d3v6";
import { onMounted, ref, watch } from "vue";
import { fetchTradeDataset } from "./apiConnector";

let assetPie, sideRow, optionRow, currencyRow, recordTypeRow, pbMapRow, pmRow;
let tickerDim;
let ndx;

const tradeDate = ref("");

const fromDate = ref("");
const toDate = ref("");
const useRange = ref(false);

//default 'to' date
function getYesterdayDate() {
  const date = new Date();
  date.setDate(date.getDate() - 1);
  return date.toISOString().split("T")[0];
}

onMounted(async () => {
  window.dc = dc;

  toDate.value = getYesterdayDate();

  let dataset = await fetchTradeDataset(null, toDate.value);

  tradeDate.value = dataset[0]?.trade_date || "N/A";

  // selectedTradeDate.value = tradeDate.value;

  ndx = crossfilter(dataset);

  const W = (id) => {
    const el = document.querySelector(id);
    if (!el || !el.parentElement) return 250;
    return el.parentElement.getBoundingClientRect().width - 20;
  };

  // 1. asset-type trade capture
  const assetDim = ndx.dimension((d) => d.asset_type);
  const assetGroup = assetDim.group().reduceCount();

  assetPie = dc.pieChart("#asset-type-wise");

  assetPie
    .width(W("#asset-type-wise"))
    .height(220)
    .radius(90)
    .dimension(assetDim)
    .group(assetGroup)

    .label((d) => `${d.key} (${d.value})`)
    .title((d) => `${d.key}: ${d.value} trades`);

  // 2. side-wise trade capture
  const sideDim = ndx.dimension((d) => d.side);
  const sideGroup = sideDim.group().reduceCount();

  sideRow = dc.rowChart("#side-type-wise");

  window.sideRow = sideRow;

  sideRow
    .width(W("#side-type-wise"))
    .height(220)
    .margins({ top: 10, right: 10, bottom: 20, left: 50 })
    .dimension(sideDim)
    .group(sideGroup)
    .elasticX(true)

    .label((d) => `${d.key} (${d.value})`)
    .title((d) => `${d.key}: ${d.value}`);

  // 3. option-type wise trade capture
  const optionDim = ndx.dimension((d) => d.option_type ?? "N/A");
  const optionGroup = optionDim.group().reduceCount();

  optionRow = dc.rowChart("#option-type-wise");

  window.optionRow = optionRow;

  optionRow
    .width(W("#option-type-wise"))
    .height(220)
    .margins({ top: 10, right: 10, bottom: 20, left: 50 })

    .dimension(optionDim)
    .group(optionGroup)

    .elasticX(true)

    .label((d) => `${d.key} (${d.value})`)
    .title((d) => `${d.key}: ${d.value}`);

  // 4. currency wise trade capture
  const currencyDim = ndx.dimension((d) => d.issue_ccy);
  const currencyGroup = currencyDim.group().reduceCount();

  currencyRow = dc.rowChart("#currency-type-wise");

  window.currencyRow = currencyRow;

  currencyRow
    .width(W("#currency-type-wise"))
    .height(220)
    .margins({ top: 10, right: 10, bottom: 20, left: 50 })

    .dimension(currencyDim)
    .group(currencyGroup)
    .elasticX(true)

    .label((d) => `${d.key} (${d.value})`)
    .title((d) => `${d.key}: ${d.value}`);

  // 5. record-type wise trade capture
  const recordTypeDim = ndx.dimension((d) => d.record_type);
  const recordTypeGroup = recordTypeDim.group().reduceCount();

  recordTypeRow = dc.rowChart("#record-type-wise");

  window.recordTypeRow = recordTypeRow;

  recordTypeRow
    .width(W("#record-type-wise"))
    .height(220)
    .margins({ top: 10, right: 10, bottom: 20, left: 50 })

    .dimension(recordTypeDim)
    .group(recordTypeGroup)
    .elasticX(true)

    .label((d) => `${d.key} (${d.value})`)
    .title((d) => `${d.key}: ${d.value}`);

  // 6. pb-map wise trade capture
  const pbMapDim = ndx.dimension((d) => d.pb_map);
  const pbMapGroup = pbMapDim.group().reduceCount();

  pbMapRow = dc.rowChart("#pb-map-wise");

  window.pbMapRow = pbMapRow;

  pbMapRow
    .width(W("#pb-map-wise"))
    .height(180)
    .margins({ top: 10, right: 10, bottom: 20, left: 50 })

    .dimension(pbMapDim)
    .group(pbMapGroup)
    .elasticX(true)

    .label((d) => `${d.key} (${d.value})`)
    .title((d) => `${d.key}: ${d.value}`);

  // 7. pm wise trade capture
  const pmDim = ndx.dimension((d) => d.pm);
  const pmGroup = pmDim.group().reduceCount();

  pmRow = dc.rowChart("#pm-wise");

  window.pmRow = pmRow;

  pmRow
    .width(W("#pm-wise"))
    .height(220)
    .margins({ top: 10, right: 10, bottom: 20, left: 50 })

    .dimension(pmDim)
    .group(pmGroup)
    .elasticX(true)

    .label((d) => `${d.key} (${d.value})`)
    .renderTitle(true)
    .title((d) => `${d.key}: ${d.value}`);

  // 8. ticker wise trade capture
  tickerDim = ndx.dimension((d) => d.ticker);
  const tickerGroup = tickerDim.group().reduceCount();

  window.tickerDim = tickerDim;

  const colorScale = d3.scaleOrdinal(d3.schemeCategory10);
  // wordCloud chart
  function renderWordCloud() {
    const width = W("#ticker");
    const height = 300;

    const container = d3.select("#ticker");
    container.selectAll("svg").remove();

    const data = tickerGroup.all().filter((d) => d.value > 0);

    if (!data.length) return;
    const max = d3.max(data, (d) => d.value);

    const fontSize = d3.scaleLinear().domain([0, max]).range([15, 60]);

    const layout = cloud()
      .size([width, height])
      .random(() => 0.5)
      .words(
        data.map((d) => ({
          text: d.key,
          size: fontSize(d.value),
          value: d.value,
        })),
      )
      .padding(5)
      .rotate(() => 0)
      .font("Arial")
      .fontSize((d) => d.size)
      .on("end", draw);

    layout.start();

    function draw(words) {
      const svg = container
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width / 2}, ${height / 2})`);

      svg
        .selectAll("text")
        .data(words)
        .enter()
        .append("text")
        .style("font-family", "Impact")
        .style("fill", (d) => colorScale(d.text))
        .style("cursor", "pointer")
        .style("font-size", (d) => d.size + "px")
        .attr("text-anchor", "middle")
        .attr(
          "transform",
          (d) => `translate(${d.x},${d.y}) rotate(${d.rotate})`,
        )
        .text((d) => d.text)

        .on("click", (event, d) => {
          if (
            tickerDim.hasCurrentFilter() &&
            tickerDim.currentFilter() === d.text
          ) {
            tickerDim.filter(null);
          } else {
            tickerDim.filter(d.text);
          }

          dc.redrawAll();

          const tickerReset = document.getElementById("ticker-reset");
          tickerReset.style.visibility = tickerDim.hasCurrentFilter()
            ? "visible"
            : "hidden";

          // handle reset-all visibility
          const anyFilterApplied =
            dc.chartRegistry.list().some((c) => c.hasFilter()) ||
            tickerDim.hasCurrentFilter();

          document.getElementById("reset-all").style.visibility =
            anyFilterApplied ? "visible" : "hidden";
        })

        .append("title")
        .text((d) => `${d.text}: ${d.value}`);
    }
  }

  window.renderWordCloud = renderWordCloud;

  // 9. Data Table
  const tableDim = ndx.dimension((d) => d.trade_date);

  const tcTable = dc.dataTable("#data-table");

  tcTable
    .dimension(tableDim)
    .section((d) => d.trade_date)
    .size(50)
    .columns([
      { label: "isin", format: (d) => (d.isin ? d.isin : "N/A") },
      "cusip",
      "account_number",
      "executing_broker",
      "settlement_date",
      "price",
      "quantity",
      "ticker",
      {
        label: "comm_amount",
        format: (d) => (d.comm_amount ? d.comm_amount : "N/A"),
      },
      "net_amount",
    ])
    .sortBy((d) => d.settlement_date)
    .order(d3.ascending);

  dc.renderAll();
  renderWordCloud();

  // Reset function for word cloud
  function resetWordCloud() {
    tickerDim.filterAll();
    dc.redrawAll();
    renderWordCloud();

    document.getElementById("ticker-reset").style.visibility = "hidden";

    const anyFilterApplied =
      dc.chartRegistry.list().some((c) => c.hasFilter()) ||
      tickerDim.hasCurrentFilter();

    document.getElementById("reset-all").style.visibility = anyFilterApplied
      ? "visible"
      : "hidden";
  }

  window.resetWordCloud = resetWordCloud;

  // Reset function for all charts
  function resetAllCharts() {
    dc.filterAll();
    tickerDim.filterAll();

    dc.renderAll();
    renderWordCloud();

    document.querySelectorAll(".reset").forEach((el) => {
      el.style.visibility = "hidden";
    });
  }

  window.resetAllCharts = resetAllCharts;

  dc.chartRegistry.list().forEach((chart) => {
    chart.on("filtered", function (chart) {
      renderWordCloud();

      // Helper function to toggle visibility of reset links
      const toggleVisibility = (element, condition) => {
        if (!element) return;
        element.style.visibility = condition ? "visible" : "hidden";
      };

      // Individual Chart Reset
      const individualReset = chart
        .root()
        .node()
        .parentNode.querySelector(".reset");

      toggleVisibility(individualReset, chart.hasFilter());

      // Reset All Charts
      const resetAllLink = document.getElementById("reset-all");

      const anyFilterApplied =
        dc.chartRegistry.list().some((c) => c.hasFilter()) ||
        tickerDim.hasCurrentFilter();

      toggleVisibility(resetAllLink, anyFilterApplied);
    });
  });
});

watch([fromDate, toDate, useRange], async () => {
  if (!toDate.value) return;

  let dataset;

  if (useRange.value) {
    dataset = await fetchTradeDataset(fromDate.value, toDate.value);
  } else {
    dataset = await fetchTradeDataset(null, toDate.value);
  }

  tradeDate.value = dataset[0]?.trade_date || "N/A";

  if (!ndx) return;

  ndx.remove();
  ndx.add(dataset);

  dc.redrawAll();
});
</script>

<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <div class="dashboard-left">
        <h2 class="dashboard-title">
          Dashboard
          <span class="trade-date">{{ fromDate }} - {{ toDate }} </span>
        </h2>
      </div>

      <!-- Date range selector -->
      <div class="dashboard-right date-range-container">
        <label v-if="useRange">
          From:
          <input type="date" v-model="fromDate" class="date-input" />
        </label>

        <label>
          To:
          <input type="date" v-model="toDate" class="date-input" />
        </label>

        <label class="range-checkbox">
          <input type="checkbox" v-model="useRange" />
          Range
        </label>
      </div>
    </div>
    <div class="dashboard-grid">
      <div class="card">
        <h3>Asset Wise</h3>
        <div id="asset-type-wise"></div>
      </div>

      <div class="card">
        <h3>
          Side Wise
          <a
            id="side-reset"
            class="reset"
            href="javascript:sideRow.filterAll();dc.redrawAll();"
            style="visibility: hidden"
          >
            reset
          </a>
        </h3>
        <div id="side-type-wise"></div>
      </div>

      <div class="card">
        <h3>
          Option Wise
          <a
            id="option-reset"
            class="reset"
            href="javascript:optionRow.filterAll();dc.redrawAll();"
            style="visibility: hidden"
            >reset</a
          >
        </h3>
        <div id="option-type-wise"></div>
      </div>

      <div class="card">
        <h3>
          Currency Wise
          <a
            id="currency-reset"
            class="reset"
            href="javascript:currencyRow.filterAll();dc.redrawAll();"
            style="visibility: hidden"
            >reset</a
          >
        </h3>
        <div id="currency-type-wise"></div>
      </div>

      <div class="card">
        <h3>
          Record Type Wise
          <a
            id="record-type-reset"
            class="reset"
            href="javascript:recordTypeRow.filterAll();dc.redrawAll();"
            style="visibility: hidden"
            >reset</a
          >
        </h3>
        <div id="record-type-wise"></div>
      </div>

      <div class="card">
        <h3>
          PB Map Wise
          <a
            id="pb-map-reset"
            class="reset"
            href="javascript:pbMapRow.filterAll();dc.redrawAll();"
            style="visibility: hidden"
            >reset</a
          >
        </h3>
        <div id="pb-map-wise"></div>
      </div>

      <div class="card">
        <h3>
          PM Wise
          <a
            id="pm-reset"
            class="reset"
            href="javascript:pmRow.filterAll();dc.redrawAll();"
            style="visibility: hidden"
            >reset</a
          >
        </h3>
        <div id="pm-wise"></div>
      </div>

      <div class="card span-2">
        <h3>
          Ticker Wise
          <a
            id="ticker-reset"
            class="reset"
            href="javascript:resetWordCloud();"
            style="visibility: hidden"
            >reset</a
          >
        </h3>
        <div id="ticker"></div>
      </div>

      <div class="card span-3">
        <h3>
          Data Table
          <a
            id="reset-all"
            class="reset"
            href="javascript:resetAllCharts();"
            style="visibility: hidden"
            >Reset All</a
          >
        </h3>
        <div id="data-table"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  padding: 10px 12px;
  width: 98%;
  max-width: 0 auto;
  overflow-x: hidden;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.dashboard-left {
  display: flex;
  align-items: center;
}

.date-range-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-input {
  padding: 5px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 13px;
}

.range-checkbox {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
}

.dashboard-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.dashboard-dropdown {
  padding: 6px 10px;
  border-radius: 4px;
  border: 1px solid #ccc;
  font-size: 14px;
  background-color: white;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.trade-date {
  font-size: 14px;
  margin-left: 16px;
  font-weight: 400;
}

.card {
  background-color: white;
  padding: 5px;
  border: 2px solid black;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.span-2 {
  grid-column: span 2;
}

.span-3 {
  grid-column: span 3;
}

.reset-link {
  font-size: 12px;
  color: blue;
  margin-left: 8px;
  visibility: hidden;
  cursor: pointer;
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .span-2 {
    grid-column: span 2;
  }

  .span-3 {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .span-2,
  .span-3 {
    grid-column: span 1;
  }
}

:deep(#data-table) {
  width: 100%;
  display: block;
}

:deep(#data-table table) {
  width: 100%;
  min-width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

:deep(#data-table th),
:deep(#data-table td) {
  width: calc(100% / 10);
  border: 1px solid #ccc;
  padding: 6px;
  text-align: left;
  word-break: break-word;
}

:deep(#data-table th) {
  background-color: #f2f2f2;
  font-weight: 600;
}

:deep(svg) {
  max-width: 100% !important;
}
</style>
