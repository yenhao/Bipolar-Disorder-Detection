    // Parse the date / time
    var parseDate = d3.time.format("%Y-%m-%d").parse;

    

    // console.log(diagnosed_date);

    if(diagnosed_date.split("/").length == 3){
      diagnosed_date = d3.time.format("%Y/%m/%d").parse(diagnosed_date);
    }else if (diagnosed_date.split("/").length ==2){
      diagnosed_date = d3.time.format("%Y/%m").parse(diagnosed_date);
    }

    console.log("Diagnosed at : " + diagnosed_date);

    var data_total = [];

    
    // var data = [{"date":"2012-03-20","total":3},{"date":"2012-03-21","total":8},{"date":"2012-03-22","total":2},{"date":"2012-03-23","total":10},{"date":"2012-03-24","total":3},{"date":"2012-03-25","total":20},{"date":"2012-03-26","total":12}];
    
    console.log(data);
    console.log(data2);

    data_total.push(data);
    data_total.push(data2);



    var colors = ["steelblue", "orange"];
    var bandPos = [-1, -1];
    var pos;
    var ydomain;
    var xbegin = data[0].date;
    var xdomain = data[data.length -1].date;

    var global_x1 = xbegin;
    var global_x2 = xdomain;

    var y1 = d3.max(data , function(d) { return d.total; });
    var y2 = d3.max(data2 , function(d) { return d.total; });

    if(y1>=y2){
      ydomain = y1;
    }else{
      ydomain = y2;
    }

    var margin = {
      top: 40,
      right: 40,
      bottom: 50,
      left: 60
    }
    var width = 1200 - margin.left - margin.right;
    var height = 450 - margin.top - margin.bottom;
    var zoomArea = {
      x1: xbegin,
      y1: 0,
      x2: xdomain,
      y2: ydomain
    };
    var drag = d3.behavior.drag();

    var svg = d3.select("#graph").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    var x = d3.time.scale()
      .range([0, width]).domain(d3.extent(data, function(d) { return d.date; }));

    var y = d3.scale.linear()
      .range([height, 0]).domain([0, ydomain]);

    var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom")
      // .tickFormat(d3.time.format("%b %Y"))
      .ticks(12);

    var yAxis = d3.svg.axis()
      .scale(y)
      .orient("left");

    var line = d3.svg.line()
      .interpolate("basis")
      .x(function(d) {
        return x(d.date);
      })
      .y(function(d) {
        return y(d.total);
      });

    var band = svg.append("rect")
      .attr("width", 0)
      .attr("height", 0)
      .attr("x", 0)
      .attr("y", 0)
      .attr("class", "band");

    svg.append("g")
      .attr("class", "x axis")
      .call(xAxis)
      .attr("transform", "translate(0," + height + ")");

    svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
     .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -60)
      .attr("x", -200)
      .attr("dy", "0.71em")
      .attr("fill", "#000")
      .text("Count");

    // Diagnozed day
    svg.append("line")
      .attr("class", "diagnosed-line")
      .attr("x1", x(diagnosed_date))
      .attr("x2", x(diagnosed_date))
      .attr("y1", 0)
      .attr("y2", height)
      .attr("stroke", "pink")
      .attr("stroke-width", "5");

    svg.append("clipPath")
      .attr("id", "clip")
      .append("rect")
      .attr("width", width)
      .attr("height", height); 

    //set the labels
    svg.append("text")
      .attr("transform", "translate(" + (width+3) + ")")
      .attr("y",40)
      .attr("x",-120)
      .attr("dy", ".5em")
      .attr("text-anchor", "start")
      .style("fill", "#ff89ba")
      .text("Diagnosed-Day");

    svg.append("text")
      .attr("transform", "translate(" + (width+3) + ")")
      .attr("y",20)
      .attr("x",-100)
      .attr("dy", ".5em")
      .attr("text-anchor", "start")
      .style("fill", "orange")
      .text("Late Tweets");

    svg.append("text")
      .attr("transform", "translate(" + (width+3) + ")")
      .attr("x",-91)
      .attr("dy", ".5em")
      .attr("text-anchor", "start")
      .style("fill", "steelblue")
      .text("Frequence");



    for (idx in data_total) {
      svg.append("path")
        .datum(data_total[idx])
        .attr("class", "line line" + idx)
        .attr("clip-path", "url(#clip)")
        .style("stroke", colors[idx])
        .attr("d", line);
    }

    var zoomOverlay = svg.append("rect")
      .attr("width", width - 10)
      .attr("height", height)
      .attr("class", "zoomOverlay")
      .call(drag);

    var zoomout = svg.append("g");

    zoomout.append("rect")
      .attr("class", "zoomOut")
      .attr("width", 75)
      .attr("height", 40)
      .attr("x", -12)
      .attr("y", height + (margin.bottom - 20))
      .on("click", function() {
        zoomOut();
      });

    zoomout.append("text")
      .attr("class", "zoomOutText")
      .attr("width", 75)
      .attr("height", 30)
      .attr("x", -10)
      .attr("y", height + (margin.bottom - 5))
      .text("Zoom Out");

    zoom();

    drag.on("dragend", function() {
      var pos = d3.mouse(this);
      var x1 = x.invert(bandPos[0]);
      var x2 = x.invert(pos[0]);

      if (x1 < x2) {
        zoomArea.x1 = x1;
        zoomArea.x2 = x2;
      } else {
        zoomArea.x1 = x2;
        zoomArea.x2 = x1;
      }

      var y1 = y.invert(pos[1]);
      var y2 = y.invert(bandPos[1]);

      if (x1 < x2) {
        zoomArea.y1 = y1;
        zoomArea.y2 = y2;
      } else {
        zoomArea.y1 = y2;
        zoomArea.y2 = y1;
      }

      bandPos = [-1, -1];

      d3.select(".band").transition()
        .attr("width", 0)
        .attr("height", 0)
        .attr("x", bandPos[0])
        .attr("y", bandPos[1]);

      zoom();
      redrawDiagnosedline();
      updateViewportFromChart();
    });

    drag.on("drag", function() {

      var pos = d3.mouse(this);

      if (pos[0] < bandPos[0]) {
        d3.select(".band").
        attr("transform", "translate(" + (pos[0]) + "," + bandPos[1] + ")");
      }
      if (pos[1] < bandPos[1]) {
        d3.select(".band").
        attr("transform", "translate(" + (pos[0]) + "," + pos[1] + ")");
      }
      if (pos[1] < bandPos[1] && pos[0] > bandPos[0]) {
        d3.select(".band").
        attr("transform", "translate(" + (bandPos[0]) + "," + pos[1] + ")");
      }

      //set new position of band when user initializes drag
      if (bandPos[0] == -1) {
        bandPos = pos;
        d3.select(".band").attr("transform", "translate(" + bandPos[0] + "," + bandPos[1] + ")");
      }

      d3.select(".band").transition().duration(1)
        .attr("width", Math.abs(bandPos[0] - pos[0]))
        .attr("height", Math.abs(bandPos[1] - pos[1]));
    });

    function redrawDiagnosedline(){
      // To re draw the diagnosed line after zoom
      svg.transition().duration(750).select(".diagnosed-line")
        .attr("x1", x(diagnosed_date))
        .attr("x2", x(diagnosed_date));
    }

    function zoom() {
      //recalculate domains
      if (zoomArea.x1 > zoomArea.x2) {
        x.domain([zoomArea.x2, zoomArea.x1]);
        // to set the global x1, x2 to get time area
        global_x1 = zoomArea.x2;
        global_x2 = zoomArea.x1;
      } else {
        x.domain([zoomArea.x1, zoomArea.x2]);
        global_x1 = zoomArea.x1;
        global_x2 = zoomArea.x2;
      }

      // if (zoomArea.y1 > zoomArea.y2) {
      //   y.domain([zoomArea.y2, zoomArea.y1]);
      // } else {
      //   y.domain([zoomArea.y1, zoomArea.y2]);
      // }

      //update axis and redraw lines
      var t = svg.transition().duration(750);
      t.select(".x.axis").call(xAxis);
      t.select(".y.axis").call(yAxis);

      t.selectAll(".line").attr("d", line);
    }

    var zoomOut = function() {
      x.domain([xbegin, xdomain]);
      y.domain([0, ydomain]);

      var t = svg.transition().duration(250);
      t.select(".x.axis").call(xAxis);
      t.select(".y.axis").call(yAxis);

      t.selectAll(".line").attr("d", line);
      redrawDiagnosedline();
      updateViewportFromChart();
    };

    function viewTweets(){
      var Ymd = d3.time.format("%Y/%m/%d");
      var date_query = new Array();
      console.log(global_x1>global_x2);
      console.log('Retrieve tweets from ' + Ymd(global_x1) + ' to ' + Ymd(global_x2));
      $(".select-label").each(function(){
        date_query.push($(this).text());
        console.log($(this).text());
        });
      $.ajax({
        url: '/getTweets',
        data: { user: "{{ user }}",
                start: Ymd(global_x1),
                end: Ymd(global_x2)
              },
        type: 'POST',
        success: function(response) {
            
            response_array = response.split("!@!@!");
            $(".wordcloud").html(response_array[0]);
            $("#tweets").html(response_array[1]);
            window.location.href='#wordcloud';
        },
        error: function(error) {
            console.log(error);
        }
      });
    }

    // THE LOWER CHART

    // setting up the drawing area
    var navWidth = width,
        navHeight = 150 - margin.top - margin.bottom;

    var navChart = d3.select("#graph").append("svg")
      .classed('navigator', true)
      .attr("width", navWidth + margin.left + margin.right)
      .attr("height", navHeight + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // define the X and Y scales
    var navXScale = d3.time.scale()
            .domain([xbegin, xdomain])
            .range([0, navWidth]),
        navYScale = d3.scale.linear()
            .domain([0, ydomain])
            .range([navHeight, 0]);

    // For the navigation chart, we only want an X axis, so we define and add that now.
    var navXAxis = d3.svg.axis()
        .scale(navXScale)
        .orient('bottom');

    navChart.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + navHeight + ')')
        .call(navXAxis);

    // The only thing left to do is to add the data. We’re going to use a d3.svg.area component, 
    // but we’re also going to add a d3.svg.line component so we can add a little visual punch.
    var navData = d3.svg.area()
        .x(function (d) { return navXScale(d.date); })
        .y0(navHeight)
        .y1(function (d) { return navYScale(d.total); });

    var navLine = d3.svg.line()
        .x(function (d) { return navXScale(d.date); })
        .y(function (d) { return navYScale(d.total); });

    navChart.append('path')
        .attr('class', 'data')
        .attr('d', navData(data));

    navChart.append('path')
        .attr('class', 'line')
        .attr('d', navLine(data));

    navChart.append('path')
        .attr('class', 'data')
        .attr('d', navData(data2));

    navChart.append('path')
        .attr('class', 'line')
        .attr('d', navLine(data2));

    // Diagnozed day
    navChart.append("line")
      .attr("class", "diagnosed-line")
      .attr("x1", x(diagnosed_date))
      .attr("x2", x(diagnosed_date))
      .attr("y1", 0)
      .attr("y2", navHeight)
      .attr("stroke", "pink")
      .attr("stroke-width", "5");

    // THE VIEWPORT ON THE LOWER CHART

    // For this chart, we’re going to use the brush event to update the xScale.domain and redraw the main chart.
    var viewport = d3.svg.brush()
        .x(navXScale)
        .on("brush", function () {
            x.domain(viewport.empty() ? navXScale.domain() : viewport.extent());
            redrawChart();
            redrawDiagnosedline();
        });

    // The method we’re calling there, redrawChart(), simply calls the data series and the X axis in order to redraw them following a change in the X scale. 
    // I’ve separated it out into its own method because we’re going to need to call it from a few other places once we add panning and zooming.
    function redrawChart() {
      //update axis and redraw lines
      var t = svg.transition().duration(750);
      t.select(".x.axis").call(xAxis);

      t.selectAll(".line").attr("d", line);
    }
    // Then we add the viewport component to the navigation chart.
    navChart.append("g")
      .attr("class", "viewport")
      .call(viewport)
      .selectAll("rect")
      .attr("height", navHeight);


    function updateViewportFromChart() {
      if ((x.domain()[0] <= xbegin) && (x.domain()[1] >= xdomain)) {
            viewport.clear();
        }
        else {
            viewport.extent(x.domain());
        }
        navChart.select('.viewport').call(viewport);
    }