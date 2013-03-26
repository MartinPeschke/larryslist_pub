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
                if(a && a.get("Region") && a.get("Country")){
                    return a.get("Region").name + ", " + a.get("Country").name;
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
            return this.get("rank")
        }
        , getCompletion: function(){
            return this.get("completion")
        }
        , parseLocal: function(obj){
            obj.updatedDate = hnc.parseDate(obj.updated);
            obj.rank = obj.ranking;
            obj.completion = obj.completness;
            obj.subscribers = obj.followers;
            return obj;
        }
    });
    return Profile;
});