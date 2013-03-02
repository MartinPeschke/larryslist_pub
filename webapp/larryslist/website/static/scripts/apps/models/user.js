define(["tools/ajax"], function(ajax){
    var

    MinimalCollector = ajax.Model
    , Collectors = ajax.Collection.extend({model:MinimalCollector})
    , UserModel = ajax.Model.extend({
        initialize: function(opts){
            this.register({Collector: new Collectors()});
        }
        , isAnon: function(){
            return _.isEmpty(this.get("token"));
        }
        , getCredits: function(){
            return this.get("credit")||0;
        }
        , ownsProfile: function(collector){
            return !_.isEmpty(this.get("Collector").get(collector.id));
        }
        , getCollectors: function(){
            return this.get("Collector")
        }
    })
    , user = new UserModel();
    user.setRecursive(hnc.options.user);
    return user;
});