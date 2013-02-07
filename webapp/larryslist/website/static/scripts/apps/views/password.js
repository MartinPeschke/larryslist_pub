define(["tools/hash", "tools/ajax", "text!ajax/templates/password.html"], function(hashlib, ajax, template){
    var View = Backbone.View.extend({
        tagName : "div"
        , className : "password-forgot-modal"
        , initialize:function(opts){
            this.$el.attr("id", "password-forgot-"+hashlib.UUID());
            $("body").append(this.$el);
        }
        , render: function(){
            var view = this;
            this.$el.find(".form-validated").off();
            this.$el.html(template);
            ajax.ifyForm({root:this.$el, success: function(resp, status, xhr){
                view.$(".modal").modal("hide");
            }
            , error: function(resp, status, xhr){
                if(resp.values && resp.values.isResend){
                    view.$(".resend-button").fadeIn();
                    view.$(".btn-primary").fadeOut();
                }
            }
            });
            this.$(".modal").modal("show");
        }
    })
    , view, init = function(opts){
        if(!view){
            view = new View(opts);
        }
        return view;
    };
    return {init:init, View:View};
});
