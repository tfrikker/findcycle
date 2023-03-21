//Determine user's location and process it
var map;
var details;
var markers = [];
/* position of 574 at Tufts */
var default_position = {lat: "42.403150", lon: "-71.113931"};

function geoloc_error(err) {
	console.log(`ERROR(${err.code}): ${err.message}`);
	renderMap(default_position.lat, default_position.lon);
}

function getLocation(){
	//Adapted from: https://www.tutorialspoint.com/html5/geolocation_getcurrentposition.htm
	if (navigator.geolocation){
		console.log("navigator.geolocation is enabled");
		navigator.geolocation.getCurrentPosition(sendLocation, geoloc_error, {timeout:10000});
	} else {
		console.log("navigator.geolocation is disabled");
		renderMap(default_position.lat, default_position.lon);
	}
}

function sendLocation(position) {
    renderMap(position.coords.latitude, position.coords.longitude);
}

//Draw the map and set up markers
function renderMap(latitude, longitude){
	console.log("Map rendered with home position: " + latitude + ", " + longitude);
	me = new google.maps.LatLng(latitude, longitude);
	viewOptions = {
		zoom: 15,
		center: me,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	};

	map = new google.maps.Map(document.getElementById("map_canvas"), viewOptions);
	details = new google.maps.InfoWindow();
	map.panTo(me);

	// Create a marker for the user
	marker = new google.maps.Marker({
		position: me,
		title: "It's you!",
		map: map,
		icon: "person.png"
	});
    google.maps.event.addListener(marker, "click", function() {
		details.setContent("<p>" + marker.title + "</p>");
		details.open(map, marker);
	});
}

function getBikePoints(duration) {
    deleteMarkers();
    $.get( location.protocol + "/bikes", { duration: duration }, function(results) {
        var test = results[0].replace(/'/g, '"');
        var json_fixed = JSON.parse(test);
        json_fixed.points.forEach(function(e) {
            addMarker({
                lat: parseFloat(e.lat),
                lng: parseFloat(e.lon)},
                e.numBikes,
                (duration != 0) ? e.confidence : 1);
        });
    });
}


// Adds a marker to the map and push to the array.
function addMarker(location, numBikes, confidence) {
    if (confidence != 0) {
        let color;
        if (numBikes == 0) {
            color = "red";
        } else if (numBikes < 4) {
            color = "orange";
        } else if (numBikes < 7) {
            color = "yellow";
        } else {
            color = "green";
        }
        let url = "https://maps.google.com/mapfiles/ms/icons/" + color + "-dot.png"
        let opacity = (Math.sqrt(confidence) >= 0.25) ? Math.sqrt(confidence) : 0.25
        var marker = new google.maps.Marker({
            position: location,
            title: "Number of bikes: " + numBikes + " (confidence: " + (confidence*100).toFixed(2) + "%)",
            map: map,
            opacity: opacity,
            icon: {
                url: url
            }
        });
    	google.maps.event.addListener(marker, "click", function() {
    		details.setContent("<p>" + marker.title + "</p>");
    		details.open(map, marker);
    	});
        markers.push(marker);
    }
}

// Sets the map on all markers in the array.
function setMapOnAll(map) {
    for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(map);
    }
}

// Removes the markers from the map, but keeps them in the array.
function clearMarkers() {
    setMapOnAll(null);
}

// Deletes all markers in the array by removing references to them.
function deleteMarkers() {
    clearMarkers();
    markers = [];
}
