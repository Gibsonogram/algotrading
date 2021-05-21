/* I want to make this js file for charting with the js library 'lightweight-charts' 
Also this is quite exciting, I'm coding in jaascript. I guess this is how you do multiline comments in js.

*/

var chart = LightweightCharts.createChart(document.getElementById('chart'), {
	width: 600,
  height: 300,
	layout: {
		backgroundColor: '#000000',
		textColor: 'rgba(255, 255, 255, 0.9)',
	},
	grid: {
		vertLines: {
			color: 'rgba(197, 203, 206, 0.5)',
		},
		horzLines: {
			color: 'rgba(197, 203, 206, 0.5)',
		},
	},
	crosshair: {
		mode: LightweightCharts.CrosshairMode.Normal,
	},
	rightPriceScale: {
		borderColor: 'rgba(197, 203, 206, 0.8)',
	},
	timeScale: {
		borderColor: 'rgba(197, 203, 206, 0.8)',
	},
});

var candleSeries = chart.addCandlestickSeries({
  upColor: 'rgba(0, 255, 0, 0.7)',
  downColor: '#ee0000',
  borderDownColor: 'rgba(255, 0, 0, 1)',
  borderUpColor: 'rgba(0, 255, 0, 1)',
  wickDownColor: 'rgba(255, 0, 0, 1)',
  wickUpColor: 'rgba(0, 255, 0, 1)',
});

fetch('http://127.0.0.1:5000/history')
	.then((r) => r.json())
	.then((response) => { 
		console.log(response)

		candleSeries.setData(response);
	})

var binanceSocket = new WebSocket('wss://stream.binance.com:9443/ws/btcusdt@kline_15m');

binanceSocket.onmessage = function (event) {
	console.log(event.data);

	var message = JSON.parse(event.data);

	console.log(message.k)
	var candlestick = message.k;

	candleSeries.update({
		time: candlestick.t / 1000,
		open: candlestick.o,
		high: candlestick.h,
		low: candlestick.l,
		close: candlestick.c
	});




}

