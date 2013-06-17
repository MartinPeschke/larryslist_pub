define(["tools/ajax"], function(ajax){
    var View = Backbone.View.extend({
        tagName:"div"
        , className:"signup-modal"
        , initialize:function(opts){
            var fbt = $("#signup-modal-fb");
            if(fbt.length == 0) {
                window.app_router.navigate("",true);
                return;
            }
            this.templates = {
                'facebook': {templ: _.template(fbt.html())}
                , email: {templ:_.template($("#signup-modal-email").html()), onLoad: function($el){
                    ajax.ifyForm({form:$el});
                }}
            };
            this.$el.appendTo("body");
        }
        , render: function(templ){
            var option = this.templates[templ];
            if(_.isEmpty(option))return;
            this.$el.find(".modal")
                    .off()
                    .modal("hide");

            this.$el.html(option.templ())
                    .find(".modal").modal("show")
                    .on({hide: function(){window.app_router.navigate("",true);}});

            option.onLoad&&option.onLoad(this.$el);

        }
    }), view, init = function(opts){
        if(_.isEmpty(view)) view = new View(opts);
        return view;
    };
    return {init:init, View: View}
});
