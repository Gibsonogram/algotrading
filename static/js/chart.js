/* 
I want to make this js file for charting with the js library 'lightweight-charts' 

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
  upColor: 'rgba(0, 240, 0, 0.7)',
  downColor: '#ee0000',
  borderDownColor: 'rgba(240, 0, 0, 1)',
  borderUpColor: 'rgba(0, 240, 0, 1)',
  wickDownColor: 'rgba(240, 0, 0, 1)',
  wickUpColor: 'rgba(0, 240, 0, 1)',
});

var coin;


// this is how we get the older history data, stored at this url
// importantly, it fetches whatever is at that url, so we need not change anything here
// we need only consider what is at that url
// so we store a coin name at the url and use this as a variable to use for the live data
fetch('http://127.0.0.1:5000/history')
	.then((r) => r.json())
	.then((response) => { 
		coin = response.shift();
		coin = str(coin.toLowerCase());

		console.log(response);
		candleSeries.setData(response);
	})



// this is a comment
// this is how we get the live data
// this however, needs to change

var binanceSocket = new WebSocket(`wss://stream.binance.com:9443/ws/${coin}usdt@kline_15m`);

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

