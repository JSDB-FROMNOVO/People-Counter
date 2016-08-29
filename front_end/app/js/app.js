$(document).ready(function () {
    google.charts.load('current', {
        'packages': ['corechart', 'bar', 'line']
    });
    google.charts.setOnLoadCallback(onionOne);
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
            console.log(jsonResult);
            $('#wifi-select-dest').html("All");
            processData(jsonResult);
        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
//    setTimeout(function () {
//        getInfo();
//    }, 5000);
}

var onionOne = function(){
    $.ajax({
        type: "GET",
        url: "./onion1.json",
        dataType: 'json',
        crossDomain: true,
        data: {},
        success: function (jsonResult) {
            console.log(jsonResult);
            $('#wifi-select-dest').html("Onion 1");
            processData(jsonResult);
        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
};

var onionTwo = function(){
    console.log("22");
    $.ajax({
        type: "GET",
        url: "./onion2.json",
        dataType: 'json',
        crossDomain: true,
        data: {},
        success: function (jsonResult) {
            console.log(jsonResult);
            $('#wifi-select-dest').html("Onion 2");
            processData(jsonResult);
        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
};

var onionAll = function(){
    $.ajax({
        type: "GET",
        url: "./onion1and2.json",
        dataType: 'json',
        crossDomain: true,
        data: {},
        success: function (jsonResult) {
            console.log(jsonResult);
            $('#wifi-select-dest').html("Onion 1 & 2");
            processData(jsonResult);
        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
};

var processData = function (jsonResult){
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
            updateLifeTime(jsonResult['randomized_intervals']);
            updateSignalStrength(jsonResult['sig_str']);
            updateVendorChart(jsonResult['vendor']);
            updateSSIDChart(jsonResult['ssid']);
            $('#loading_screen').hide();
            $('#main_content').show();
};

var updateLifeTime = function (jsonResult) {

        var dataarray = [];
        dataarray.push(['Year', 'Visitations', {
            role: 'style'
        }]);
        $.each(jsonResult, function (key, value) {
            if (key != "None") {
                dataarray.push([key, value, 'stroke-color: #703593; stroke-width: 4; fill-color: #C5A5CF']);
            }
        })
        var data = google.visualization.arrayToDataTable(dataarray);
    
        var view = new google.visualization.DataView(data);
        view.setColumns([0, 1,
                           2]);
    
        var options = {
            width: 800,
            height: 400,
            bar: {
                groupWidth: "95%"
            },
            legend: {
                position: "none"
            },
        };
        var chart = new google.visualization.ColumnChart(document.getElementById("chart_div"));
        chart.draw(view, options);
//    var chartDiv = document.getElementById('chart_div');
//
//    var data = new google.visualization.DataTable();
//    data.addColumn('number', 'Index');
//    data.addColumn('number', 'Fibonacci Number');
//
//    var dataarray = [];
//
//    $.each(jsonResult, function (key, value) {
//        if (key != "None") {
//            data.addRows([parseInt(key), parseInt(value)]);
//        }
//    })
//
//    console.log(dataarray);
//    data.addRows(
//        dataarray);
//
//    var linearOptions = {
//        legend: 'none',
//        pointSize: 5,
//        width: 900,
//        height: 500,
//        hAxis: {
//            gridlines: {
//                count: -1
//            }
//        },
//        vAxis: {
//            ticks: [0, 50, 250, 300]
//        }
//    };
//
//    var mirrorLogOptions = {
//        title: 'Fibonacci Numbers in Mirror Log Scale',
//        legend: 'none',
//        pointSize: 5,
//        width: 900,
//        height: 500,
//        hAxis: {
//            gridlines: {
//                count: -1
//            }
//        },
//        vAxis: {
//            scaleType: 'mirrorLog',
//            ticks: [0, 5, 10]
//        }
//    };
//
//    function drawLinearChart() {
//        var linearChart = new google.visualization.LineChart(chartDiv);
//        linearChart.draw(data, linearOptions);
//    }
//
//    function drawMirrorLogChart() {
//        var mirrorLogChart = new google.visualization.LineChart(chartDiv);
//        mirrorLogChart.draw(data, mirrorLogOptions);
//    }
//
//    drawMirrorLogChart();
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
//    setTimeout(function () {
//        getNumberDevices();
//    }, 3000);
}

var updateSignalStrength = function (jsonResult) {
    var data = new google.visualization.DataTable();
    
//    $('#wifi-poor').html(jsonResult['poor']);
//    $('#wifi-fair').html(jsonResult['fair']);
//    $('#wifi-good').html(jsonResult['good']);
//    $('#wifi-strong').html(jsonResult['strong']);
    
    
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
        'height': 400,
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
//    setTimeout(function () {
//        getSignalStrength();
//    }, 3000);
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
        'height': 400
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
//    setTimeout(function () {
//        getVendorChart();
//    }, 3000);
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
        'height': 400
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
//    setTimeout(function () {
//        getSSIDChart();
//    }, 3000);
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
//    setTimeout(function () {
//        getLifetimeChart();
//    }, 3000);
}