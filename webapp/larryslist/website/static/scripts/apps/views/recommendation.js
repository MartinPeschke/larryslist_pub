define(["tools/ajax", "models/cart", "models/user", "models/collector"
    , "views/colitem", "text!templates/searchresult_mini.html"]
    , function(ajax, cart, user, Collector, colItem, miniItem){

    var
    templ = _.template(miniItem)
    , View = Backbone.View.extend({
        initialize: function(opts){
            this.$results = this.$el.find(".search-results-body");
            this.results = new colItem.SearchResults();
            new colItem.CartFlyout({root: this.$results});

            this.listenTo(this.results, "add", this.addResult);
            this.listenTo(this.results, "updated", this.updatedResults);
            this.listenTo(this.results, "cart:added", this.updatedResults);
            this.listenTo(this.results, "cart:removed", this.updatedResults);
            this.fetch();
        }
        , checkVisible: function(){
            var visCount = 0;
            this.$results.find(".search-results-row").each(function(idx, elem){
                var $el = $(elem);
                if(visCount<3 && !$el.hasClass("selected")){
                    $el.removeClass("hide");
                    visCount+=1;
                } else {
                    $el.addClass("hide");
                }
            });
            return visCount;
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
            var notEmpty = this.checkVisible();
            this.$results.find(".empty")[notEmpty?"addClass":"removeClass"]("hide");
        }
        , fetch: function(){
            var view = this;
            this.$results.addClass("loading");
            ajax.submitPrefixed({
                url: '/web/search/recommended'
                , data: {'userToken': user.get("token")}
                , success: function(resp, status, xhr){
                    var results = hnc.getRecursive(resp, "Collectors.Collector", []);
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
