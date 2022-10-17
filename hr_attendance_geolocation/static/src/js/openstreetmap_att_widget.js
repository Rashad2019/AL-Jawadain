odoo.define("hr_attendance_geolocation.openstreetmap_att_widget", function (require) {
  "use strict";
  var fieldRegistry = require("web.field_registry");
  var abstractField = require("web.AbstractField");

  var openstreetmap_check_in = abstractField.extend({
    template: "openstreetmap_check_in_template",
    start: function () {
      var self = this;
      this._super();
      self._initMap();
    },
    _initMap: function () {
      var self = this
      $(document).ready(function () {
        setTimeout(() => {
          var lat = self.recordData.check_in_latitude;
          var lng = self.recordData.check_in_longitude;

          if (!lat && !lng) {
            lat = 33.312805;
            lng = 44.361488;
          }
          
          var mymap = L.map('mapid').setView([lat, lng], 13);
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
                check_in_latitude: latlng.lat,
                check_in_longitude: latlng.lng,
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
                check_in_latitude: lat,
                check_in_longitude: lng,
                },
                viewType: self.viewType,
              });
            });
          }

          var interval = setInterval(() => {
            if (mymap && mymap._size.x > 0){
              clearInterval(interval);
            } else if (!document.getElementById("mapid")) {
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

  var openstreetmap_check_out = abstractField.extend({
    template: "openstreetmap_check_out_template",
    start: function () {
      var self = this;
      this._super();
      self._initMap2();
    },
    _initMap2: function () {
      var self = this
      $(document).ready(function () {
        setTimeout(() => {
          var lat = self.recordData.check_out_latitude;
          var lng = self.recordData.check_out_longitude;

          if (!lat && !lng) {
            lat = 33.312805;
            lng = 44.361488;
          }

          var mymap = L.map('mapid2').setView([lat, lng], 13);
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
                check_out_latitude: latlng.lat,
                check_out_longitude: latlng.lng,
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
                  check_out_latitude: lat,
                  check_out_longitude: lng,
                },
                viewType: self.viewType,
              });
            });
          }

          var interval = setInterval(() => {
            if (mymap && mymap._size.x > 0){
              clearInterval(interval);
            } else if (!document.getElementById("mapid2")) {
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
  fieldRegistry.add("openstreetmap_check_in", openstreetmap_check_in);

  fieldRegistry.add("openstreetmap_check_out", openstreetmap_check_out);
});
