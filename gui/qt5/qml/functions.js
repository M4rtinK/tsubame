//.pragma library


var foo = "bar"

function formatDistance(d, scale) {
    d = d/scale
    if (! d) {
        return "0"
    }

    //TODO: imperial unit handling
    if (1) {
        if (d >= 1000) {
            return Math.round(d / 1000.0) + " km"
        } else if (d >= 100) {
            return Math.round(d) + " m"
        } else {
            return d.toFixed(1) + " m"
        }
    }
}

function formatBearing(b) {
    return Math.round(b) + "°"
}

function formatCoordinate(lat, lon, c) {
    return getLat(lat, c) + " " + getLon(lon, c)
}

function getDM(l) {
    var out = Array(3);
    out[0] = (l > 0) ? 1 : -1
    l = out[0] * l
    out[1] = ("00" + Math.floor(l)).substr(-3, 3)
    out[2] = ("00" + ((l - Math.floor(l)) * 60).toFixed(3)).substr(-6, 6)
    return out
}

function getValueFromDM(sign, deg, min) {
    return sign*(deg + (min/60))
}

function getBearingTo(lat, lon, tlat, tlon) {
    var lat1 = lat * (Math.PI/180.0);
    var lat2 = tlat * (Math.PI/180.0);

    var dlon = (tlon - lon) * (Math.PI/180.0);
    var y = Math.sin(dlon) * Math.cos(lat2);
    var x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dlon);
    return (360 + (Math.atan2(y, x)) * (180.0/Math.PI)) % 360;
}

function getDistanceTo(lat, lon, tlat, tlon) {
    var dlat = Math.pow(Math.sin((tlat-lat) * (Math.PI/180.0) / 2), 2)
    var dlon = Math.pow(Math.sin((tlon-lon) * (Math.PI/180.0) / 2), 2)
    var a = dlat + Math.cos(lat * (Math.PI/180.0)) * Math.cos(tlat * (Math.PI/180.0)) * dlon;
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return 6371000.0 * c;
}

function p2pDistance(point1, point2) {
   var lat1 = point1.latitude
   var lon1 = point1.longitude
   var lat2 = point2.latitude
   var lon2 = point2.longitude
   return getDistanceTo(lat1, lon1, lat2, lon2)
}

function p2pDistanceString(point1, point2) {
   var lat1 = point1.latitude
   var lon1 = point1.longitude
   var lat2 = point2.latitude
   var lon2 = point2.longitude
   return formatDistance(getDistanceTo(lat1, lon1, lat2, lon2), 1)
}

function makeUsernamesClickable(inputString) {
    // make just Twitter usernames and hashtags clickable
    return inputString.replace(/(@\w+)/g,'<a href="$&">$&</a>')
}

function makeTextClickable(inputString, linksClickable) {
    if (linksClickable) {
        // make Twitter related things & URLs clickable in a piece of text
        return inputString.replace(/(@\w+)|(#\S+)\s|(http\S+)/g,'<a href="$&">$&</a>')
    } else {
        // make just Twitter usernames and hashtags clickable
        return inputString.replace(/(@\w+)|(#\w+)/g,'<a href="$&">$&</a>')
    }
}

String.prototype.trunc =
     function(n,useWordBoundary){
         var toLong = this.length>n,
             s_ = toLong ? this.substr(0,n-1) : this;
         s_ = useWordBoundary && toLong ? s_.substr(0,s_.lastIndexOf(' ')) : s_;
         return  toLong ? s_ +'...' : s_;
      };
