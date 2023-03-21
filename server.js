// Express initialization
var express = require('express');
var ps = require('python-shell');
const https = require('https');
var app = express();

app.use(express.static(__dirname + '/public'));

app.get('/', function(request, response) {
	response.sendFile(__dirname + '/public/index.html');
});

app.get('/ideagenerator', function(request, response) {
	response.sendFile(__dirname + '/public/ideagen.html');
});

app.get('/ohgod', function(request, response) {
	https.get('https://www.reddit.com/', (res) => {
		var bodyChunks = [];
		res.on('data', function(chunk) {
			bodyChunks.push(chunk);
		}).on('end', function() {
			var body_information = Buffer.concat(bodyChunks).toString();
			console.log(body_information);
			body_information = body_information.replace(/<span/g, "<marquee");
			body_information = body_information.replace(/<\/span>/g, "</marquee>");
			body_information = body_information.replace(/<a/g, "<marquee><a");
			body_information = body_information.replace(/<\/a>/g, "</a></marquee>");
			body_information = body_information.replace(/<p/g, "<marquee");
			body_information = body_information.replace(/<\/p>/g, "</marquee>");
			body_information = body_information.replace(/<h1/g, "<marquee");
			body_information = body_information.replace(/<\/h1>/g, "</marquee>");
			body_information = body_information.replace(/<h2/g, "<marquee");
			body_information = body_information.replace(/<\/h2>/g, "</marquee>");
			body_information = body_information.replace(/<h3/g, "<marquee");
			body_information = body_information.replace(/<\/h3>/g, "</marquee>");
			response.set('Content-Type', 'text/html');
			response.send(body_information);
		});
	});
});

app.get('/bikes', function(request, response) {
	var duration = parseInt(request.query.duration);
	https.get('https://gbfs.bluebikes.com/gbfs/es/station_status.json', (res) => {
		var bodyChunks = [];
		res.on('data', function(chunk) {
			bodyChunks.push(chunk);
		}).on('end', function() {
			var ddd = {status: {stations: []}, information: {stations: []}, duration: 0, time: 0};
			var body_status = JSON.parse(Buffer.concat(bodyChunks));
			body_status.data.stations.forEach(function(e) {
				ddd.status.stations.push({station_id: e.station_id, num_bikes_available: e.num_bikes_available, num_docks_available: e.num_docks_available});
			});
			https.get('https://gbfs.bluebikes.com/gbfs/es/station_information.json', (res) => {
				var bodyChunks = [];
				res.on('data', function(chunk) {
					bodyChunks.push(chunk);
				}).on('end', function() {
					var body_information = JSON.parse(Buffer.concat(bodyChunks));
					body_information.data.stations.forEach(function(e) {
						ddd.information.stations.push({station_id: e.station_id, capacity: e.capacity, lat: e.lat, lon: e.lon});
					});
					ddd.duration = duration * 60;
					ddd.time = Math.floor(new Date().getTime()/1000);
					var options = {
						args: [JSON.stringify(ddd)]
					};
					ps.PythonShell.run('processtest.py', options, function (err, results) {
						return response.send(results);
					});
				});
			});
		});
	});
});

app.get('/run_ideagen', function(request, response) {
    ps.PythonShell.run('ideagen.py', null, function (err, results) {
        if (err) throw err;
        return response.send(results);
    });
});


// Oh joy! http://stackoverflow.com/questions/15693192/heroku-node-js-error-web-process-failed-to-bind-to-port-within-60-seconds-of
app.listen(process.env.PORT || 3000);
