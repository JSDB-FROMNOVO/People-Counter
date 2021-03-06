$(document).ready(function () {
    google.charts.load('current', {
        'packages': ['corechart', 'bar', 'line']
    });
    google.charts.setOnLoadCallback(onionOne);
    //            getNumberDevices();
    //            getSignalStrength();
    //
});

var getTimeChart = function () {
    $.ajax({
        type: "GET",
        url: "./heatmap.json",
        dataType: 'json',
        crossDomain: true,
        data: {},
        success: function (jsonResult) {
            console.log(jsonResult);
            drawLineColors(jsonResult);
        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
}

var drawLineColors = function(jsonResult) {
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'X');
    data.addColumn('number', 'Onion1');
    data.addColumn('number', 'Onion2');
    data.addColumn('number', 'Middle');
    
    var count = 13;
    var dataarray = [];
    
    $.each(jsonResult['onion1'], function (key, value) {
        //console.log(key);
        if (key != "None") {
            dataarray.push([count, jsonResult['onion1'][key],jsonResult['onion2'][key], jsonResult['onion1and2'][key]]);
            count += 1;
        }
    })
    
    data.addRows(dataarray);

    var options = {
        width: 800,
        height: 400,
        hAxis: {
            title: 'Time (Starting from 10:13)'
        },
        vAxis: {
            title: 'Number of People'
        },
        colors: ['#1abc9c', '#e74c3c', '#f39c12']
    };

    var chart = new google.visualization.LineChart(document.getElementById('time_chart'));
    chart.draw(data, options);
}

var getLifeCycleProbaility = function () {
    $.ajax({
        type: "GET",
        url: "./lcycle_1_probablity.json",
        dataType: 'json',
        crossDomain: true,
        data: {},
        success: function (jsonResult) {
            //console.log(jsonResult);
            getLifeCycleProbailityChart(jsonResult);
        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
}

var getLifeCycleProbailityChart = function(jsonResult) {
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'X');
    data.addColumn('number', 'Probability of number of MAC');
    
    var dataarray = [];
    
    var current_count =0;
    
    $.each(jsonResult, function (key, value) {
        console.log("KEY" + key);
        console.log("value" + value);
        if (key != "None") {
            current_count += parseFloat(value);
            if (current_count >= 1)
                current_count =1 ;
            dataarray.push([parseInt(key), current_count]);
        }
    })
    
    data.addRows(dataarray);

    var options = {
        width: 800,
        height: 400,
        hAxis: {
            title: 'Life Time (min)'
        },
        vAxis: {
            title: 'Probability of Number of MAC'
        },
        colors: ['#9b59b6']
    };

    var chart = new google.visualization.LineChart(document.getElementById('probaility_mac_chart'));
    chart.draw(data, options);
}

var macNumber = function () {
    $.ajax({
        type: "GET",
        url: "./lifecycles_3_count.json",
        dataType: 'json',
        crossDomain: true,
        data: {},
        success: function (jsonResult) {
            //console.log(jsonResult);
            macNumberChart(jsonResult);
        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
}

var macNumberChart = function(jsonResult) {
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'X');
    data.addColumn('number', 'Number of MAC');
    
    var dataarray = [];
    
    $.each(jsonResult, function (key, value) {
        console.log("KEY" + key);
        console.log("value" + value);
        if (key != "None") {
            dataarray.push([parseInt(key), parseInt(value)]);
        }
    })
    
    data.addRows(dataarray);

    var options = {
        width: 800,
        height: 400,
        hAxis: {
            title: 'Life Time (min)'
        },
        vAxis: {
            title: 'Number of MAC'
        },
        colors: ['#e74c3c']
    };

    var chart = new google.visualization.ColumnChart(document.getElementById('num_mac_time_chart'));
    chart.draw(data, options);
}

var probingTime = function () {
    $.ajax({
        type: "GET",
        url: "./probes_2_count.json",
        dataType: 'json',
        crossDomain: true,
        data: {},
        success: function (jsonResult) {
            //console.log(jsonResult);
            probingTimeChart(jsonResult);
        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
}

var probingTimeChart = function(jsonResult) {
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'X');
    data.addColumn('number', 'Number of Probe');
    
    var data2 = new google.visualization.DataTable();
    data2.addColumn('number', 'X');
    data2.addColumn('number', 'Number of Probe');
    
    var data3 = new google.visualization.DataTable();
    data3.addColumn('number', 'X');
    data3.addColumn('number', 'Number of Probe');
    
    var data4 = new google.visualization.DataTable();
    data4.addColumn('number', 'X');
    data4.addColumn('number', 'Number of Probe');
    
    var dataarray1 = [];
    var dataarray2 = [];
    var dataarray3 = [];
    var dataarray4 = [];
    
    $.each(jsonResult, function (key, value) {
        console.log("KEY" + key);
        console.log("value" + value);
        if (key != "None") {
            
            var tempkey = parseFloat(key);
            if(tempkey < 0.002)
            {
                dataarray1.push([parseFloat(key)*60, parseInt(value)]);
            }
            else if(tempkey >= 0.002 && tempkey <= 0.08)
            {
                dataarray2.push([parseFloat(key)*60, parseInt(value)]);
            }
            else if(tempkey > 0.08)
            {
                dataarray3.push([parseFloat(key), parseInt(value)]);
            }
            dataarray4.push([parseFloat(key), parseInt(value)]);
        }
    })
    
    data.addRows(dataarray1);
    data2.addRows(dataarray2);
    data3.addRows(dataarray3);
    data4.addRows(dataarray4);
    
    var options = {
        width: 800,
        height: 400,
        hAxis: {
            title: 'Delta of Probing Time (sec)'
        },
        vAxis: {
            title: 'Number of Probe'
        },
        colors: ['#3498db']
    }; 
    
    var options2 = {
        width: 800,
        height: 400,
        hAxis: {
            title: 'Delta of Probing Time (sec)'
        },
        vAxis: {
            title: 'Number of Probe'
        },
        colors: ['#1abc9c']
    };
    
    var options3 = {
        width: 800,
        height: 400,
        hAxis: {
            title: 'Delta of Probing Time (min)'
        },
        vAxis: {
            title: 'Number of Probe'
        },
        colors: ['#f1c40f']
    };
    
    var options4 = {
        width: 800,
        height: 400,
        hAxis: {
            title: 'Delta of Probing Time (min)'
        },
        vAxis: {
            title: 'Number of Probe'
        },
        colors: ['#f39c12']
    };
    
    var chart = new google.visualization.ColumnChart(document.getElementById('probing_time_chart_1'));
    chart.draw(data, options);
    var chart = new google.visualization.ColumnChart(document.getElementById('probing_time_chart_2'));
    chart.draw(data2, options2);
    var chart = new google.visualization.ColumnChart(document.getElementById('probing_time_chart_3'));
    chart.draw(data3, options3);
    var chart = new google.visualization.ColumnChart(document.getElementById('overall_probing_chart'));
    chart.draw(data4, options4);
}

var lifeTime = function () {
    $.ajax({
        type: "GET",
        url: "./randomized_intervals.json",
        dataType: 'json',
        crossDomain: true,
        data: {},
        success: function (jsonResult) {
            //console.log(jsonResult);
            lifeTimeChart(jsonResult);
        },
        error: function (jqXHR, textStatus) {
            //handle error
            console.log('err');
            console.log(jqXHR);
        }
    });
}

var lifeTimeChart = function(jsonResult) {
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'X');
    data.addColumn('number', 'Number of change in MAC');
    
    var dataarray = [];
    
    $.each(jsonResult['randomized_intervals'], function (key, value) {
        if (key != "None") {
            dataarray.push([parseInt(value)/60, 1]);
        }
    })
    
    data.addRows(dataarray);

    var options = {
        width: 800,
        height: 400,
        hAxis: {
            title: 'Life Time (min)'
        },
        vAxis: {
            title: 'Number of change in MAC'
        },
        colors: ['#f39c12']
    };

    var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
    chart.draw(data, options);
}



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

var onionOne = function () {
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

var onionTwo = function () {
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

var onionAll = function () {
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

var processData = function (jsonResult) {
    getTimeChart();
    getLifeCycleProbaility();
    macNumber();
    probingTime();
    lifeTime();
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
    //updateLifeTime(jsonResult['randomized_intervals']);
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
    var totalstrong = 0;
    var totalgood = 0;
    var totalfair = 0;
    var totalpoor = 0;
    if (jsonResult['onion1'] == undefined) {
        totalstrong = jsonResult['onion2']['strong'];
        totalgood = jsonResult['onion2']['good'];
        totalfair = jsonResult['onion2']['fair'];
        totalpoor = jsonResult['onion2']['poor'];

        $('#onion1-wifi-poor').html(0);
        $('#onion1-wifi-fair').html(0);
        $('#onion1-wifi-good').html(0);
        $('#onion1-wifi-strong').html(0);

        $('#onion2-wifi-poor').html(totalpoor);
        $('#onion2-wifi-fair').html(totalfair);
        $('#onion2-wifi-good').html(totalgood);
        $('#onion2-wifi-strong').html(totalstrong);

    } else if (jsonResult['onion2'] == undefined) {
        totalstrong = jsonResult['onion1']['strong'];
        totalgood = jsonResult['onion1']['good'];
        totalfair = jsonResult['onion1']['fair'];
        totalpoor = jsonResult['onion1']['poor'];

        $('#onion1-wifi-poor').html(totalpoor);
        $('#onion1-wifi-fair').html(totalfair);
        $('#onion1-wifi-good').html(totalgood);
        $('#onion1-wifi-strong').html(totalstrong);

        $('#onion2-wifi-poor').html(0);
        $('#onion2-wifi-fair').html(0);
        $('#onion2-wifi-good').html(0);
        $('#onion2-wifi-strong').html(0);
    } else {
        totalstrong = jsonResult['onion1']['strong'] + jsonResult['onion2']['strong'];
        totalgood = jsonResult['onion1']['good'] + jsonResult['onion2']['good'];
        totalfair = jsonResult['onion1']['fair'] + jsonResult['onion2']['fair'];
        totalpoor = jsonResult['onion1']['poor'] + jsonResult['onion2']['poor'];

        $('#onion1-wifi-poor').html(jsonResult['onion1']['poor']);
        $('#onion1-wifi-fair').html(jsonResult['onion1']['fair']);
        $('#onion1-wifi-good').html(jsonResult['onion1']['good']);
        $('#onion1-wifi-strong').html(jsonResult['onion1']['strong']);

        $('#onion2-wifi-poor').html(jsonResult['onion2']['poor']);
        $('#onion2-wifi-fair').html(jsonResult['onion2']['fair']);
        $('#onion2-wifi-good').html(jsonResult['onion2']['good']);
        $('#onion2-wifi-strong').html(jsonResult['onion2']['strong']);
    }

    data.addColumn('string', 'Strength');
    data.addColumn('number', '# Devices');
    data.addRows([
					  ['Strong', totalstrong],
					  ['Good', totalgood],
					  ['Fair', totalfair],
					  ['Poor', totalpoor]
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


//def process_sig_str(sniff, sig_str_stats):
//    ss = sniff["signal_strength"]
//    if ss >= -35: #5m
//        sig_str_stats["strong"] += 1
//    elif ss < -35 and ss >= -45: #25m
//        sig_str_stats["good"] += 1
//    elif ss < -45 and ss >= -49: #100m
//        sig_str_stats["fair"] += 1
//    else: #200-250m
