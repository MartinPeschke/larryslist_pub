/**
 * Created with PyCharm.
 * User: Martin
 * Date: 24.01.13
 * Time: 14:20
 * To change this template use File | Settings | File Templates.
 */
define(['tools/ajax', "libs/typeahead"], function(ajax, TypeAhead){
    var View = Backbone.View.extend({
        events: {
            "click .remove-link": "removeRow"
            , "keyup .remove-link": "removeRow"
            , "click .add-more-link" :"addRow"
            , "keyup .add-more-link": "addRow"
        }
        , removeLink: '<a class="remove-link link close">&times;</a>'
        , initialize: function(opts){
            var view = this;
            ajax.ifyForm({form: this.$el});

            this.wrapperSelector = opts.wrapperSelector || '[data-closure="form"]';
            this.templateSelector = opts.templateSelector || "[data-sequence]";

            this.$el.find(this.wrapperSelector).each(function(idx, elem){
                var required = $(elem).data("required") === true;
                $(elem).find(view.templateSelector).each(function(idx, elem){
                    if(!required || idx)
                        $(elem).prepend(view.removeLink);
                });
            });



            this.widgets = [];
            this.$el.find(".typeahead-container").each(_.bind(this.addTypeAhead, this));
        }
        , addTypeAhead: function(idx, elem){
            var opts = $(elem).data();
            opts.el = elem;
            if(opts.apiDependency){
                this.widgets.push(new TypeAhead.ViewWithDependency(opts));
            } else {
                this.widgets.push(new TypeAhead.View(opts));
            }
        }

        , addRow : function(e){
            if((!e.keyCode || e.keyCode == 13)){
                var $target = $(e.target)
                    , templ = $target.closest(this.wrapperSelector).find(this.templateSelector).last()
                    , new_node = templ.clone()
                    , new_position = parseInt(templ.data("sequence"), 10) + 1
                    , inc = function(elem, attr){
                        if(elem.attr(attr))
                            elem.attr(attr, elem.attr(attr).replace(/-[0-9]+\./g, "-"+new_position+"."))
                    };
                new_node.find("input,select,textarea").each(function(index, elem){
                    elem = $(elem);
                    inc(elem, "id");
                    inc(elem, "name");
                    if(!elem.is('[type=checkbox]'))elem.val("");
                });
                new_node.removeAttr("data-sequence").attr("data-sequence", new_position);
                if(!new_node.find(".remove-link").length) new_node.prepend(this.removeLink);
                new_node.find(".numbering").html(new_position+1);
                templ.after(new_node);
                new_node.find(".typeahead-container").each(_.bind(this.addTypeAhead, this));
                new_node.find("[generated]").remove();
                new_node.find(".error").removeClass("error");
                new_node.find(".valid").removeClass("valid");
            }
        }
        , removeRow : function(e){
            if(!e.keyCode|| e.keyCode == 13){
                var $target = $(e.target), $embeddedForm = $target.closest(this.templateSelector)
                    , siblings = $embeddedForm.siblings(this.templateSelector)
                    , idx = function(elem, pos){
                        _.each(['id','name'], function(attr){
                            if(elem.attr(attr))
                                elem.attr(attr, elem.attr(attr).replace(/-[0-9]+\./g, "-"+pos+"."))
                        });
                    };
                $embeddedForm.remove();
                siblings.each(function(i, elem){
                    $(elem).attr('data-sequence', i).find("input,select,textarea").each(function(k, e){
                            idx($(e), i);
                    });
                    $(elem).find(".numbering").html(i+1);
                });

            }
        }
    });
    return View;
});