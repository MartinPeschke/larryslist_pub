define(["tools/ajax", "models/collector"], function(ajax, Collector){
    var STORAGE_KEY = 'LS_USER_CART'

    , Collectors = ajax.Collection.extend({
        model:Collector
    })
    , Cart = ajax.Model.extend({
        initialize: function(opts){
            this.register({'Collectors': new Collectors()});

            var data = hnc.options.cart;
            if(data)this.setRecursive(data);
            this.listenTo(this, 'Collectors:add', this.persist);
            this.listenTo(this, 'Collectors:remove', this.persist);
        }
        , persist:function(collector){
            var cart = this;
            ajax.submit({url:"/cart/save", data:this.toJSON(), success: function(){
                cart.trigger.call(cart, "item:changed", collector);
            }});
        }
        , addProfile: function(collector){
            this.get("Collectors").add(collector);
        }
        , removeProfile: function(collector){
            this.get("Collectors").remove(collector.id);
        }
        , contains: function(collector){
            return !_.isEmpty(this.get("Collectors").get(collector.id))
        }
        , getItems: function(cb, ctxt){
            cb.call(ctxt, this.get("Collectors")||[]);
        }
    })

    , cart = new Cart();
    return cart;
});