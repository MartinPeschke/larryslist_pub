define(["tools/ajax", "models/cart", "models/user", "models/collector"
    , "views/colitem", "text!templates/searchresult_mini.html"]
    , function(ajax, cart, user, Collector, colItem, miniItem){

    var
    templ = _.template(miniItem)
    , View = Backbone.View.extend({
        initialize: function(opts){
            this.$results = this.$el.find(".search-results-body");
            this.results = new colItem.SearchResults();

            this.listenTo(this.results, "add", this.addResult);
            this.listenTo(this.results, "updated", this.updatedResults);
            this.listenTo(cart, "added", this.cartOut);
            this.listenTo(cart, "removed", this.cartIn);
            this.fetch();
        }
        , cartOut: function(model){
            var m = this.results.get(model.id)
            if(m)m.set("selected", false);
        }
        , cartIn: function(model){
            var m = this.results.get(model.id);
            if(m)m.set("selected", true);
        }
        , addResult: function(result){
            var t = this.$results.children(".sortable").eq(this.results.indexOf(result))
                , v = colItem.getView(result, templ);
            if(t.length){
                t.before(v.$el);
            } else {
                this.$results.append(v.$el);
            }
        }
        , updatedResults: function(){
            var empty = this.results.length==0;
            this.$results[empty?'addClass':'removeClass']("is-empty");
        }
        , fetch: function(){
            var view = this;
            this.$results.addClass("loading");
            ajax.submitPrefixed({
                url: '/web/search/recommended'
                , data: {'userToken': user.get("token")}
                , success: function(resp, status, xhr){
                    var results = hnc.getRecursive(resp, "Collectors.Collector", []).slice(0,20);
                    _.each(results, function(obj){
                        cart.prepResult(user.prepResult(obj));
                    });
                    view.results.addOrUpdate(results, {'preserve':false});
                }
                , complete: function(){
                    view.$results.removeClass("loading");
                }
            });
        }
    });
    return View;
});
