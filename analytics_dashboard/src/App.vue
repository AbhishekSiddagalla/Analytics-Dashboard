<script setup>
import * as d3 from "d3";
import crossfilter from "crossfilter2";
import * as dc from "dc";
import "dc/dist/style/dc.css";
import { onMounted, ref } from "vue";
import { fetchTradeDataset } from "./apiConnector";

let assetPie, sideRow, optionRow, currencyRow, recordTypeRow, pbMapRow, pmRow;

function attachReset(chart, selector) {
  chart.on("filtered", function () {
    const link = document.querySelector(selector);
    if (!link) return;

    link.style.visibility = chart.filters().length ? "visible" : "hidden";
  });
}

const tradeDate = ref("");

onMounted(async () => {
  const dataset = await fetchTradeDataset();

  tradeDate.value = dataset[0]?.trade_date || "N/A";

  const ndx = crossfilter(dataset);

  const W = (id) =>
    document.querySelector(id)?.parentElement.clientWidth || 300;

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

  sideRow
    .width(W("#side-type-wise"))
    .height(220)
    .margins({ top: 10, right: 10, bottom: 20, left: 50 })

    .dimension(sideDim)
    .group(sideGroup)

    .elasticX(true)
    .ordinalColors(["#4CAF50", "#F44336"])

    .label((d) => `${d.key} (${d.value})`)
    .title((d) => `${d.key}: ${d.value}`);

  // 3. option-type wise trade capture
  const optionDim = ndx.dimension((d) => d.option_type ?? "N/A");
  const optionGroup = optionDim.group().reduceCount();

  optionRow = dc.rowChart("#option-type-wise");

  optionRow
    .width(W("#option-type-wise"))
    .height(220)
    .margins({ top: 10, right: 10, bottom: 20, left: 50 })

    .dimension(optionDim)
    .group(optionGroup)

    .elasticX(true)
    .ordinalColors(["#4CAF50", "#F44336"])

    .label((d) => `${d.key} (${d.value})`)
    .title((d) => `${d.key}: ${d.value}`);

  // 4. currency wise trade capture
  const currencyDim = ndx.dimension((d) => d.issue_ccy);
  const currencyGroup = currencyDim.group().reduceCount();

  currencyRow = dc.rowChart("#currency-type-wise");

  currencyRow
    .width(W("#currency-type-wise"))
    .height(220)
    .margins({ top: 10, right: 10, bottom: 20, left: 50 })

    .dimension(currencyDim)
    .group(currencyGroup)

    .elasticX(true)
    .ordinalColors(["#4CAF50", "#F44336"])

    .label((d) => `${d.key} (${d.value})`)
    .title((d) => `${d.key}: ${d.value}`);

  // 5. record-type wise trade capture
  const recordTypeDim = ndx.dimension((d) => d.record_type);
  const recordTypeGroup = recordTypeDim.group().reduceCount();

  recordTypeRow = dc.rowChart("#record-type-wise");

  recordTypeRow
    .width(W("#record-type-wise"))
    .height(220)
    .margins({ top: 10, right: 10, bottom: 20, left: 50 })

    .dimension(recordTypeDim)
    .group(recordTypeGroup)

    .elasticX(true)
    .ordinalColors(["#4CAF50", "#F44336"])

    .label((d) => `${d.key} (${d.value})`)
    .title((d) => `${d.key}: ${d.value}`);

  // 6. pb-map wise trade capture
  const pbMapDim = ndx.dimension((d) => d.pb_map);
  const pbMapGroup = pbMapDim.group().reduceCount();

  pbMapRow = dc.rowChart("#pb-map-wise");

  pbMapRow
    .width(W("#pb-map-wise"))
    .height(180)
    .margins({ top: 10, right: 10, bottom: 20, left: 50 })

    .dimension(pbMapDim)
    .group(pbMapGroup)

    .elasticX(true)
    .ordinalColors(["#4CAF50", "#F44336"])

    .label((d) => `${d.key} (${d.value})`)
    .title((d) => `${d.key}: ${d.value}`);

  // 7. pm wise trade capture
  const pmDim = ndx.dimension((d) => d.pm);
  const pmGroup = pmDim.group().reduceCount();

  pmRow = dc.rowChart("#pm-wise");

  pmRow
    .width(W("#pm-wise"))
    .height(220)
    .margins({ top: 10, right: 10, bottom: 20, left: 50 })

    .dimension(pmDim)
    .group(pmGroup)

    .elasticX(true)
    .ordinalColors(["#4CAF50", "#F44336"])

    .label((d) => `${d.key} (${d.value})`)
    .renderTitle(true)
    .title((d) => `${d.key}: ${d.value}`);

  // 8. ticker wise trade capture
  const tickerDim = ndx.dimension((d) => d.ticker);
  const tickerGroup = tickerDim.group().reduceCount();
  // wordCloud chart
  function renderWordCloud(group) {
    const data = group.all().filter((d) => d.value > 0);

    const width = W("#ticker");
    const height = 260;

    const max = d3.max(data, (d) => d.value);
    const sizeScale = d3.scaleLinear().domain([1, max]).range([14, 50]);

    const container = d3.select("#ticker");
    container.selectAll("svg").remove();

    const svg = container
      .append("svg")
      .attr("width", width)
      .attr("height", height);

    let x = 10;
    let y = 40;
    const lineHeight = 55;

    data.forEach((d) => {
      const text = svg
        .append("text")
        .style("font-size", sizeScale(d.value) + "px")
        .style("fill", d3.schemeCategory10[Math.floor(Math.random() * 10)])
        .style("cursor", "pointer")
        .text(d.key)
        .on("click", () => {
          if (
            tickerDim.hasCurrentFilter() &&
            tickerDim.currentFilter() === d.key
          ) {
            tickerDim.filter(null);
          } else {
            tickerDim.filter(d.key);
          }
          dc.redrawAll();
        });

      text.append("title").text(`${d.key}: ${d.value}`);

      const box = text.node().getBBox();

      if (x + box.width > width - 10) {
        x = 10;
        y += lineHeight;
      }

      text.attr("x", x).attr("y", y);

      x += box.width + 12;
    });
  }

  // 9. Data Table
  // const tableDim = ndx.dimension((d) => d.trade_date);

  // const tcTable = dc.dataTable("#data-table");

  // tcTable
  //   .dimension(tableDim)
  //   .section((d) => d3.timeFormat("%Y-%m-%d")(d.trade_date))
  //   .size(10)
  //   .columns([
  //     "isin",
  //     "cusip",
  //     // (d) => d.isin,
  //     // (d) => d.cusip,
  //     // (d) => d.account_number,
  //     // (d) => d.executing_broker,
  //     // (d) => d.settlement_date,
  //     // (d) => d.price,
  //     // (d) => d.quantity,
  //     // (d) => d.comm_amount,
  //     // (d) => d.net_amount,
  //   ])
  //   .sortBy((d) => d.settlement_date)
  //   .on("renderlet", function (table) {
  //     table.selectAll(".dc-table-group").classed("info", true);
  //   });

  dc.renderAll();
  renderWordCloud(tickerGroup);

  dc.chartRegistry.list().forEach((chart) => {
    chart.on("filtered", () => {
      renderWordCloud(tickerGroup);
    });
  });
  attachReset(sideRow, "#side-reset");
  attachReset(optionRow, "#option-reset");
  attachReset(currencyRow, "#currency-reset");
  attachReset(recordTypeRow, "#record-type-reset");
  attachReset(pbMapRow, "#pb-map-reset");
  attachReset(pmRow, "#pm-reset");
});
</script>

<template>
  <div class="p-3">
    <h2 class="text-lg font-semibold mb-2">
      Dashboard <span class="ml-4 text-sm">Trade Date: {{ tradeDate }}</span>
    </h2>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div class="bg-white shadow rounded p-2 border-2 border-black">
        <h3 class="text-sm font-semibold mb-1">Asset Wise</h3>
        <div id="asset-type-wise"></div>
      </div>

      <div class="bg-white shadow rounded p-2 border-2 border-black">
        <h3 class="text-sm font-semibold mb-1">
          Side Wise
          <a id="side-reset" class="text-xs text-blue-600 invisible">reset</a>
        </h3>
        <div id="side-type-wise"></div>
      </div>

      <div class="bg-white shadow rounded p-2 border-2 border-black">
        <h3 class="text-sm font-semibold mb-1">
          Option Wise
          <a id="option-reset" class="text-xs text-blue-600 invisible">reset</a>
        </h3>
        <div id="option-type-wise"></div>
      </div>

      <div class="bg-white shadow rounded p-2 border-2 border-black">
        <h3 class="text-sm font-semibold mb-1">
          Currency Wise
          <a id="currency-reset" class="text-xs text-blue-600 invisible"
            >reset</a
          >
        </h3>
        <div id="currency-type-wise"></div>
      </div>

      <div class="bg-white shadow rounded p-2 border-2 border-black">
        <h3 class="text-sm font-semibold mb-1">
          Record Type Wise
          <a id="record-type-reset" class="text-xs text-blue-600 invisible"
            >reset</a
          >
        </h3>
        <div id="record-type-wise"></div>
      </div>

      <div class="bg-white shadow rounded p-2 border-2 border-black">
        <h3 class="text-sm font-semibold mb-1">
          PB Map Wise
          <a id="pb-map-reset" class="text-xs text-blue-600 invisible">reset</a>
        </h3>
        <div id="pb-map-wise"></div>
      </div>

      <div
        class="bg-white shadow rounded p-2 border-2 border-black lg:col-span-2"
      >
        <h3 class="text-sm font-semibold mb-1">
          PM Wise
          <a id="pm-reset" class="text-xs text-blue-600 invisible">reset</a>
        </h3>
        <div id="pm-wise"></div>
      </div>

      <div class="bg-white shadow rounded p-2 border-2 border-black">
        <h3 class="text-sm font-semibold mb-1">Ticker Wise</h3>
        <div id="ticker"></div>
      </div>

      <div
        class="bg-white shadow rounded p-2 border-2 border-black col-span-1 md:col-span-2 lg:col-span-3"
      >
        <h3 class="text-sm font-semibold mb-1">Data Table</h3>
        <div id="data-table"></div>
      </div>
    </div>
  </div>
</template>
