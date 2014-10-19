/**
 * Created by pat on 2/13/2014.
 */

(function () {

  var API_KEY_QUERY_STRING = '?api_key=YOUR_API_KEY__CHANGE_ME';

  // Lightweight shim for those users that don't have a console
  if (typeof console === "undefined") {
    console = {};
    console.log = function (msg) {
      return;
    }
  }

  var ViewUtilities = {
    getTemplate: function (template) {
      return $.ajax({
        url: '/static/templates/' + template,
        type: 'GET'
      });
    },
    initializeView: function (v, opts) {
      if (!opts) {
        opts = {};
      }

      var tagName = 'div';
      if (opts.tagName) {
        tagName = opts.tagName;
      } else if (v.tagName) {
        tagName = v.tagName;
      }

      v.$el = $('<' + tagName + '>');
      v.el = v.$el[0];
      $.extend(v, opts);
    },
    closeView: function (v) {
      v.$el.off();
      v.$el.remove();
    },
    /**
     * Locks on to the name attributes of the html elements, and sets its html contents to what's in the data object
     * @param data
     */
    renderData: function (v, data, options) {
      var el = v.$el;
      if (!options){
        options = {};
      }
      if (options.el){
        el = options.el;
      }
      el.find('[name]').each(function () {
        $(this).html(data[$(this).attr('name')]);
      });
    }
  };

  var ApplicationTemplates = {
    listingCollectionItem: null,
    locationView: null,
    runLocationForm: null,
    locationList: null,
    locationItem: null
  };

  var LocationListItemView = function (opts) {
    this.data = opts.data;
    this.tagName = 'tr';
    this.template = ApplicationTemplates.locationItem;
    ViewUtilities.initializeView(this, opts);

    this.onDelete = $.proxy(this.onDelete, this);
    this.locationDeleted = $.proxy(this.locationDeleted, this);
  };

  LocationListItemView.prototype = {
    initialize: function () {
      this.$el.html(this.template);

      this.$el.on('click', '.button.delete', this.onDelete);

      this.renderData(this.data);
      return this;
    },
    onDelete: function () {

      if (confirm('Are you sure you wish to delete this location?')) {
        $.ajax({
          type: 'DELETE',
          url: '/location/' + this.data.id + API_KEY_QUERY_STRING,
          dataType: 'json'
        }).then(this.locationDeleted);
      }
      return false;
    },
    locationDeleted: function () {
      this.$el.trigger('location-deleted', this);
    },
    renderData: function (data) {
      ViewUtilities.renderData(this, data);

      this.$el.find('a.view-location-link').attr('href', '#/location/' + this.data.id);
    },
    close: function () {
      ViewUtilities.closeView(this);
    }
  };

  var LocationListView = function (opts) {
    this.template = ApplicationTemplates.locationList;
    this.views = [];
    this.renderData = $.proxy(this.renderData, this);
    this.closeView = $.proxy(this.closeView, this);

    ViewUtilities.initializeView(this, opts);
  };

  LocationListView.prototype = {
    initialize: function () {
      this.$el.html(this.template);
      this.loadData();
    },
    loadData: function () {
      $.ajax({
        type: 'GET',
        url: '/locations' + API_KEY_QUERY_STRING,
        dataType: 'json'
      }).then(this.renderData);
    },
    renderData: function (data) {
      this.closeViews();
      for (var i = 0 , ii = data.length; i < ii; i++) {
        var v = new LocationListItemView({
          data: data[i]
        }).initialize();

        v.$el.on('location-deleted', this.closeView);

        this.views.push(v);
        this.$el.find('table tbody').append(v.el);
      }
    },
    closeView: function (el, v) {
      var index = this.views.indexOf(v);
      this.views.splice(index, 1)[0].close();
    },
    closeViews: function () {
      for (var i = 0 , ii = this.views.length; i < ii; i++) {
        this.views[i].close();
      }
    },
    close: function () {
      this.closeViews();
    }
  };

  var LocationView = function (opts) {
    this.template = ApplicationTemplates.locationView;
    this.data = opts.data;
    this.listingViews = [];
    this.reviewViews = [];
    ViewUtilities.initializeView(this, opts);

    this.receivedData = $.proxy(this.receivedData, this);
    this.receivedListings = $.proxy(this.receivedListings, this);
    this.receivedReviews = $.proxy(this.receivedReviews, this);
    this.loadData = $.proxy(this.loadData, this);

    this.refreshInterval = null;
  };

  LocationView.prototype = {
    initialize: function () {
      this.$el.html(this.template);
      this.loadData();
      this.renderedListings = {};
      this.renderedReviews = {};

      this.refreshInterval = setInterval(this.loadData, 11000);
    },
    loadData: function () {
      var ctx = this;
      return $.ajax({
        type: 'GET',
        url: '/location/' + ctx.id + API_KEY_QUERY_STRING,
        dataType: 'json'
      }).then(this.receivedData).then(function () {
        return $.ajax({
          type: 'GET',
          url: '/location/' + ctx.id + '/listings' + API_KEY_QUERY_STRING,
          dataType: 'json'
        });
      }).then(this.receivedListings).then(function () {
        return $.ajax({
          type: 'GET',
          url: '/location/' + ctx.id + '/reviews' + API_KEY_QUERY_STRING,
          dataType: 'json'
        });
      }).then(this.receivedReviews);
    },
    receivedData: function (data) {
      this.data = data;
      this.renderData();

      if (data.is_completed && this.refreshInterval) {
        clearInterval(this.refreshInterval);
        this.refreshInterval = null;
      }

      return $.when({locationReceived: true});
    },
    receivedListings: function (listings) {
      this.closeListingViews();

      for (var i = 0 , ii = listings.length; i < ii; i++) {
        var listingId = listings[i].unique_hash
        if (this.renderedListings[listingId]){
          continue;
        }
        this.renderedListings[listingId] = this.renderedListings[listings[i].id] = listings[i];
        var v = new ListingItemView({
          data: listings[i]
        }).initialize();

        this.$el.find('.listing-collection-view-container tbody').append(v.el);
      }

    },
    receivedReviews: function (reviews) {
      this.closeReviewViews();

      for (var i = 0 , ii = reviews.length; i < ii; i++) {
        var reviewId = reviews[i].review_id
        if (this.renderedReviews[reviewId]){
          continue;
        }
        this.renderedReviews[reviewId] = reviews[i];

        var v = new ReviewItemView({
          data: reviews[i]
        }).initialize();

        var $el = this.$el.find('.review-collection-view-container tbody').append(v.el);

        var isVerified = reviews[i].listing && this.renderedListings[reviews[i].listing] && /verified/i.test(this.renderedListings[reviews[i].listing].status)
        if (isVerified) {
          $el.children().last().css({'background-color':'#F1F1F1','color':'#4EAFD5'})
        }
      }
    },
    renderData: function () {
      ViewUtilities.renderData(this, this.data, {
        el: this.$el.find('.location-view-container,.metrics-view-container')
      });

      this.$el.find('a[name=phone]').attr('href', 'callto:' + this.data.phone);
    },
    closeListingViews: function () {
      for (var i = 0 , ii = this.listingViews.length; i < ii; i++) {
        this.listingViews[i].close();
      }
    },
    closeReviewViews: function () {
      for (var i = 0 , ii = this.reviewViews.length; i < ii; i++) {
        this.reviewViews[i].close();
      }
    },
    close: function () {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }
      ViewUtilities.closeView(this);
    }
  };

  var ReviewItemView = function (opts) {
    this.template = ApplicationTemplates.reviewCollectionItem;
    this.tagName = 'tr';
    this.data = opts.data;
    ViewUtilities.initializeView(this, opts);
  };

  ReviewItemView.prototype = {
    initialize: function () {
      this.$el.html(this.template);
      this.renderData();
      return this;
    },
    renderData: function () {
      ViewUtilities.renderData(this, this.data);
      this.$el.find('a.view-review').attr('href', this.data.link);
    },
    close: function () {
      ViewUtilities.closeView(this);
    }
  };

  var ListingItemView = function (opts) {
    this.template = ApplicationTemplates.listingCollectionItem;
    if(/not me/i.test(opts.data.status)){
      opts.data.status ="Potential Competitor";
    }
    this.data = opts.data;
    this.tagName = 'tr';
    ViewUtilities.initializeView(this, opts);
  };

  ListingItemView.prototype = {
    initialize: function () {
      this.$el.html(this.template);
      this.renderData();
      return this;
    },
    renderData: function () {
      ViewUtilities.renderData(this, this.data);

      this.$el.find('a.view-listing').attr('href', this.data.link);
    },
    close: function () {
      ViewUtilities.closeView(this);
    }
  };

  var NewLocationView = function (opts) {
    this.template = ApplicationTemplates.runLocationForm;
    ViewUtilities.initializeView(this, opts);

    this.onSubmit = $.proxy(this.onSubmit, this);
    this.locationSent = $.proxy(this.locationSent, this);
  };

  NewLocationView.prototype = {
    initialize: function () {
      this.$el.html(this.template);
      this.$el.on('submit', 'form', this.onSubmit);

      // Set defaults
      var locationData = {
        name: 'Schwartz\'s',
        address: '3895 Boulevard Saint-Laurent',
        city: 'Montreal',
        province: 'Quebec',
        country: 'Canada',
        postal: 'H2W 1L2',
        phone: '(514) 842-4813'
      };

      var ctx = this;
      for (var key in locationData) {
        ctx.$el.find(':input[name="' + key + '"]').val(locationData[key]);
      }

      return this;
    },
    onSubmit: function () {

      var locationData = {};

      this.$el.find(':input[name]').each(function () {
        locationData[$(this).attr('name')] = $(this).val();
      });

      $.ajax({
        url: '/location' + API_KEY_QUERY_STRING,
        type: 'POST',
        dataType: 'json',
        data: locationData
      }).then(this.locationSent);

      return false;
    },
    locationSent: function (data) {
      window.location.hash = '#/location/' + data.id;
    },
    close: function () {
      ViewUtilities.closeView(this);
    }
  };

  var ApplicationLoader = function (appContainer) {
    this.appContainer = appContainer;
  };

  ApplicationLoader.prototype = {
    load: function () {
      var ctx = this;
      return ViewUtilities.getTemplate('listing-collection-item.html').then(function (data) {
        ApplicationTemplates.listingCollectionItem = data;
        return ViewUtilities.getTemplate('location-view.html');
      }).then(function (data) {
        ApplicationTemplates.locationView = data;
        return ViewUtilities.getTemplate('review-collection-item.html');
      }).then(function (data) {
        ApplicationTemplates.reviewCollectionItem = data;
        return ViewUtilities.getTemplate('run-location-form.html');
      }).then(function (data) {
        ApplicationTemplates.runLocationForm = data;
        return ViewUtilities.getTemplate('location-list.html');
      }).then(function (data) {
        ApplicationTemplates.locationList = data;
        return ViewUtilities.getTemplate('location-item.html');
      }).then(function (data) {
        ApplicationTemplates.locationItem = data;
        return $.when({});
      });
    }
  };

  var ApplicationRouter = function (appContainer) {
    this.appContainer = appContainer;
    this.currentView = null;
    this.routes = {
      'locations': this.listLocations,
      'new-location': this.newLocation,
      'location/(.+)': this.viewLocation
    };
  };

  ApplicationRouter.prototype = {
    initialize: function () {

      this.onHashChange = $.proxy(this.onHashChange, this);
      for (var key in this.routes) {
        this.routes[key] = $.proxy(this.routes[key], this);
      }

      $(window).on('hashchange', this.onHashChange);

      if (!window.location.hash) {
        window.location.hash = '#/locations';
      } else {
        this.onHashChange();
      }

      return this;
    },
    onHashChange: function () {
      var hash = window.location.hash.replace(/^#\/?/, '');

      for (var route in this.routes) {
        var r = new RegExp('^' + route);
        var match = r.exec(hash);
        if (match) {
          var args = match.splice(1);
          this.routes[route].call(this, args);
        }
      }
    },
    showView: function (newView) {
      if (this.currentView) {
        if (!this.currentView.close) {
          console.log('WARN: View does not implement a close function, cannot guarantee a full cleanup', this.currentView);
        } else {
          this.currentView.close();
        }
      }

      this.currentView = newView;
      this.appContainer.empty().append(newView.el);
    },
    listLocations: function () {
      var view = new LocationListView();
      view.initialize();
      this.showView(view);
    },
    viewLocation: function (id) {
      var view = new LocationView({
        id: id
      });
      view.initialize();
      this.showView(view);
    },
    newLocation: function (id) {
      var view = new NewLocationView({

      });
      view.initialize();
      this.showView(view);
    },
    close: function () {
      if (this.currentView) {
        this.currentView.close();
      }
    }
  };


  $(function () {
    // Document is ready , wire up application

    var mainAppContainer = $("#app-container");
    mainAppContainer.find('h3').html('Loading templates ... ');
    new ApplicationLoader(mainAppContainer).load().then(function () {
      mainAppContainer.find('h3').html('Finished loading templates, initializing router');
      var router = new ApplicationRouter(mainAppContainer).initialize();
    });

  });

}());
