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
        , getAddress: function(){
            var a = this.get("Address");
            if(_.isEmpty(a))
                return ' ';
            else {
                a = a.first();
                return a.get("Region").name + ", " + a.get("Country").name;
            }
        }
        , getPicture: function(){
            var path = this.get("picture");
            return path?hnc.resUrl(path):"http://www.gravatar.com/avatar/00000000000000000000000000000000?d=mm";
        }
        , parseLocal: function(obj){
            obj.rank = Math.floor(Math.random()*1000);
            obj.completion = Math.floor(Math.random()*100);
            obj.subscribers = Math.floor(Math.random()*1000);
            return obj;
        }
    });
    return Profile;
});