$(document).ready(function() {
    $.get( location.protocol + "/run_ideagen", function(results) {
        var html = "";
        results.forEach(function(e) {
            html += e + "<br/>";
        });
        $("#content").append(html);
    });
});
