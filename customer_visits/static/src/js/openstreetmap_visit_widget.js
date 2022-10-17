odoo.define("customer_visits.openstreetmap_visit_widget", function (require) {
  "use strict";
  var fieldRegistry = require("web.field_registry");
  var abstractField = require("web.AbstractField");

  var openstreetmap_visits = abstractField.extend({
    template: "openstreetmap_visits",
    start: function () {
      var self = this;
      this._super();
      self._initMap();
    },
    _initMap: function () {
      var self = this
      $(document).ready(function () {
        setTimeout(() => {
          var lat = self.recordData.latitude;
          var lng = self.recordData.longitude;

          if (!lat && !lng) {
            lat = 33.312805;
            lng = 44.361488;
          }
          
          var mymap = L.map('mapvisit').setView([lat, lng], 13);
          L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution:
            '&copy; <a href="https://smart-bt.net/">Smart Business Technology</a>',
          }).addTo(mymap);

          var edit = self.mode == "edit" ? true : false;
          var marker = L.marker([lat, lng], { draggable: edit }).addTo(mymap);
          
          marker.on("dragend", function (e) {
            var latlng = e.target._latlng;
            self.trigger_up("field_changed", {
              dataPointID: self.dataPointID,
              changes: {
                latitude: latlng.lat,
                longitude: latlng.lng,
              },
              viewType: self.viewType,
            });
          });

          if (edit) {
            var geocode = L.Control.geocoder({
              defaultMarkGeocode: false,
            }).addTo(mymap);

            geocode.on("markgeocode", function (e) {
              var lat = e.geocode.center.lat;
              var lng = e.geocode.center.lng;

              mymap.flyTo([lat, lng]);
              marker.setLatLng(new L.LatLng(lat, lng));
              self.trigger_up("field_changed", {
                dataPointID: self.dataPointID,
                changes: {
                latitude: lat,
                longitude: lng,
                },
                viewType: self.viewType,
              });
            });
          }

          var interval = setInterval(() => {
            if (mymap && mymap._size.x > 0){
              clearInterval(interval);
            } else if (!document.getElementById("mapvisit")) {
              clearInterval(interval);
            }
            window.dispatchEvent(new Event("resize"));
          }, 1000);
        }, 500);

      });
    },
    isSet: function () {
      return true;
    },
  });

  fieldRegistry.add("openstreetmap_visits", openstreetmap_visits);

});
