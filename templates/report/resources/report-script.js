$(function () {

  //mock data
   var data = [[1370822400000,1],[1372636800000,2],[1378684800000,3],[1379289600000,5],[1379894400000,8],[1380499200000,13],[1381104000000,21],[1381708800000,34],[1382313600000,55],[1382918400000,89],[1383523200000,144],[1384128000000,233],[1385337600000,160],[1385942400000,188],[1386547200000,199],[1387152000000,201],[1387756800000,221],[1388361600000,240],[1388966400000,201],[1389571200000,231],[1390176000000,1],[1390780800000,1],[1391385600000,1],[1391990400000,1],[1392595200000,1],[1393200000000,1]], //some trends points over time
   reviewList = { //some mock reviews
      total: 3,
      list: [{
        rating: 3.5,
        excerpt: "Montreal's best-known steakhouse.",
        date: "2012-10-11",
      },
      {
        rating: 2,
        excerpt: "Heard so much about this place for all my life, finally went and what a dissapointment. Felt I was eating in a cafeteria. Too bright, no intimacy.",
        date: "2014-03-04",
      },
      {
        rating: 1.5,
        excerpt: "Visited Moishes for a 90th birthday party and all 9 of us left the restaurant disappointed. The food was very good, but overpriced. The ambiance was non-existent. To make a few extra dollars, the restaurant owners crammed way to many people into the restaurant.",
        date: "2014-03-04",
      }]
    },
    
  pageData = { //the actual data structure that the page is expeting to render
    totalReviews : {
      positiveTrend: true,
      headerValue: 63,
      headerPercent: true,
      trendData: data,
    },
    averageStarRating : {
      positiveTrend: false,
      headerValue: 0.5,
      avgStarRating: 3.5,
      trendData: data,
    },
    socialMedia : {
      providers: [ //"411", "bing", "facebook", "foursquare", "google", "n49", "tripadvisor", "yahoo", "yellowpages", "yelp"
        {provider: "411", listing: true},
        {provider: "Bing", listing: true},
        {provider: "Facebook", listing: true},
        {provider: "Foursquare", listing: false},
        {provider: "Google", listing: false},
        {provider: "N49", listing: false},
        {provider: "Tripadvisor", listing: false},
        {provider: "Yahoo", listing: true},
        {provider: "Yellowpages", listing: false},
        {provider: "Yelp", listing: false},
      ],
      headerValue: "0",
      trendData: data,
    },
    starRatingDistribution : {
      positiveTrend: false,
      headerValue: 0.4,
      headerPercent: true,
      trendData: [[0, 3], [1, 5], [2, 8], [3, 11], [4, 5]],
    },
    reviewsRequiringAttention: {
      "tripadvisor" : reviewList,
      "google" : reviewList,
      "yahoo":  reviewList,
    },
  };

  function proccessingSocialMediaData(){
    var providersListed = {},
      totalListed = 0, elem;
    
    for (var i = 0, ii = pageData.socialMedia.providers.length; i < ii; i++){
      elem = pageData.socialMedia.providers[i];
      if(elem.listing){
        providersListed[elem.provider.toLowerCase()] = elem.provider;
        totalListed++;
      }
    }
    pageData.socialMedia.headerValue = totalListed + " / " + pageData.socialMedia.providers.length;
    pageData.socialMedia.providersListed = providersListed;
  }

  //convert the date in a readable string, with format: Month Day Year (removing day of the week)
  function getReadableDateNoWeekDay(date){
    if(date && date != ""){
      return (new Date(date)).toDateString().replace(/\w+ /, "");
    }
    return "";
  }

  //rendering 5 stars (active, half or inactive) inside the given container
  function renderStars(container, ratingValue, starCssClass){
    var container = container.find("."+starCssClass);
    
    for (var i = 1; i <= 5; i++) {
      if (i <= ratingValue) {
        container.append($('<div class="active"></div>'));
      } else if (i <= Math.round(ratingValue)) {
        container.append($('<div class="half"></div>'));
      } else {
        container.append($('<div class="inactive"></div>'));
      }
    }
  }

  
  function getFlotTrendOptions(color){
    return {
      series: {
          color :[color],
        points: {
          show: false,
        },
        lines: {
          fill: true,
          lineWidth: 2,
        },
        shadowSize: 1
      },
      tooltip: true,
    	tooltipOpts: {
        content: function(date, yval){ 
          $('#flotTip').css({"background-color":color});
          return getReadableDateNoWeekDay(date) + ": " + yval;
        },
        shifts: {
          x: -150,
          y: -28
        }
      },
      grid: {
        hoverable: true,
        autoHighlight: false,
        clickable: true,
        borderWidth: 1,
        color: "#646464",
        borderColor: "#c0c0c0",
        minBorderMargin: 20
      },
      legend: {
        show: false
      },
      yaxis: {
        min: 0,
        tickSize: 60,
        tickFormatter: function (v) {
          if (v == 0) {
            return "";
          }
          else {
            return v;
          }
        },
      },
      xaxis: {
        tickColor: "transparent",
        mode: "time",
        timeformat: "%b %0d <br/> %y",
      },
    }
  }

  function getFlotBarOptions(){
    return {
      bars: {
          show: true,
          barWidth: 0.4, 
          align: "center",
          lineWidth: 0, //no borders for the lines
          fill: true,
          fillColor:  "#2492c3"
      },
      xaxis: {
        ticks: function() {
          var ticks = [];

          for (var i = 0;i < 5; i++){
           ticks[i] = [i, (i+1) + "<span></span>"];
          }
          return ticks;
        },
        tickLength: 1, // hide gridlines
        color:  "#2492c3",
      },
      yaxis: {
        tickFormatter: function (v, axis) {
            return "";
        },
      },
      grid: {
        borderWidth: 0,
      }
    };
  }

  function renderTrendChart(containerId, chartTitle, objectData, options){
  /*params ->
    containerId: string (id of the object in the DOM where it's going to be rendered this info)
      chartTitle: string  
      objectData: {
        positiveTrend: true | false ,
        headerValue: number,
        headerPercent: true | false ,
        trendData: array(), //array of data rendered in flot
        avgStarRating: number,
      }
      options:
      {
        //Object with options that will be used by flot to render the chart
      }*/

    var header = $("#" + containerId + " .chart-header");
    header.find(".text p").html(chartTitle);
    
    if(typeof objectData == "undefined"){
      $("#" + containerId + " .flot-placeholder").html("<i>No Data Available.</i>");
      return;
    }

    if(objectData.positiveTrend){
      header.find(".trend").addClass("up");
    }
    else {
      header.find(".trend").addClass("down");
    }
    header.find(".value").html(objectData.headerValue);
    if(objectData.headerPercent){
      header.find(".value").append("<sup>%</sup>");
    }
    

    
    if(objectData.avgStarRating){
      renderStars(header, objectData.avgStarRating, "stars");
    }

    $.plot($("#" + containerId + " .flot-placeholder"), [
      {data: objectData.trendData}
    ],options);

  }

  function renderReviewSections(reviewsRequiringAttention){
    //as we don't know how many reviews, we add them to the page dynamically
    var reviewRowTmpl = '<div class="reviews-requiring-attention-row"> <div class="review-icon"> <div class="thumbnail"> <span class="source-image"><span class="icon"></span></span> </div> <span class="source"></span> </div> <div class="review-data"> <div class="date"></div><div class="review-stars"></div></div><div class="review-text"><blockquote></blockquote></div></div>',
      reviewProviderSetTmpl = '<div class="reviews-requiring-attention" ><div class="provider-header content-row-header">Reviews requiring attention on <span class="provider-name"><span></div><div class="provider-content"></div></div>',
      reviewTotalRowTmpl = '<div class="reviews-requiring-total"><div class="review-elem-total-provider"></div><div class="review-elem-total-number"></div></div>';

    var reviewRow,reviewsByProvider, reviewTotalRow;

    for( var provider in reviewsRequiringAttention){
      reviewsByProvider = $(reviewProviderSetTmpl);
      reviewsByProvider.find(".provider-name").html(provider);
      
      reviewTotalRow = $(reviewTotalRowTmpl);
      reviewTotalRow.find(".review-elem-total-provider").html(provider);
      reviewTotalRow.find(".review-elem-total-number").html(reviewsRequiringAttention[provider].total);

      for(var i = 0, ii = reviewsRequiringAttention[provider].list.length  ; i < ii; i++){
        reviewRow = $(reviewRowTmpl);
        reviewRow.find(".date").html(getReadableDateNoWeekDay(reviewsRequiringAttention[provider].list[i].date));

        reviewRow.find(".source-image").addClass("source-" + provider);
        reviewRow.find(".review-text blockquote").html(reviewsRequiringAttention[provider].list[i].excerpt);
        
        renderStars(reviewRow, reviewsRequiringAttention[provider].list[i].rating, "review-stars");
        reviewsByProvider.find(".provider-content").append(reviewRow);
      }
      
      $("#reviews-requiring-attention-by-provider").append(reviewsByProvider);
      $("#reviews-requiring-attention-totals").append(reviewTotalRow);
    }
  }

  proccessingSocialMediaData();

  renderTrendChart("reviews", "Total reviews", pageData.totalReviews, getFlotTrendOptions("#f5ae30"));
  renderTrendChart("star-rating", "Average star rating", pageData.averageStarRating, getFlotTrendOptions("#e56961"));
  renderTrendChart("social-media", "Social Media Listings", pageData.socialMedia, getFlotTrendOptions("#0000ff"));
  renderTrendChart("bar-chart", "Star rating distribution", pageData.starRatingDistribution, getFlotBarOptions());

  //In the page template, it's being assumed that no provider was listed. Showing in the report 
  //  the providers that actually were found listed.
  for(var elem in pageData.socialMedia.providersListed) {
    $(".icons .thumbnail .source-" + elem + " .icon").removeClass("not-found");
    $(".icons .thumbnail .source-" + elem + " .icon").siblings().remove();
  }
  
  if(pageData.reviewsRequiringAttention && !jQuery.isEmptyObject(pageData.reviewsRequiringAttention)){
    renderReviewSections(pageData.reviewsRequiringAttention);
  }
  else {
    $("#reviews-requiring-attention-by-provider").html("<i>No reviews requiring attention.</i>");
    $("#reviews-requiring-attention-totals").parent(".content-row").hide();
  }

}); 
