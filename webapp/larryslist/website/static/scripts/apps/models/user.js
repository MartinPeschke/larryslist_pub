define([], function(){
    var UserModel = Backbone.Model.extend({
        isAnon: function(){
            return _.isEmpty(this.get("token"));
        }
        , getCredits: function(){
            return this.get("credit")||0;
        }
    });
    return new UserModel(hnc.options.user);
});