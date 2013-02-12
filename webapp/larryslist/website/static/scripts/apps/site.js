define(["router"], function (Router) {
    var
    VIEW_MAP = {}
    , opts = hnc.options
    , dodo = function(required, idx, action){
        return function(){
            var args = arguments;
            require(required, function (mod) {
                var view = mod.init(opts);
                if(view)view[action||'render'].apply(view, args);
            });
        }
    };
    Router.initialize(
        Backbone.Router.extend({
            routes: {
                "search": "search"
                , "cart": "cart"
                , "*default": "default"
            }
            , initialize:function(){
                this.on("route:default", function(path){
                    if(opts.default_route)window.app_router.navigate(opts.default_route, true);
                });
                this.on("route:search", dodo(["views/search"], 100));
                this.on("route:cart", dodo(["views/cartpage"], 100));
            }
        })
    );
});