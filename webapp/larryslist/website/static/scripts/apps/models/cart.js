define(["tools/ajax", "models/collector", "models/user"], function(ajax, Collector, user){
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
            if(!this.contains(collector) && !user.ownsProfile(collector)){
                this.get("Collectors").add(collector);
                collector.trigger("cart:added");
            }
        }
        , addProfiles: function(collectors){
            this.stopListening(this, 'Collectors:add', this.persist);
            this.stopListening(this, 'Collectors:remove', this.persist);
            collectors.each(this.addProfile, this);
            this.listenTo(this, 'Collectors:add', this.persist);
            this.listenTo(this, 'Collectors:remove', this.persist);
            this.persist();
        }
        , removeProfile: function(collector){
            this.get("Collectors").remove(collector.id);
            collector.trigger("cart:removed");
        }
        , removeProfiles: function(collectors){
            this.stopListening(this, 'Collectors:add', this.persist);
            this.stopListening(this, 'Collectors:remove', this.persist);
            collectors.each(this.removeProfile, this);
            this.listenTo(this, 'Collectors:add', this.persist);
            this.listenTo(this, 'Collectors:remove', this.persist);
            this.persist();
        }
        , getProfile: function(collector){
            return this.get("Collectors").get(collector.id) || collector;
        }
        , parseResults: function(objs){
            var cart = this.get("Collectors");
            if(!cart.length)return objs;
            var result = [];
            _.each(objs, function(obj){
                result.push(cart.get(obj.id) || obj);
            });
            return result;
        }
        , prepResult: function(obj){
            var o = cart.get(obj.id);
            if(o) { o.setRecursive(obj); return o; }
            else return obj;
        }
        , contains: function(collector){
            return !_.isEmpty(this.get("Collectors").get(collector.id))
        }
        , getItems: function(cb, ctxt){
            cb.call(ctxt, this.get("Collectors")||[]);
        }
        , canSpend: function(user, cb, ctxt){
            this.getItems(function(items){
                 cb.call(ctxt, items.length>0 && user.getCredits() >= items.length);
            })
        }
    })

    , cart = new Cart();
    return cart;
});