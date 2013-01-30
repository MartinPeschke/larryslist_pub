/**
 * Created with PyCharm.
 * User: Martin
 * Date: 24.01.13
 * Time: 14:20
 * To change this template use File | Settings | File Templates.
 */
define(['tools/ajax', "tools/fileupload", "libs/typeahead"], function(ajax, FileUploader, TypeAhead){
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
            var valid_params = {form: this.$el};

            ajax.ifyForm(_.extend(valid_params, opts.validatorOpts));

            this.wrapperSelector = opts.wrapperSelector || '[data-closure="form"], .form-validated';
            this.templateSelector = opts.templateSelector || "[data-sequence], .form-validated";

            this.$el.find(this.wrapperSelector).each(function(idx, elem){
                var required = $(elem).data("required") === true;
                $(elem).find(view.templateSelector).each(function(idx, elem){
                    if(idx>0)$(elem).prepend(view.removeLink);
                });
            });

            this.widgets = [];
            this.$el.find(".typeahead-container").each(_.bind(this.addTypeAhead, this));
            this.$el.find(".dependent-control").each(_.bind(this.addDependent, this));
            this.$el.find(".picture-upload-control").each(_.bind(this.addPictureUpload, this));
        }
        , addDependent: function(idx, elem){
            var $target = $(elem), data = $target.data(), wrapper = $target.closest(this.templateSelector), depSrc = wrapper.find('[name$='+data.dependency+']')
                , f = function(t){
                    var val = new RegExp(t.find("option").filter(":selected").val()||'hide-at-all-costs');
                    if(val.test(data.dependencyValue)){
                        $target.show()
                    } else {
                        $target.hide();
                    }
                };
            depSrc.on("change.dependent-fields", function(e){f($(e.target))});
            f(depSrc);
        }
        , addTypeAhead: function(idx, elem){
            var opts = $(elem).data();
            opts.el = elem;
            TypeAhead.init(opts);
        }
        , addPictureUpload: function(idx, elem){
            var fpl = new FileUploader({el: elem});
            fpl.on("file:uploaded", function(file_path, file){
                var path = hnc.resUrl(file_path);
                $(elem).find(".img-wrap-inner").empty().html('<img src="'+path+'" class="picture"/>');
                $(elem).find(".picture-holder").val(file_path);
            })
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
                new_node.find(".dependent-control").each(_.bind(this.addDependent, this));
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