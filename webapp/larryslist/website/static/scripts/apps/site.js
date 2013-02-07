define(["router"], function (Router) {
    var
    opts = window.__options__
    , VIEW_MAP = {}
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
                "*default": "default"
            }
            , initialize:function(){
                this.on("route:default", function(path){
                    if(opts.default_route)window.app_router.navigate(opts.default_route, true);
                });
            }
        })
    );
});