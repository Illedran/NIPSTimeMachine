function drawChart(years) {
  var data = years;
  var labels = _.map(data, getYear);
  var series = _.map(data, getCount);

  new Chartist.Bar('.js-years-chart', {
    labels: labels,
    series: series,
  }, {
    distributeSeries: true
  });
}

function getYear(n) {
  return n.year;
}

function getCount(n) {
  return n.count;
}
