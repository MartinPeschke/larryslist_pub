define(["tools/ajax"], function(ajax){
    var
    Address = ajax.Model.extend({

    })
    , Addresses = ajax.Collection.extend({
        model: Address
    })
    , Profile = ajax.Model.extend({
        initialize:function(opts){
            this.register({"Address" : new Addresses()});
        }
        , getName: function(){
            return this.get("initials");
        }
        , getFullName: function(){
            return this.get("firstName") +' '+ this.get("lastName");
        }
        , getAddress: function(){
            var a = this.get("Address");
            if(_.isEmpty(a))
                return ' ';
            else {
                a = a.first();
                if(a && a.get("City") && a.get("Country")){
                    return a.get("City").name + ", " + a.get("Country").name;
                } else {
                    return '';
                }
            }
        }
        , getLastUpdated : function(){
            var d = this.get("updatedDate");
            return hnc.zeroFill((d.getUTCMonth()+1), 2) +'/' + d.getFullYear();
        }
        , getPicture: function(){
            var path = this.get("picture");
            return path?hnc.resUrl(path):"/web/static/img/nopic-83px.png";
        }
        , getRank: function(){
            return this.get("ranking")
        }
        , getPoints: function(){
            return this.get("points")
        }
        , getContactCSS: function(){
            return this.get("isContactable")?"has-prop":"has-not";
        }
        , getCollectionCSS: function(){
            return this.get("hasCollection")?"has-prop":"has-not";
        }
        , parseLocal: function(obj){
            obj.updatedDate = hnc.parseDate(obj.updated);
            return obj;
        }
    });
    return Profile;
});