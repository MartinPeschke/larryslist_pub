define(["tools/ajax"
    , "models/cart"
    , "models/user"
    , "text!ajax/templates/payment/options.html"
    ], function(ajax, cart, user, templ){
    var
        MODULE_KEY = "PAYMENT_OPTIONS"
        , instance
        , View = Backbone.View.extend({
            template: _.template(templ)
          , initialize: function(opts){
                this.setElement($(this.template({}).trim()).appendTo("body"));
                ajax.ifyForm({form:this.$(".form-validated")});
          }
          , render: function(){
                this.$el.modal("show");

          }
        })
        , init = function(opts){
            if(!instance){
                var opts = opts.pageconfig[MODULE_KEY]||{};
                instance = new View(opts);
            }
            return instance;
        };
    return {init:init, View:View};
});