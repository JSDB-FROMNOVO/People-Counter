$(document).ready(function () {
    google.charts.load('current', {
        'packages': ['corechart']
    });
    google.charts.setOnLoadCallback(getInfo);
    //            getNumberDevices();
    //            getSignalStrength();
    //
});

var getInfo = function () {
    $.ajax({
        type: "GET",
        url: "http://142.150.208.226:8101/db/fend/all",
        dataType: 'json',
        crossDomain: true,
        data: {},
        success: function (jsonResult) {

            $("#num-unique-mac").html(jsonResult.total_devices['real_count']);
            width = $('#num-unique-mac').width();
            $('#num-unique-mac').css({
                'height': width + 'px'
            });

            $("#num-invalid-mac").html(jsonResult.total_devices['invalid_count']);
            var width = $('#num-invalid-mac').width();
            $('#num-invalid-mac').css({
                'height': width + 'px'
            });


            $("#num-total-mac").html(jsonResult.total_devices['total_count']);
            var width = $('#num-total-mac').width();
            $('#num-total-mac').css({
                'height': width + 'px'
            });

            updateSignalStrength(jsonResult['sig_str']);
            updateVendorChart(jsonResult['vendor']);
            updateSSIDChart(jsonResult['ssid']);
            $('#loading_screen').hide();
            $('#main_content').show();
        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
    setTimeout(function () {
        getInfo();
    }, 5000);
}
var getNumberDevices = function () {
    //get the number of real MACs, randomized MACs, and total devices
    $.ajax({
        type: "GET",
        url: "http://142.150.208.226:8101/db/test/",
        dataType: 'json',
        crossDomain: true,
        data: {},
        success: function (jsonResult) {

            $("#num-unique-mac").html(jsonResult['real_count']);
            width = $('#num-unique-mac').width();
            $('#num-unique-mac').css({
                'height': width + 'px'
            });

            $("#num-invalid-mac").html(jsonResult['invalid_count']);
            var width = $('#num-invalid-mac').width();
            $('#num-invalid-mac').css({
                'height': width + 'px'
            });


            $("#num-total-mac").html(jsonResult['total_count']);
            var width = $('#num-total-mac').width();
            $('#num-total-mac').css({
                'height': width + 'px'
            });

            $('#loading_screen').hide();
            $('#main_content').show();
        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
    setTimeout(function () {
        getNumberDevices();
    }, 3000);
}

var updateSignalStrength = function (jsonResult) {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Strength');
    data.addColumn('number', '# Devices');
    data.addRows([
					  ['Strong', jsonResult['strong']],
					  ['Good', jsonResult['good']],
					  ['Fair', jsonResult['fair']],
					  ['Poor', jsonResult['poor']]
					]);

    // Set chart options
    var options = {
        'pieHole': 0.4,
        'width': 800,
        'height': 600,
        slices: {
            0: {
                color: 'green'
            },
            1: {
                color: 'lightgreen'
            },
            2: {
                color: 'orange'
            },
            3: {
                color: 'red'
            }
        }
    };

    // Instantiate and draw our chart, passing in some options.
    var sigstr_chart = new google.visualization.PieChart(document.getElementById('sig_str_div'));
    sigstr_chart.draw(data, options);
}

var getSignalStrength = function () {
    //get the number of real MACs, randomized MACs, and total devices
    $.ajax({
        type: "GET",
        url: "http://142.150.208.226:8101/db/test/sig_str",
        dataType: 'json',
        crossDomain: true,
        data: {},
        success: function (jsonResult) {

            // Create the data table.
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'Strength');
            data.addColumn('number', '# Devices');
            data.addRows([
					  ['Strong', jsonResult['strong']],
					  ['Good', jsonResult['good']],
					  ['Fair', jsonResult['fair']],
					  ['Poor', jsonResult['poor']]
					]);

            // Set chart options
            var options = {
                'pieHole': 0.4,
                'width': 800,
                'height': 600,
                slices: {
                    0: {
                        color: 'green'
                    },
                    1: {
                        color: 'lightgreen'
                    },
                    2: {
                        color: 'orange'
                    },
                    3: {
                        color: 'red'
                    }
                }
            };

            // Instantiate and draw our chart, passing in some options.
            var sigstr_chart = new google.visualization.PieChart(document.getElementById('sig_str_div'));
            sigstr_chart.draw(data, options);


            $('#loading_screen').hide();
            $('#main_content').show();
        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
    setTimeout(function () {
        getSignalStrength();
    }, 3000);
}

var updateVendorChart = function (jsonResult) {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Vendor');
    data.addColumn('number', '# Devices');

    $.each(jsonResult, function (key, value) {
        var elem = [key, value]
        data.addRows([elem])
    })

    // Set chart options
    var options = {
        backgroundColor: 'transparent',
        'pieHole': 0.4,
        'width': 800,
        'height': 600
    };

    // Instantiate and draw our chart, passing in some options.
    var vendor_chart = new google.visualization.PieChart(document.getElementById('vendor_chart_div'));
    vendor_chart.draw(data, options);
}

var getVendorChart = function () {
    $.ajax({
        type: "GET",
        url: "http://142.150.208.226:8101/db/test/vendor",
        dataType: 'json',
        crossDomain: true,
        data: {},
        success: function (jsonResult) {
            // Create the data table.
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'Vendor');
            data.addColumn('number', '# Devices');

            $.each(jsonResult, function (key, value) {
                var elem = [key, value]
                data.addRows([elem])
            })

            // Set chart options
            var options = {
                'pieHole': 0.4,
                'width': 800,
                'height': 600
            };

            // Instantiate and draw our chart, passing in some options.
            var vendor_chart = new google.visualization.PieChart(document.getElementById('vendor_chart_div'));
            vendor_chart.draw(data, options);

            $('#loading_screen').hide();
            $('#main_content').show();

        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
    setTimeout(function () {
        getVendorChart();
    }, 3000);
}

var updateSSIDChart = function (jsonResult) {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'SSID');
    data.addColumn('number', '# Devices');

    $.each(jsonResult, function (key, value) {
        if (key != "None") {
            var elem = [key, value]
            data.addRows([elem])
        }
    })

    // Set chart options
    var options = {
        'pieHole': 0.4,
        'width': 800,
        'height': 600
    };

    // Instantiate and draw our chart, passing in some options.
    var ssid_chart = new google.visualization.PieChart(document.getElementById('ssid_chart_div'));
    ssid_chart.draw(data, options);
}

var getSSIDChart = function () {
    $.ajax({
        type: "GET",
        url: "http://142.150.208.226:8101/db/test/ssid",
        dataType: 'json',
        crossDomain: true,
        data: {},
        success: function (jsonResult) {
            // Create the data table.
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'SSID');
            data.addColumn('number', '# Devices');

            $.each(jsonResult, function (key, value) {
                if (key != "None") {
                    var elem = [key, value]
                    data.addRows([elem])
                }
            })

            // Set chart options
            var options = {
                'pieHole': 0.4,
                'width': 800,
                'height': 600
            };

            // Instantiate and draw our chart, passing in some options.
            var ssid_chart = new google.visualization.PieChart(document.getElementById('ssid_chart_div'));
            ssid_chart.draw(data, options);

            $('#loading_screen').hide();
            $('#main_content').show();

        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
    setTimeout(function () {
        getSSIDChart();
    }, 3000);
}

var getLifetimeChart = function () {
    $.ajax({
        type: "GET",
        url: "http://142.150.208.226:8101/db/lifetime",
        dataType: 'json',
        crossDomain: true,
        data: {},
        success: function (jsonResult) {
            // Create the data table.
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'Time (s)');
            data.addColumn('number', 'MACs');
            data.addRows([
					  jsonResult
					]);

            // Set chart options
            var options = {
                title: "Lifetime of Randomized MAC addresses",
                width: 600,
                height: 1000,
                bar: {
                    groupWidth: "95%"
                },
                legend: {
                    position: "none"
                },
            };

            // Instantiate and draw our chart, passing in some options.
            var lifetime_chart = new google.visualization.BarChart(document.getElementById('lifetime_bar_div'));
            lifetime_chart.draw(data, options);

            $('#loading_screen').hide();
            $('#main_content').show();

        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
    setTimeout(function () {
        getLifetimeChart();
    }, 3000);
}